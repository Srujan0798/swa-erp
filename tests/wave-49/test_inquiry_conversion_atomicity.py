"""Wave-49: atomicity test for inquiry conversion.

Proves that if project creation fails AFTER client creation,
the client row is rolled back (not left as an orphan).
"""
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from src.backend.models.client import Client
from src.backend.models.user import User
from src.backend.core.security import hash_password
from src.backend.schemas.inquiry import InquiryCreate, InquiryConvertRequest
from src.backend.services.inquiry_service import convert_inquiry, create_inquiry_service

TEST_DATABASE_URL = "postgresql://swa:***@localhost:5432/swa_erp_test"


@pytest.fixture
def actor(db_session):
    u = User(
        email="w49-actor@swa.co.in",
        name="W49 Actor",
        password_hash=hash_password("w49pass!"),
        role="pm",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


def test_convert_inquiry_rolls_back_client_on_project_failure(db_session, actor):
    """If project creation fails, the client created just before must NOT persist as an orphan."""
    inquiry = create_inquiry_service(
        db_session,
        InquiryCreate(
            inquiry_date=date(2025, 1, 1),
            client_name="W49 Orphan Probe Client",
            requirement_summary="atomicity probe",
        ),
        actor.id,
    )
    db_session.refresh(inquiry)

    req = InquiryConvertRequest(project_name="W49 Probe Project")

# Force project creation to fail AFTER client has been created
    with patch(
        "src.backend.db.repositories.project_repo.create_project",
        side_effect=RuntimeError("simulated project failure"),
    ):
        with pytest.raises(RuntimeError):
            convert_inquiry(db_session, inquiry.id, req, actor.id)

    # Roll back the session -- simulates what the get_db() wrapper does on exception
    db_session.rollback()

    # Use a FRESH session (on the TEST DB) to check -- avoids identity-map cache artifacts
    eng = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, future=True)
    Fresh = sessionmaker(autocommit=False, autoflush=False, bind=eng, expire_on_commit=False)
    fresh = Fresh()
    try:
        orphans = fresh.query(Client).filter(Client.name == "W49 Orphan Probe Client").all()
        assert orphans == [], (
            f"ATOMICITY VIOLATION: orphan client persisted after failed conversion: "
            f"{[(str(c.id), c.name, c.code) for c in orphans]}"
        )
    finally:
        fresh.close()
        eng.dispose()
