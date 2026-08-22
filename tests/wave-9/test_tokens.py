import uuid
from datetime import UTC, date, datetime
from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import ValidationError

from src.backend.models.agreement import ServiceAgreement
from src.backend.models.client import Client
from src.backend.models.token import Token
from src.backend.models.user import User
from src.backend.schemas.token import TokenCreate, TokenUpdate
from src.backend.services.token_service import (
    create_token_service,
    get_token_service,
    list_tokens_service,
    soft_delete_token_service,
    update_token_service,
)
from tests.conftest import TestingSessionLocal


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


def _seed_agreement(db, client, service_name="APEX"):
    aid = uuid.uuid4()
    a = ServiceAgreement(
        id=aid,
        reference_id=f"SWA-{datetime.now(UTC).year}-SA-EXIST-{aid.hex[:6]}",
        client_id=client.id,
        service_name=service_name,
        start_date=date(2026, 7, 1),
        status="Active",
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


class TestTokenReferenceIdGeneration:
    def test_create_assigns_reference_id(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = _seed_agreement(db_session, client)
        token = create_token_service(
            db_session,
            TokenCreate(
                agreement_id=agreement.id,
                token_date=date(2026, 7, 1),
                token_type="Query",
                description="System R & U value calculation",
            ),
            actor.id,
        )
        year = datetime.now(UTC).year
        assert token.reference_id == f"SWA-{year}-TKN-001"
        assert token.token_status == "In Progress"
        assert token.tokens_used == 1

    def test_create_stores_excel_employee_names(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = _seed_agreement(db_session, client)
        token = create_token_service(
            db_session,
            TokenCreate(
                agreement_id=agreement.id,
                token_date=date(2026, 7, 1),
                token_type="Query",
                swa_employee_name="Mihir",
                project_owner_name="Priya",
                client_employee_name="Akash",
            ),
            actor.id,
        )
        assert token.swa_employee_name == "Mihir"
        assert token.project_owner_name == "Priya"
        assert token.client_employee_name == "Akash"

    def test_two_tokens_increment_seq(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = _seed_agreement(db_session, client)
        a = create_token_service(
            db_session,
            TokenCreate(
                agreement_id=agreement.id,
                token_date=date(2026, 7, 1),
            ),
            actor.id,
        )
        b = create_token_service(
            db_session,
            TokenCreate(
                agreement_id=agreement.id,
                token_date=date(2026, 7, 1),
            ),
            actor.id,
        )
        assert a.reference_id.endswith("-001")
        assert b.reference_id.endswith("-002")

    def test_tokens_used_defaults_to_one(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = _seed_agreement(db_session, client)
        token = create_token_service(
            db_session,
            TokenCreate(
                agreement_id=agreement.id,
                token_date=date(2026, 7, 1),
            ),
            actor.id,
        )
        assert token.tokens_used == 1

    def test_tokens_used_uses_supplied_value(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = _seed_agreement(db_session, client)
        token = create_token_service(
            db_session,
            TokenCreate(
                agreement_id=agreement.id,
                token_date=date(2026, 7, 1),
                tokens_used=2,
            ),
            actor.id,
        )
        assert token.tokens_used == 2


class TestTokenCrud:
    def test_get_by_id_returns_none_when_missing(self, db_session):
        assert get_token_service(db_session, uuid.uuid4()) is None

    def test_soft_delete(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = _seed_agreement(db_session, client)
        token = create_token_service(
            db_session,
            TokenCreate(
                agreement_id=agreement.id,
                token_date=date(2026, 7, 1),
            ),
            actor.id,
        )
        assert soft_delete_token_service(db_session, token.id, actor.id) is True
        assert get_token_service(db_session, token.id) is None

    def test_list_filters_by_agreement(self, db_session):
        actor = _seed_user(db_session)
        c1 = _seed_client(db_session, name="C1", code="C1")
        c2 = _seed_client(db_session, name="C2", code="C2")
        a1 = _seed_agreement(db_session, c1, service_name="X")
        a2 = _seed_agreement(db_session, c2, service_name="Y")
        create_token_service(
            db_session,
            TokenCreate(agreement_id=a1.id, token_date=date(2026, 7, 1)),
            actor.id,
        )
        create_token_service(
            db_session,
            TokenCreate(agreement_id=a1.id, token_date=date(2026, 7, 1)),
            actor.id,
        )
        create_token_service(
            db_session,
            TokenCreate(agreement_id=a2.id, token_date=date(2026, 7, 1)),
            actor.id,
        )
        items, total, _, _ = list_tokens_service(db_session, 1, 20, a1.id, None, None, None)
        assert total == 2
        assert all(t.agreement_id == a1.id for t in items)

    def test_list_filters_by_status(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = _seed_agreement(db_session, client)
        t1 = create_token_service(
            db_session,
            TokenCreate(agreement_id=agreement.id, token_date=date(2026, 7, 1)),
            actor.id,
        )
        t2 = create_token_service(
            db_session,
            TokenCreate(
                agreement_id=agreement.id,
                token_date=date(2026, 7, 1),
                token_status="Closed",
            ),
            actor.id,
        )
        items, total, _, _ = list_tokens_service(
            db_session, 1, 20, None, None, "Closed", None
        )
        assert total == 1
        assert items[0].id == t2.id
        assert t1.token_status == "In Progress"


class TestTokenUpdate:
    def test_update_changes_status(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = _seed_agreement(db_session, client)
        token = create_token_service(
            db_session,
            TokenCreate(agreement_id=agreement.id, token_date=date(2026, 7, 1)),
            actor.id,
        )
        updated = update_token_service(
            db_session,
            token.id,
            TokenUpdate(token_status="Closed"),
            actor.id,
        )
        assert updated.token_status == "Closed"

    def test_update_missing_returns_none(self, db_session):
        actor = _seed_user(db_session)
        result = update_token_service(
            db_session,
            uuid.uuid4(),
            TokenUpdate(token_status="Closed"),
            actor.id,
        )
        assert result is None

    def test_tokens_used_rejects_zero(self):
        with pytest.raises(ValidationError):
            TokenCreate(
                agreement_id=uuid.uuid4(),
                token_date=date(2026, 7, 1),
                tokens_used=0,
            )


class TestTokenApi:
    @pytest.mark.asyncio
    async def test_create_token_endpoint(
        self, authed_pm_client, admin_user, db_session
    ):
        from src.backend.core.security import create_access_token

        token = create_access_token(admin_user.id)
        client = authed_pm_client
        client.headers["Authorization"] = f"Bearer {token}"
        r = await client.post(
            "/api/clients",
            json={"name": "TC", "code": f"TC-{uuid.uuid4().hex[:6]}", "primary_email": "tc@x.com"},
        )
        assert r.status_code == 201
        cid = r.json()["id"]
        r2 = await client.post(
            "/api/service-agreements",
            json={"client_id": cid, "service_name": "APEX", "start_date": "2026-07-01"},
        )
        assert r2.status_code == 201, r2.text
        aid = r2.json()["id"]
        body = {
            "agreement_id": aid,
            "token_date": "2026-10-03",
            "token_type": "Query",
            "description": "System R & U value calculation",
            "client_employee_name": "Akash",
        }
        r3 = await client.post("/api/tokens", json=body)
        assert r3.status_code == 201, r3.text
        data = r3.json()
        assert data["token_type"] == "Query"
        assert data["token_status"] == "In Progress"
        assert data["tokens_used"] == 1
        assert data["client_employee_name"] == "Akash"
        assert data["reference_id"].startswith("SWA-")
        assert "-TKN-" in data["reference_id"]

    @pytest.mark.asyncio
    async def test_list_tokens_endpoint(self, authed_pm_client, db_session):
        r = await authed_pm_client.get("/api/tokens")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body

    @pytest.mark.asyncio
    async def test_viewer_cannot_create_token(self, authed_viewer_client, db_session):
        r = await authed_viewer_client.post(
            "/api/tokens",
            json={
                "agreement_id": str(uuid.uuid4()),
                "token_date": "2026-07-01",
            },
        )
        assert r.status_code == 403



    @pytest.mark.asyncio
    async def test_list_includes_agreement_reference_id(self, authed_pm_client, db_session):
        client = _seed_client(db_session, name="AgrRef", code="AGR-REF-C")
        agreement = _seed_agreement(db_session, client)
        actor = _seed_user(db_session)
        create_token_service(
            db_session,
            TokenCreate(agreement_id=agreement.id, token_date=date(2026, 7, 1)),
            actor.id,
        )
        r = await authed_pm_client.get("/api/tokens")
        assert r.status_code == 200
        items = r.json()["items"]
        match = next((t for t in items if t.get("agreement_id") == str(agreement.id)), None)
        assert match is not None
        assert match["agreement_reference_id"] == agreement.reference_id


class TestTokenConcurrency:
    def test_20_parallel_creates_produce_gapless_sequential_ids(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        agreement = _seed_agreement(db_session, client)
        n = 20

        def worker(_i):
            s = TestingSessionLocal()
            try:
                t = create_token_service(
                    s,
                    TokenCreate(
                        agreement_id=agreement.id,
                        token_date=date(2026, 7, 1),
                    ),
                    actor.id,
                )
                return t.reference_id
            finally:
                s.close()

        with ThreadPoolExecutor(max_workers=n) as ex:
            futures = [ex.submit(worker, i) for i in range(n)]
            ids = [f.result() for f in futures]

        year = datetime.now(UTC).year
        assert len(ids) == n
        assert len(set(ids)) == n, f"duplicate ids: {ids}"
        seqs = sorted(int(rid.split("-")[-1]) for rid in ids)
        assert seqs == list(range(1, n + 1)), f"expected 1..{n}, got {seqs}"
        for rid in ids:
            assert rid.startswith(f"SWA-{year}-TKN-")
