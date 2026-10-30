"""Offline synthetic seed for CI browser tests. Refuses a demo database URL."""

import sys
from pathlib import Path

from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend/tests"))
from app.db import DATABASE_URL, engine
from app.ingest import import_match
from fixtures import fixture, lineups, meta

if "_test" not in DATABASE_URL and ":55433/" not in DATABASE_URL:
    raise RuntimeError("Dedicated test database required")
with Session(engine) as db, db.begin():
    import_match(db, meta(), fixture(), lineups(), {"synthetic": "sha-test"}, "synthetic-test-only")
print("SYNTHETIC TEST DATABASE ONLY")
