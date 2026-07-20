"""Isolated SQLite session for Wave 13 import tests (no postgres dependency)."""
from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.backend.db.base import Base
from src.backend.models import Client, Inquiry, Project, ServiceAgreement


# Wave 13 import tests are fully self-contained on SQLite; skip the root
# conftest's postgres `setup_test_db` autouse fixture (it drops/creates the
# postgres schema and is prone to deadlocks under load here).
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    yield


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    make_session = sessionmaker(bind=engine, expire_on_commit=False)
    s = make_session()
    try:
        yield s
    finally:
        s.close()
        engine.dispose()


@pytest.fixture
def seeded(session):
    client = Client(
        code="SWA-2025-CLT-001",
        name="Acme Corp",
        primary_email="acme@example.com",
    )
    session.add(client)
    session.flush()
    session.add(
        Inquiry(
            reference_id="SWA-2025-INQ-001",
            inquiry_date=date.today(),
            client_name="Acme Corp",
            status="New",
        )
    )
    session.add(
        ServiceAgreement(
            reference_id="SWA-2025-SA-011",
            client_id=client.id,
            service_name="INSUDESIGN",
            start_date=date.today(),
        )
    )
    session.add(
        Project(code="SWA-2025-PRJ-065", client_id=client.id, name="Green Tower")
    )
    session.commit()
    return session
