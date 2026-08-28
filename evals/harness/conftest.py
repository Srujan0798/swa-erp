"""Shared fixtures for the wave-43 evals harness.

Reuses the project's real test stack (live FastAPI ASGI app over a real Postgres
test DB at postgresql://swa:***@localhost:5432/swa_erp_test). Every *trial* resets
all tables — including reference_counters — so ID-sequence assertions (task 002) are
reproducible across trials instead of accidentally depending on prior state.

This is a genuine eval harness, not a stub: it drives the application through its
real HTTP API the way a client (PM / Viewer) would, then hands environmental state to
the deterministic graders in evals/graders/code_based.py.
"""
from __future__ import annotations

import os
import uuid

# Disable the auth rate limiter so repeated logins in one process don't 429.
os.environ.setdefault("DISABLE_AUTH_RATE_LIMIT", "1")

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.backend.db.base import Base
from src.backend.db.session import get_db
from src.backend.main import app
import src.backend.models  # noqa: F401  (register all models with Base.metadata)


TEST_DATABASE_URL = os.environ.get(
    "EVALS_TEST_DATABASE_URL", "postgresql://swa:***@localhost:5432/swa_erp_test"
)
engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, future=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


def _reset_schema() -> None:
    """Drop + recreate public schema and all tables (fresh start for the session)."""
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    Base.metadata.create_all(bind=engine)


def _truncate_all() -> None:
    """Reset every table + reference_counters (restart identity) to fresh state."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        )
        existing = {r[0] for r in result}
        tables = [t for t in Base.metadata.tables.keys() if t in existing]
        if tables:
            conn.execute(
                text(f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE")
            )
        conn.commit()


@pytest.fixture(scope="session", autouse=True)
def _setup_session():
    _reset_schema()
    yield
    _reset_schema()


@pytest.fixture
def db_session():
    """Fresh DB with all rows wiped; yields a session bound to the eval engine."""
    _truncate_all()
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """AsyncClient bound to the live app with get_db overridden to the eval session."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def reset_db(db_session):
    """Reset all tables before each trial so trials run against fresh, independent state.

    Uses the SAME db_session connection the app is bound to (the test's `db_session`),
    so the TRUNCATE does not deadlock against an open transaction on a separate engine —
    a naive separate-engine truncate would block on the app's idle-in-transaction
    connection and make the suite crawl. Invoke (call) at the top of a trial.

    Table names are taken from Base.metadata (authoritative) rather than hard-coded, so
    they never drift from the models.
    """

    def _do_reset():
        tables = [t for t in Base.metadata.tables.keys()]
        if tables:
            db_session.execute(
                text(f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE")
            )
            db_session.commit()

    return _do_reset
