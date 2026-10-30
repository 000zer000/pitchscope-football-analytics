import os
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import services
from app.db import session
from app.models import Appearance, Event, Match

app = FastAPI(title="PitchScope", version="1.0.0", description="Verifiable statistics · StatsBomb Open Data")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_methods=["GET"],
    allow_headers=["Accept"],
)
DB = Annotated[Session, Depends(session)]
Role = Literal["Goalkeeper", "Defender", "Midfielder", "Forward"]
SeasonID = Literal["43-106"]
Sort = Literal["name", "minutes", "shots", "goals", "xg", "passes", "pass_pct", "shots_p90", "xg_p90"]


@app.get("/api/ready")
def ready(db: DB):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(503, "Database unavailable") from None
    return {"status": "ready"}


@app.get("/api/coverage")
def coverage(db: DB):
    return services.coverage(db)


@app.get("/api/players")
def players(
    db: DB,
    season: SeasonID = "43-106",
    q: str = Query("", max_length=100),
    team: int | None = Query(None, gt=0),
    role: Role | None = None,
    min_minutes: int = Query(0, ge=0, le=10000),
    sort: Sort = "minutes",
    desc: bool = True,
    page: int = Query(1, ge=1, le=10000),
    size: int = Query(15, ge=1, le=100),
):
    rows = services.stats(db, season, role, team)
    rows = [p for p in rows if q.casefold() in p["name"].casefold() and (p["minutes"] or 0) >= min_minutes]
    available = [p for p in rows if p[sort] is not None]
    absent = [p for p in rows if p[sort] is None]
    available.sort(key=lambda p: (p[sort], p["id"]), reverse=desc)
    rows = available + absent
    return {"items": rows[(page - 1) * size : page * size], "total": len(rows), "page": page, "size": size}


@app.get("/api/players/{player_id}")
def profile(player_id: int, db: DB, season: SeasonID = "43-106"):
    rows = services.stats(db, season, player=player_id)
    if not rows:
        raise HTTPException(404, "Player not found")
    appearances = db.scalars(
        select(Appearance)
        .where(Appearance.player_id == player_id)
        .join(Match)
        .where(Match.season == season)
        .order_by(Match.date, Match.id)
    ).all()
    return {
        "player": rows[0],
        "matches": [
            dict(
                **services.match_info(db, db.get(Match, a.match_id)),
                minutes=a.minutes,
                role=a.role,
                uncertainty=a.uncertainty,
            )
            for a in appearances
        ],
    }


@app.get("/api/compare")
def compare(
    db: DB,
    left: int = Query(gt=0),
    right: int = Query(gt=0),
    role: Role = "Forward",
    min_minutes: int = Query(180, ge=0, le=10000),
    season: SeasonID = "43-106",
):
    if left == right:
        raise HTTPException(422, "Choose two different players")
    try:
        return services.comparison(db, left, right, role, min_minutes, season)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None


@app.get("/api/report.pdf")
def report(
    db: DB,
    left: int = Query(gt=0),
    right: int = Query(gt=0),
    role: Role = "Forward",
    min_minutes: int = Query(180, ge=0, le=10000),
    season: SeasonID = "43-106",
):
    data = compare(db, left, right, role, min_minutes, season)
    from app.report import render_report

    return Response(
        render_report(data, services.coverage(db)),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="pitchscope-comparison.pdf"'},
    )


@app.get("/api/matches")
def matches(db: DB, season: SeasonID = "43-106"):
    return [
        services.match_info(db, m)
        for m in db.scalars(
            select(Match).where(Match.season == season).order_by(Match.date.desc(), Match.id.desc())
        )
    ]


@app.get("/api/matches/{match_id}/events")
def events(
    match_id: int,
    db: DB,
    team: int | None = Query(None, gt=0),
    player: int | None = Query(None, gt=0),
    kind: Literal["Shot", "Pass", "Substitution", "Bad Behaviour", "Own Goal Against", "all"] | None = "Shot",
    page: int = Query(1, ge=1, le=10000),
    size: int = Query(100, ge=1, le=500),
):
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(404, "Match not found")
    stmt = select(Event).where(Event.match_id == match_id)
    if kind and kind != "all":
        stmt = stmt.where(Event.kind == kind)
    if team:
        stmt = stmt.where(Event.team_id == team)
    if player:
        stmt = stmt.where(Event.player_id == player)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(Event.index).offset((page - 1) * size).limit(size)).all()
    return {
        "match": services.match_info(db, match),
        "summary": services.match_stats(db, match_id),
        "total": total,
        "page": page,
        "size": size,
        "items": [
            {
                "id": e.id,
                "index": e.index,
                "period": e.period,
                "minute": e.minute,
                "second": e.second,
                "kind": e.kind,
                "team_id": e.team_id,
                "player_id": e.player_id,
                "x": e.x,
                "y": e.y,
                "attributes": e.payload,
            }
            for e in rows
        ],
    }
