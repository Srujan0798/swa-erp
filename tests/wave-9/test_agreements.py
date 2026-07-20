import uuid
from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from src.backend.models.client import Client
from src.backend.models.inquiry import Inquiry
from src.backend.models.user import User
from src.backend.schemas.agreement import (
    ServiceAgreementCreate,
    ServiceAgreementUpdate,
)
from src.backend.services.agreement_service import (
    create_agreement_service,
    get_agreement_service,
    list_agreements_service,
    soft_delete_agreement_service,
    update_agreement_service,
)


def _seed_user(db, role="pm"):
    uid = uuid.uuid4()
    u = User(
        id=uid,
        email=f"{uid.hex[:8]}@test.com",
        name="PM",
        password_hash="x",
        role=role,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _seed_client(db, name="Acme", code=None):
    cid = uuid.uuid4()
    c = Client(
        id=cid,
        name=name,
        code=code or f"C-{cid.hex[:8]}",
        primary_email=f"{cid.hex[:6]}@test.com",
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _seed_inquiry(db, client_name="Acme"):
    iid = uuid.uuid4()
    i = Inquiry(
        id=iid,
        reference_id=f"SWA-{datetime.now(UTC).year}-INQ-999",
        inquiry_date=date(2026, 7, 1),
        client_name=client_name,
        status="New",
    )
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


class TestServiceNameFreeText:
    def test_accepts_unknown_service_name(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = create_agreement_service(
            db_session,
            ServiceAgreementCreate(
                client_id=client.id,
                service_name="INSUDESIGN",
                start_date=date(2026, 7, 1),
            ),
            actor.id,
        )
        assert agreement.service_name == "INSUDESIGN"

    def test_accepts_long_arbitrary_service_name(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        long = "Custom One-Off " + "X" * 200
        agreement = create_agreement_service(
            db_session,
            ServiceAgreementCreate(
                client_id=client.id, service_name=long, start_date=date(2026, 7, 1)
            ),
            actor.id,
        )
        assert agreement.service_name == long


class TestAgreementCrud:
    def test_create_assigns_reference_id(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = create_agreement_service(
            db_session,
            ServiceAgreementCreate(
                client_id=client.id,
                service_name="APEX",
                start_date=date(2026, 7, 1),
                end_date=date(2027, 6, 30),
                total_tokens=100,
            ),
            actor.id,
        )
        year = datetime.now(UTC).year
        assert agreement.reference_id == f"SWA-{year}-SA-001"
        assert agreement.status == "Active"

    def test_total_tokens_can_be_null(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = create_agreement_service(
            db_session,
            ServiceAgreementCreate(
                client_id=client.id, service_name="APEX", start_date=date(2026, 7, 1)
            ),
            actor.id,
        )
        assert agreement.total_tokens is None

    def test_get_by_id_returns_none_when_missing(self, db_session):
        assert get_agreement_service(db_session, uuid.uuid4()) is None

    def test_soft_delete(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = create_agreement_service(
            db_session,
            ServiceAgreementCreate(
                client_id=client.id, service_name="APEX", start_date=date(2026, 7, 1)
            ),
            actor.id,
        )
        assert soft_delete_agreement_service(db_session, agreement.id, actor.id) is True
        assert get_agreement_service(db_session, agreement.id) is None

    def test_list_filters_by_client(self, db_session):
        actor = _seed_user(db_session)
        c1 = _seed_client(db_session, name="C1", code="C1")
        c2 = _seed_client(db_session, name="C2", code="C2")
        create_agreement_service(
            db_session,
            ServiceAgreementCreate(client_id=c1.id, service_name="X", start_date=date(2026, 7, 1)),
            actor.id,
        )
        create_agreement_service(
            db_session,
            ServiceAgreementCreate(client_id=c1.id, service_name="Y", start_date=date(2026, 7, 1)),
            actor.id,
        )
        create_agreement_service(
            db_session,
            ServiceAgreementCreate(client_id=c2.id, service_name="Z", start_date=date(2026, 7, 1)),
            actor.id,
        )
        items, total, _, _ = list_agreements_service(db_session, 1, 20, c1.id, None, None, None)
        assert total == 2
        assert all(a.client_id == c1.id for a in items)


class TestAgreementDateValidation:
    def test_end_before_start_rejected_at_schema(self):
        with pytest.raises(ValidationError):
            ServiceAgreementCreate(
                client_id=uuid.uuid4(),
                service_name="X",
                start_date=date(2026, 7, 1),
                end_date=date(2026, 6, 30),
            )

    def test_end_equal_to_start_accepted(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = create_agreement_service(
            db_session,
            ServiceAgreementCreate(
                client_id=client.id,
                service_name="X",
                start_date=date(2026, 7, 1),
                end_date=date(2026, 7, 1),
            ),
            actor.id,
        )
        assert agreement.end_date == date(2026, 7, 1)

    def test_update_validates_end_after_start(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = create_agreement_service(
            db_session,
            ServiceAgreementCreate(
                client_id=client.id,
                service_name="X",
                start_date=date(2026, 7, 1),
                end_date=date(2026, 12, 31),
            ),
            actor.id,
        )
        with pytest.raises(ValueError):
            update_agreement_service(
                db_session,
                agreement.id,
                ServiceAgreementUpdate(end_date=date(2026, 1, 1)),
                actor.id,
            )


class TestAgreementApi:
    @pytest.mark.asyncio
    async def test_create_agreement_endpoint(
        self, authed_pm_client, admin_user, db_session
    ):
        from src.backend.core.security import create_access_token

        token = create_access_token(admin_user.id)
        client = authed_pm_client
        client.headers["Authorization"] = f"Bearer {token}"
        r = await client.post(
            "/api/clients",
            json={"name": "AC", "code": f"AC-{uuid.uuid4().hex[:6]}", "primary_email": "ac@x.com"},
        )
        assert r.status_code == 201
        cid = r.json()["id"]
        body = {
            "client_id": cid,
            "service_name": "APEX",
            "start_date": "2026-07-01",
            "end_date": "2027-06-30",
            "total_tokens": 50,
        }
        r = await client.post("/api/service-agreements", json=body)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["service_name"] == "APEX"
        assert data["total_tokens"] == 50
        assert data["reference_id"].startswith("SWA-")

    @pytest.mark.asyncio
    async def test_list_agreements_endpoint(self, authed_pm_client, db_session):
        r = await authed_pm_client.get("/api/service-agreements")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body

    @pytest.mark.asyncio
    async def test_end_before_start_returns_422(
        self, authed_pm_client, admin_user, db_session
    ):
        from src.backend.core.security import create_access_token

        token = create_access_token(admin_user.id)
        client = authed_pm_client
        client.headers["Authorization"] = f"Bearer {token}"
        r = await client.post(
            "/api/clients",
            json={"name": "AC2", "code": f"AC2-{uuid.uuid4().hex[:6]}", "primary_email": "ac2@x.com"},
        )
        assert r.status_code == 201
        cid = r.json()["id"]
        body = {
            "client_id": cid,
            "service_name": "APEX",
            "start_date": "2026-07-01",
            "end_date": "2026-06-30",
        }
        r = await client.post("/api/service-agreements", json=body)
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_viewer_cannot_create_agreement(self, authed_viewer_client, db_session):
        r = await authed_viewer_client.post(
            "/api/service-agreements",
            json={
                "client_id": str(uuid.uuid4()),
                "service_name": "APEX",
                "start_date": "2026-07-01",
            },
        )
        assert r.status_code == 403
