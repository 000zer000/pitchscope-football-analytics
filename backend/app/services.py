"""One SQL-backed metric contract shared by API and report."""

from datetime import timezone

from sqlalchemy import case, func, select

from app.models import Appearance as A
from app.models import Event, ImportRecord, Match, Player, Season, Team

METRICS = [
    ("appearances", "Appearances", "matches"),
    ("minutes", "Reliable playing time", "min"),
    ("shots", "Shots", "shots"),
    ("goals", "Goals", "goals"),
    ("xg", "StatsBomb xG", "xG"),
    ("passes", "Passes attempted", "passes"),
    ("completed", "Passes completed", "passes"),
    ("pass_pct", "Pass completion", "%"),
    ("shots_p90", "Shots / 90", "shots/90 min"),
    ("goals_p90", "Goals / 90", "goals/90 min"),
    ("xg_p90", "xG / 90", "xG/90 min"),
    ("passes_p90", "Passes / 90", "passes/90 min"),
]
ROLES = ["Goalkeeper", "Defender", "Midfielder", "Forward"]


def stats(db, season="43-106", role=None, team=None, player=None):
    valid = A.minutes.is_not(None)
    cols = [
        Player.id,
        Player.name,
        func.count().label("appearances"),
        func.sum(A.minutes).label("minutes"),
        func.count().filter(A.minutes.is_(None)).label("uncertain_appearances"),
        func.array_agg(func.distinct(Team.name)).label("teams"),
        func.array_agg(func.distinct(A.role)).label("roles"),
    ]
    for key in ["shots", "goals", "xg", "passes", "completed", "penalties", "xg_missing"]:
        cols.append(func.sum(getattr(A, key)).label(key))
        if key in ("shots", "goals", "xg", "passes", "xg_missing"):
            cols.append(func.sum(case((valid, getattr(A, key)), else_=0)).label("reliable_" + key))
    stmt = (
        select(*cols)
        .join(A, A.player_id == Player.id)
        .join(Team, Team.id == A.team_id)
        .join(Match, Match.id == A.match_id)
    )
    stmt = stmt.where(Match.season == season)
    if role:
        stmt = stmt.where(A.role == role)
    if team:
        stmt = stmt.where(A.team_id == team)
    if player:
        stmt = stmt.where(Player.id == player)
    rows = []
    for record in db.execute(stmt.group_by(Player.id)).mappings():
        row = dict(record)
        if row["xg_missing"]:
            row["xg"] = None
        row["pass_pct"] = 100 * row["completed"] / row["passes"] if row["passes"] else None
        for key in ("shots", "goals", "xg", "passes"):
            row[key + "_p90"] = (
                90 * row["reliable_" + key] / row["minutes"]
                if row["minutes"] and not (key == "xg" and row["reliable_xg_missing"])
                else None
            )
        row["rate_note"] = (
            "Rate unavailable: zero/unknown minutes or missing xG"
            if not row["minutes"]
            else (
                "Rates limited to appearances with reliable playing time"
                if row["uncertain_appearances"]
                else None
            )
        )
        rows.append(row)
    return rows


def comparison(db, left, right, role, min_minutes, season="43-106"):
    pool = stats(db, season, role)
    population = [p for p in pool if (p["minutes"] or 0) >= min_minutes]
    by_id = {p["id"]: p for p in pool}
    if left not in by_id or right not in by_id:
        raise ValueError("Choose two players with an appearance in this role group")
    selected = [by_id[left], by_id[right]]
    warnings = []
    if any((p["minutes"] or 0) < min_minutes for p in selected):
        warnings.append("A player is below the reference-group threshold.")
    if any((p["minutes"] or 0) < 450 for p in selected):
        warnings.append("Small sample: at least one player has fewer than 450 reliable minutes.")
    if len(population) < 20:
        warnings.append("Fewer than 20 reference players: percentiles are not shown.")
    for p in selected:
        p["percentiles"] = {}
        if len(population) >= 20 and (p["minutes"] or 0) >= min_minutes:
            for key in ("shots_p90", "xg_p90", "passes_p90"):
                values = [x[key] for x in population if x[key] is not None]
                if p[key] is not None and len(values) >= 20:
                    # Midrank empirical CDF; ties share rank. Higher is volume, not talent.
                    p["percentiles"][key] = (
                        100
                        * (sum(v < p[key] for v in values) + 0.5 * sum(v == p[key] for v in values))
                        / len(values)
                    )
    return {
        "players": selected,
        "population": {"season": season, "role": role, "min_minutes": min_minutes, "count": len(population)},
        "warnings": warnings,
        "metrics": [{"key": key, "label": label, "unit": unit} for key, label, unit in METRICS],
        "source_commit": db.get(Season, season).source_commit,
    }


def match_info(db, m):
    return {
        "id": m.id,
        "home": db.get(Team, m.home_id).name,
        "away": db.get(Team, m.away_id).name,
        "home_id": m.home_id,
        "away_id": m.away_id,
        "home_score": m.home_score,
        "away_score": m.away_score,
        "date": m.date,
        "stage": m.stage,
        "duration": m.duration,
        "periods": m.periods,
    }


def coverage(db):
    season = db.get(Season, "43-106")
    if not season:
        return {
            "seasons": [],
            "imported_matches": 0,
            "expected_matches": 64,
            "teams": [],
            "events": 0,
            "players": 0,
        }
    imports = db.scalars(select(ImportRecord).order_by(ImportRecord.match_id)).all()
    matches = db.scalars(select(Match).order_by(Match.date, Match.id)).all()
    return {
        "seasons": [{"id": season.id, "name": season.name}],
        "imported_matches": len(matches),
        "expected_matches": season.expected_matches,
        "complete": len(matches) == season.expected_matches,
        "source_commit": season.source_commit,
        "synthetic": season.source_commit == "synthetic-test-only",
        "events": db.scalar(select(func.count()).select_from(Event)),
        "players": db.scalar(select(func.count(func.distinct(A.player_id)))),
        "uncertain_appearances": db.scalar(select(func.count()).select_from(A).where(A.minutes.is_(None))),
        "teams": [{"id": t.id, "name": t.name} for t in db.scalars(select(Team).order_by(Team.name))],
        "imports": [
            {
                "match_id": r.match_id,
                "imported_at": r.imported_at.replace(tzinfo=timezone.utc).isoformat(),
                "transform_version": r.transform_version,
                "hashes": r.hashes,
            }
            for r in imports
        ],
        "matches": [match_info(db, m) for m in matches],
    }


def match_stats(db, match_id):
    rows = db.execute(
        select(
            A.team_id,
            func.sum(A.shots).label("shots"),
            func.sum(A.xg).label("xg"),
            func.sum(A.xg_missing).label("missing"),
        )
        .where(A.match_id == match_id)
        .group_by(A.team_id)
    ).mappings()
    return [
        {
            "team_id": r["team_id"],
            "team": db.get(Team, r["team_id"]).name,
            "shots": r["shots"],
            "xg": None if r["missing"] else r["xg"],
        }
        for r in rows
    ]
