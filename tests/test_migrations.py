"""tests/test_migrations.py — proves alembic migrations actually produce the right schema.

The dev DB was once stamped at 0033 with 21 columns missing because no test
ever ran alembic upgrade head. tests/conftest.py builds the schema via
create_all + _stamp_alembic_head() — a blind test gate.

This test directly proves:
  1. The dev DB is NOT lying about migration status (alembic_version table
     has real content, not a stamped lie).
  2. All 21 columns added by migrations 0031/0032/0033 actually exist.
  3. Core tables are present.
  4. A fresh schema built via alembic upgrade head has all tables + columns.

Run:  python3 -m pytest tests/test_migrations.py -v
"""
from __future__ import annotations

import os
import subprocess
import uuid
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import src.backend.models  # noqa: F401 - registers all models with Base.metadata
from src.backend.core.security import hash_password
from src.backend.models.client import Client
from src.backend.models.inquiry import Inquiry
from src.backend.models.project import Project
from src.backend.models.time_tracking import TimeEntry
from src.backend.models.user import User

# ---------------------------------------------------------------------------
# The dev DB — connect via SQLAlchemy (no subprocess psql needed)
# ---------------------------------------------------------------------------

DEV_DB_URL = "postgresql://swa:***@localhost:5432/swa_erp"
_dev_engine = None


def _get_dev_engine():
    """Get or create the dev DB engine (singleton)."""
    global _dev_engine
    if _dev_engine is None:
        _dev_engine = create_engine(DEV_DB_URL, pool_pre_ping=True, future=True)
    return _dev_engine


def _dev_query(sql: str) -> list:
    """Run a query against the dev DB and return result rows."""
    engine = _get_dev_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = list(result)
        return rows


def _dev_column_exists(table: str, column: str) -> bool:
    """Check if a column exists in a table on the dev DB."""
    engine = _get_dev_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name=:t AND column_name=:c"
            ),
            {"t": table, "c": column},
        )
        return result.fetchone() is not None


# ---------------------------------------------------------------------------
# 1. Dev DB: alembic_version integrity
# ---------------------------------------------------------------------------

def test_dev_db_has_alembic_version_table():
    """The alembic_version table exists and is not empty."""
    rows = _dev_query("SELECT version_num FROM alembic_version")
    assert len(rows) == 1, f"Expected 1 row in alembic_version, got {len(rows)}: {rows}"
    version = rows[0][0]
    assert version, "alembic_version.version_num is empty"
    assert len(version) >= 4, f"Version looks fake: {version!r}"


def test_dev_db_at_alembic_head():
    """Dev DB alembic_version matches the latest migration file."""
    versions = sorted(Path("src/backend/alembic/versions").glob("*.py"))
    versions = [v for v in versions if v.name.startswith("00")]
    assert versions, "No migration files found"
    head_file = versions[-1]
    head = head_file.stem  # e.g. "0034_invoice_number_sequence"
    head_prefix = head.split("_")[0]  # e.g. "0034"

    rows = _dev_query("SELECT version_num FROM alembic_version")
    current = rows[0][0] if rows else None
    assert current == head_prefix, f"Dev DB not at head: current={current}, heads={head}"


# ---------------------------------------------------------------------------
# 2. The 21 columns added by migrations 0031/0032/0033 exist
# ---------------------------------------------------------------------------

COLUMN_CHECKS = [
    # clients (migration 0033)
    ("clients", "primary_contact"),
    ("clients", "date_onboarded"),
    # projects (migration 0033)
    ("projects", "milestone"),
    ("projects", "progress_indicators"),
    ("projects", "team_leader_name"),
    ("projects", "project_owner_name"),
    ("projects", "notes"),
    ("projects", "inquiry_id"),
    # time_entries (migration 0031)
    ("time_entries", "billable_hours"),
    ("time_entries", "employee_name"),
    ("time_entries", "employee_role"),
    ("time_entries", "work_type"),
    ("time_entries", "sheet_reference_id"),
    ("time_entries", "revision"),
    ("time_entries", "activity_type"),
    ("time_entries", "software_used"),
    ("time_entries", "work_mode"),
    # tokens (migration 0032)
    ("tokens", "swa_employee_name"),
    ("tokens", "project_owner_name"),
    # document_references (migration 0032)
    ("document_references", "author_name"),
    # inquiries (migration 0031)
    ("inquiries", "technical_lead"),
]


@pytest.mark.parametrize("table,column", COLUMN_CHECKS)
def test_column_exists(table: str, column: str):
    """Each column added by migrations 0031/0032/0033 must be present."""
    assert _dev_column_exists(table, column), (
        f"Column {table}.{column} MISSING — migration was not applied."
    )


