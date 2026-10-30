import os

import pytest
from app.db import session
from app.main import app
from app.models import Base
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


@pytest.fixture()
def db():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL required: dedicated PostgreSQL test database")
    if url == os.getenv("DATABASE_URL") or ("_test" not in url and ":55433/" not in url):
        raise RuntimeError("Refusing non-test database")
    engine = create_engine(url, connect_args={"prepare_threshold": None}, pool_size=1, max_overflow=0)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
        s.rollback()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def client(db):
    app.dependency_overrides[session] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def pytest_addoption(parser):
    parser.addoption(
        "--require-postgres", action="store_true", help="Require native PostgreSQL and forbid skips"
    )


def pytest_sessionstart(session):
    if session.config.getoption("--require-postgres"):
        url = os.getenv("TEST_DATABASE_URL")
        if not url:
            raise pytest.UsageError("TEST_DATABASE_URL is required for native integration validation")
        check = create_engine(url)
        try:
            with check.connect() as connection:
                version = connection.execute(text("SELECT version()")).scalar_one()
                if "PostgreSQL" not in version or "PGlite" in version:
                    raise pytest.UsageError(
                        "Native PostgreSQL required, not an emulation or WebAssembly build"
                    )
        except Exception as exc:
            raise pytest.UsageError(f"Native test database unavailable: {exc}") from exc
        finally:
            check.dispose()


def pytest_sessionfinish(session, exitstatus):
    if session.config.getoption("--require-postgres"):
        reporter = session.config.pluginmanager.getplugin("terminalreporter")
        if reporter and reporter.stats.get("skipped"):
            session.exitstatus = 1
