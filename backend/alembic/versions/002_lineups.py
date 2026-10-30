"""Persist source lineup metadata for repeatable role reconstruction."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("imports", sa.Column("lineups", JSONB(), nullable=False, server_default="[]"))


def downgrade():
    op.drop_column("imports", "lineups")
