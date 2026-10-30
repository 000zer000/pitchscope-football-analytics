import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://pitchscope:pitchscope@127.0.0.1:55432/pitchscope"
)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"prepare_threshold": None},
    pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
    max_overflow=0,
)


def session():
    with Session(engine) as db:
        yield db