# ---------------------------------------------------------------------------
# 3. Core tables exist
# ---------------------------------------------------------------------------

CORE_TABLES = [
    "users",
    "clients",
    "projects",
    "inquiries",
    "service_agreements",
    "tokens",
    "document_references",
    "time_entries",
    "sustainability_metrics",
    "compliance_checklist_items",
    "alembic_version",
]


def test_core_tables_exist():
    """All core tables exist in the dev DB."""
    rows = _dev_query(
        "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
    )
    existing = {r[0] for r in rows}
    for table in CORE_TABLES:
        assert table in existing, f"Core table {table} missing from dev DB"


# ---------------------------------------------------------------------------
# 4. Migrations produce a valid schema (scratch DB via alembic upgrade head)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def scratch_db():
    """Create a temporary DB, run alembic upgrade head, yield engine."""
    db_name = f"swa_erp_migration_test_{uuid.uuid4().hex[:8]}"
    password = os.environ.get("PGPASSWORD", "***")
    db_url = f"postgresql://swa:{password}@localhost:5432/{db_name}"

    # Create DB via psql (psql is on PATH in dev env)
    subprocess.run(
        ["psql", "-h", "localhost", "-U", "swa", "-d", "postgres",
         "-c", f"CREATE DATABASE {db_name}"],
        env=os.environ,
        check=True,
        capture_output=True,
        text=True,
    )

    engine = None
    try:
        # Run alembic upgrade head on the temp DB
        # env.py reads DATABASE_URL from environment — set it for this subprocess
        env = os.environ.copy()
        env["DATABASE_URL"] = db_url
        subprocess.run(
            [
                "python3", "-m", "alembic",
                "-c", "src/backend/alembic.ini",
                "upgrade", "head",
            ],
            cwd="/Users/srujansai/Desktop/swa-erp",
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

        engine = create_engine(db_url, pool_pre_ping=True, future=True)
        yield engine
    finally:
        if engine is not None:
            try:
                engine.dispose()
            except Exception:
                pass
        subprocess.run(
            ["psql", "-h", "localhost", "-U", "swa", "-d", "postgres",
             "-c", f"DROP DATABASE {db_name}"],
            env=os.environ,
            check=False,
            capture_output=True,
            text=True,
        )


def test_scratch_db_has_all_tables(scratch_db):
    """A fresh schema built via alembic upgrade head has all expected tables."""
    with scratch_db.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        tables = {r[0] for r in result}

    for table in CORE_TABLES:
        assert table in tables, f"Table {table} missing from scratch DB built via alembic upgrade head"


def test_scratch_db_has_all_columns(scratch_db):
    """All 21 columns exist on a fresh schema built via alembic upgrade head."""
    for table, col in COLUMN_CHECKS:
        with scratch_db.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='public' AND table_name=:t AND column_name=:c"
                ),
                {"t": table, "c": col},
            )
            row = result.fetchone()
            assert row is not None, (
                f"Column {table}.{col} missing from scratch DB built via alembic upgrade head"
            )


def test_scratch_db_core_chain_works(scratch_db):
    """Core chain works on a fresh schema (proves migrations are correct)."""
    Session = sessionmaker(bind=scratch_db, expire_on_commit=False)

    with Session() as session:
        c = Client(name="Test Client", code="TC-1", primary_email="tc1@test.com")
        session.add(c)
        session.flush()

        p = Project(
            client_id=c.id,
            name="Test Project",
            code="TP-1",
            milestone="Lead",
            notes="Test notes from migration verification",
            estimated_value=100000,
        )
        session.add(p)
        session.flush()

        u = User(
            email="test_user@swa.co.in",
            name="Test User",
            password_hash=hash_password("test123!"),
            role="viewer",
        )
        session.add(u)
        session.flush()
        user_id = u.id

        assert p.milestone == "Lead"
        assert p.notes == "Test notes from migration verification"

        i = Inquiry(
            reference_id="SWA-TEST-INQ-001",
            inquiry_date=date.today(),
            client_name="Test Client",
            technical_lead="test_lead",
            status="open",
            notes="Migration verification",
        )
        session.add(i)
        session.flush()

        assert i.technical_lead == "test_lead"

        t = TimeEntry(
            project_id=p.id,
            user_id=user_id,
            date=date.today(),
            hours=8,
            description="Migration test",
            billable_hours=8,
            employee_name="Test User",
            employee_role="engineer",
            work_type="design",
        )
        session.add(t)
        session.flush()

        assert t.billable_hours == 8
        assert t.employee_name == "Test User"
