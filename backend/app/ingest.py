"""Local administrator CLI. No ingestion HTTP route."""

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import httpx
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from app.db import ROOT, engine
from app.metrics import TRANSFORM_VERSION, reconstruct
from app.models import Appearance, Event, ImportRecord, Match, Player, Season, Team

COMMIT = "4b73468fc5b0f1950f9f66fada70ad3a4f9327cb"
SOURCE = f"https://raw.githubusercontent.com/hudl/open-data/{COMMIT}/"
CACHE = ROOT / "data/raw"
LOCK = ROOT / "data/source-lock.json"


class Ref(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    name: str


class Named(BaseModel):
    name: str


class ShotAttributes(BaseModel):
    model_config = ConfigDict(extra="allow")
    outcome: Named
    type: Named
    statsbomb_xg: float | None = Field(None, ge=0, le=1)


class PassAttributes(BaseModel):
    model_config = ConfigDict(extra="allow")
    outcome: Named | None = None


class SourceEvent(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(min_length=1)
    index: int = Field(gt=0)
    period: int = Field(ge=1, le=5)
    timestamp: str = Field(pattern=r"^\d\d:\d\d:\d\d\.\d+$")
    minute: int = Field(ge=0)
    second: int = Field(ge=0, le=59)
    type: Ref
    team: Ref
    player: Ref | None = None
    location: list[float] | None = Field(None, min_length=2, max_length=3)
    shot: ShotAttributes | None = None
    pass_attributes: PassAttributes | None = Field(None, alias="pass")

    @model_validator(mode="after")
    def attributes_for_type(self):
        if self.type.name == "Shot" and self.shot is None:
            raise ValueError("Missing shot attributes")
        if self.type.name == "Pass" and self.pass_attributes is None:
            raise ValueError("Missing pass attributes")
        return self


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def cached(path, expected=None, download=False):
    target = CACHE / path
    if not target.exists():
        if not download:
            raise ValueError(f"Missing file: {path}; run download")
        response = httpx.get(SOURCE + path, timeout=60, follow_redirects=True)
        response.raise_for_status()
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_suffix(".tmp")
        temp.write_bytes(response.content)
        temp.replace(target)
    blob = target.read_bytes()
    if expected and digest(blob) != expected:
        raise ValueError(f"Hash mismatch: {path}; cache rejected")
    json.loads(blob)
    return blob


def download():
    old = json.loads(LOCK.read_text()) if LOCK.exists() else None
    if old and old["commit"] != COMMIT:
        raise ValueError("Source change rejected: explicitly create a new manifest")
    listing = "data/matches/43/106.json"
    matches_blob = cached(listing, old["files"].get(listing) if old else None, True)
    matches = json.loads(matches_blob)
    paths = ["data/competitions.json", listing]
    paths += [f"data/{kind}/{m['match_id']}.json" for m in matches for kind in ("events", "lineups")]

    def fetch(path):
        blob = cached(path, old["files"].get(path) if old else None, True)
        return path, digest(blob)

    with ThreadPoolExecutor(max_workers=4) as pool:
        files = dict(pool.map(fetch, paths))
    manifest = {
        "commit": COMMIT,
        "competition_id": 43,
        "season_id": 106,
        "match_ids": sorted(m["match_id"] for m in matches),
        "files": files,
    }
    if old and manifest != old:
        raise ValueError("Manifest differs: explicit refresh required")
    LOCK.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"downloaded_or_verified": len(paths), "matches": len(matches), "commit": COMMIT}))


