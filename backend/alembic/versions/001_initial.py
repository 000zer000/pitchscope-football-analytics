"""Initial relational schema; immutable migration snapshot."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "seasons",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("competition_id", sa.Integer(), nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("expected_matches", sa.Integer(), nullable=False),
        sa.Column("source_commit", sa.String(), nullable=False),
    )
    for table in ("teams", "players"):
        op.create_table(
            table,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(), nullable=False),
        )
    op.create_index("ix_players_name", "players", ["name"])
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season", sa.String(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("home_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("away_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=False),
        sa.Column("away_score", sa.Integer(), nullable=False),
        sa.Column("date", sa.String(), nullable=False),
        sa.Column("stage", sa.String(), nullable=False),
        sa.Column("duration", sa.Float()),
        sa.Column("periods", JSONB(), nullable=False),
    )
    op.create_index("ix_matches_season", "matches", ["season"])
    op.create_table(
        "imports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), unique=True, nullable=False),
        sa.Column("source_commit", sa.String(), nullable=False),
        sa.Column("hashes", JSONB(), nullable=False),
        sa.Column("transform_version", sa.String(), nullable=False),
        sa.Column("imported_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False),
        sa.Column("period", sa.Integer(), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("second", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id")),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("x", sa.Float()),
        sa.Column("y", sa.Float()),
        sa.Column("payload", JSONB(), nullable=False),
        sa.UniqueConstraint("match_id", "index"),
    )
    op.create_index("ix_events_match_id", "events", ["match_id"])
    op.create_index("ix_event_match_kind", "events", ["match_id", "kind"])
    cols = [
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), primary_key=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), primary_key=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("position", sa.String(), nullable=False),
        sa.Column("minutes", sa.Float()),
        sa.Column("uncertainty", sa.String()),
        sa.Column("xg", sa.Float()),
    ]
    cols += [
        sa.Column(key, sa.Integer(), nullable=False)
        for key in ("shots", "goals", "xg_missing", "passes", "completed", "penalties")
    ]
    op.create_table("appearances", *cols, sa.CheckConstraint("minutes IS NULL OR minutes >= 0"))
    op.create_index("ix_appearances_team_id", "appearances", ["team_id"])
    op.create_index("ix_appearances_role", "appearances", ["role"])


def downgrade():
    for table in ("appearances", "events", "imports", "matches", "players", "teams", "seasons"):
        op.drop_table(table)
