from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Season(Base):
    __tablename__ = "seasons"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    competition_id: Mapped[int]
    season_id: Mapped[int]
    expected_matches: Mapped[int]
    source_commit: Mapped[str]


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)


class Match(Base):
    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[str] = mapped_column(ForeignKey("seasons.id"), index=True)
    home_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    home_score: Mapped[int]
    away_score: Mapped[int]
    date: Mapped[str]
    stage: Mapped[str]
    duration: Mapped[float | None]
    periods: Mapped[dict] = mapped_column(JSONB)


class ImportRecord(Base):
    __tablename__ = "imports"
    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), unique=True)
    source_commit: Mapped[str]
    hashes: Mapped[dict] = mapped_column(JSONB)
    lineups: Mapped[list] = mapped_column(JSONB, default=list)
    transform_version: Mapped[str]
    imported_at: Mapped[datetime]


class Event(Base):
    __tablename__ = "events"
    id: Mapped[str] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    index: Mapped[int]
    period: Mapped[int]
    minute: Mapped[int]
    second: Mapped[int]
    kind: Mapped[str]
    player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    x: Mapped[float | None]
    y: Mapped[float | None]
    payload: Mapped[dict] = mapped_column(JSONB)
    __table_args__ = (UniqueConstraint("match_id", "index"), Index("ix_event_match_kind", "match_id", "kind"))


class Appearance(Base):
    __tablename__ = "appearances"
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    role: Mapped[str] = mapped_column(index=True)
    position: Mapped[str]
    minutes: Mapped[float | None]
    uncertainty: Mapped[str | None]
    shots: Mapped[int]
    goals: Mapped[int]
    xg: Mapped[float | None]
    xg_missing: Mapped[int]
    passes: Mapped[int]
    completed: Mapped[int]
    penalties: Mapped[int]
    __table_args__ = (CheckConstraint("minutes IS NULL OR minutes >= 0"),)