def import_match(db, meta, events, lineups, hashes, commit):
    # Serializes ingest/rebuild; protects check-then-insert across processes.
    db.execute(text("SELECT pg_advisory_xact_lock(713209)"))
    mid = meta["match_id"]
    for e in events:
        SourceEvent.model_validate(e)
    if len({e["id"] for e in events}) != len(events) or len({e["index"] for e in events}) != len(events):
        raise ValueError("Duplicate event identifiers")
    if len(lineups) != 2 or len(events) < 2:
        raise ValueError("Incomplete lineups/events")
    old = db.scalar(select(ImportRecord).where(ImportRecord.match_id == mid))
    if old:
        if old.hashes != hashes or old.source_commit != commit or old.transform_version != TRANSFORM_VERSION:
            raise ValueError("Existing import differs: rebuild or a new database required")
        return "unchanged"
    season = db.get(Season, "43-106")
    if season and season.source_commit != commit:
        raise ValueError("Incompatible source versions in the same season")
    if not season:
        db.add(
            Season(
                id="43-106",
                name="FIFA World Cup · 2022",
                competition_id=43,
                season_id=106,
                expected_matches=64,
                source_commit=commit,
            )
        )
    for side in ("home", "away"):
        team = meta[f"{side}_team"]
        if not db.get(Team, team[f"{side}_team_id"]):
            db.add(Team(id=team[f"{side}_team_id"], name=team[f"{side}_team_name"]))
    names = {p["player_id"]: p["player_name"] for t in lineups for p in t["lineup"]}
    for e in events:
        if "player" in e:
            names[e["player"]["id"]] = e["player"]["name"]
        for item in e.get("tactics", {}).get("lineup", []):
            names[item["player"]["id"]] = item["player"]["name"]
        if "substitution" in e:
            p = e["substitution"]["replacement"]
            names[p["id"]] = p["name"]
    for pid, name in names.items():
        if not db.get(Player, pid):
            db.add(Player(id=pid, name=name))
    rows, periods, duration = reconstruct(events, lineups)
    db.flush()
    db.add(
        Match(
            id=mid,
            season="43-106",
            home_id=meta["home_team"]["home_team_id"],
            away_id=meta["away_team"]["away_team_id"],
            home_score=meta["home_score"],
            away_score=meta["away_score"],
            date=meta["match_date"],
            stage=meta["competition_stage"]["name"],
            duration=duration,
            periods=periods,
        )
    )
    db.flush()
    db.execute(
        Event.__table__.insert(),
        [
            dict(
                id=e["id"],
                match_id=mid,
                index=e["index"],
                period=e["period"],
                minute=e["minute"],
                second=e["second"],
                kind=e["type"]["name"],
                team_id=e["team"]["id"],
                player_id=e.get("player", {}).get("id"),
                x=e.get("location", [None, None])[0],
                y=e.get("location", [None, None])[1],
                payload=e,
            )
            for e in events
        ],
    )
    db.add_all(Appearance(match_id=mid, **row) for row in rows)
    db.add(
        ImportRecord(
            match_id=mid,
            source_commit=commit,
            hashes=hashes,
            lineups=lineups,
            transform_version=TRANSFORM_VERSION,
            imported_at=datetime.now(UTC),
        )
    )
    return "imported"


def run_import(limit=None):
    lock = json.loads(LOCK.read_text())
    if lock["commit"] != COMMIT:
        raise ValueError("Incompatible manifest commit")
    listing = "data/matches/43/106.json"
    matches = json.loads(cached(listing, lock["files"][listing]))
    # Vertical slice first: final, England-Iran, Iran-Wales (red card).
    priority = {3869685: 0, 3857271: 1}
    matches.sort(key=lambda m: (priority.get(m["match_id"], 2), m["match_id"]))
    results = []
    for m in matches[:limit]:
        mid = m["match_id"]
        try:
            paths = [f"data/{k}/{mid}.json" for k in ("events", "lineups")]
            blobs = [cached(p, lock["files"][p]) for p in paths]
            hashes = {p: lock["files"][p] for p in [listing, *paths]}
            with Session(engine) as db, db.begin():
                status = import_match(db, m, *[json.loads(b) for b in blobs], hashes, lock["commit"])
            results.append({"match_id": mid, "status": status})
        except Exception as exc:
            results.append({"match_id": mid, "status": "rejected", "error": str(exc)})
        print(json.dumps(results[-1], ensure_ascii=False), flush=True)
    (ROOT / "data/import-summary.json").write_text(json.dumps(results, indent=2))
    if any(r["status"] == "rejected" for r in results):
        raise SystemExit(1)


def rebuild():
    with Session(engine) as db, db.begin():
        db.execute(text("SELECT pg_advisory_xact_lock(713209)"))
        db.execute(delete(Appearance))
        for match in db.scalars(select(Match).order_by(Match.id)):
            events = [
                e.payload
                for e in db.scalars(select(Event).where(Event.match_id == match.id).order_by(Event.index))
            ]
            record = db.scalar(select(ImportRecord).where(ImportRecord.match_id == match.id))
            if not record.lineups:
                path = f"data/lineups/{match.id}.json"
                record.lineups = json.loads(cached(path, record.hashes[path]))
            rows, periods, duration = reconstruct(events, record.lineups)
            db.add_all(Appearance(match_id=match.id, **r) for r in rows)
            match.periods, match.duration = periods, duration
        for record in db.scalars(select(ImportRecord)):
            record.transform_version = TRANSFORM_VERSION
    print("Atomic rebuild completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["download", "import", "rebuild"])
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    {"download": download, "import": lambda: run_import(args.limit), "rebuild": rebuild}[args.command]()
