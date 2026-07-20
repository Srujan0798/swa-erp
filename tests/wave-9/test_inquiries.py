import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from src.backend.models.client import Client
from src.backend.models.user import User
from src.backend.schemas.inquiry import InquiryConvertRequest, InquiryCreate, InquiryUpdate
from src.backend.services.inquiry_service import (
    InquiryConversionError,
    convert_inquiry,
    create_inquiry_service,
    get_inquiry_service,
    list_inquiries_service,
    soft_delete_inquiry_service,
    update_inquiry_service,
)


def _seed_user(db, role="pm", email=None, name="PM User"):
    uid = uuid.uuid4()
    u = User(
        id=uid,
        email=email or f"{uid.hex[:8]}@test.com",
        name=name,
        password_hash="x",
        role=role,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _seed_client(db, name="Acme Corp", code=None):
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


class TestInquiryCrud:
    def test_create_assigns_reference_id(self, db_session):
        actor = _seed_user(db_session)
        data = InquiryCreate(
            inquiry_date=date(2026, 7, 1),
            inquiry_type="Design",
            inquiry_source="Referral",
            client_name="Acme",
            requirement_summary="New warehouse MEP",
            estimated_value=Decimal("500000.00"),
            priority="High",
        )
        inquiry = create_inquiry_service(db_session, data, actor.id)
        year = datetime.now(UTC).year
        assert inquiry.reference_id == f"SWA-{year}-INQ-001"
        assert inquiry.status == "New"

    def test_create_two_inquiries_increment_seq(self, db_session):
        actor = _seed_user(db_session)
        a = create_inquiry_service(
            db_session,
            InquiryCreate(inquiry_date=date(2026, 7, 1), client_name="A"),
            actor.id,
        )
        b = create_inquiry_service(
            db_session,
            InquiryCreate(inquiry_date=date(2026, 7, 1), client_name="B"),
            actor.id,
        )
        assert a.reference_id.endswith("-001")
        assert b.reference_id.endswith("-002")

    def test_get_by_id_returns_none_when_missing(self, db_session):
        assert get_inquiry_service(db_session, uuid.uuid4()) is None

    def test_list_filters_by_status(self, db_session):
        actor = _seed_user(db_session)
        a = create_inquiry_service(
            db_session,
            InquiryCreate(inquiry_date=date(2026, 7, 1), client_name="A"),
            actor.id,
        )
        b = create_inquiry_service(
            db_session,
            InquiryCreate(inquiry_date=date(2026, 7, 1), client_name="B"),
            actor.id,
        )
        update_inquiry_service(db_session, b.id, InquiryUpdate(status="Contacted"), actor.id)
        items, total, _, _ = list_inquiries_service(db_session, 1, 20, None, "New")
        assert total == 1
        assert items[0].id == a.id

    def test_soft_delete_marks_deleted_at(self, db_session):
        actor = _seed_user(db_session)
        inquiry = create_inquiry_service(
            db_session,
            InquiryCreate(inquiry_date=date(2026, 7, 1), client_name="X"),
            actor.id,
        )
        assert soft_delete_inquiry_service(db_session, inquiry.id, actor.id) is True
        assert get_inquiry_service(db_session, inquiry.id) is None
        assert soft_delete_inquiry_service(db_session, inquiry.id, actor.id) is False


class TestConvertInquiryExistingClient:
    def test_existing_client_does_not_create_duplicate(self, db_session):
        actor = _seed_user(db_session)
        existing = _seed_client(db_session, name="Acme Corp")
        before_count = db_session.query(Client).count()

        inquiry = create_inquiry_service(
            db_session,
            InquiryCreate(inquiry_date=date(2026, 7, 1), client_name="Acme Corp"),
            actor.id,
        )
        req = InquiryConvertRequest(
            project_name="Acme Warehouse",
            project_code="ACME-PRJ-1",
        )
        result = convert_inquiry(db_session, inquiry.id, req, actor.id)
        after_count = db_session.query(Client).count()
        assert after_count == before_count
        assert result["client"].id == existing.id
        assert result["project"].client_id == existing.id
        assert result["inquiry"].status == "Converted"
        assert result["inquiry"].converted_client_id == existing.id
        assert result["inquiry"].converted_project_id == result["project"].id

    def test_can_pass_client_id_to_pin_specific_client(self, db_session):
        actor = _seed_user(db_session)
        _seed_client(db_session, name="Acme Corp")
        b = _seed_client(db_session, name="Acme Corp 2")
        inquiry = create_inquiry_service(
            db_session,
            InquiryCreate(inquiry_date=date(2026, 7, 1), client_name="Acme"),
            actor.id,
        )
        req = InquiryConvertRequest(
            project_name="Test", project_code="T-1", client_id=b.id
        )
        result = convert_inquiry(db_session, inquiry.id, req, actor.id)
        assert result["client"].id == b.id


class TestConvertInquiryNewClient:
    def test_no_existing_client_creates_client_and_project(self, db_session):
        actor = _seed_user(db_session)
        before_clients = db_session.query(Client).count()
        inquiry = create_inquiry_service(
            db_session,
            InquiryCreate(
                inquiry_date=date(2026, 7, 1),
                client_name="Brand New Client",
                estimated_value=Decimal("1000000"),
            ),
            actor.id,
        )
        req = InquiryConvertRequest(
            project_name="New Project",
            project_code="NP-1",
            client_primary_email="contact@brandnewclient.com",
            client_industry="Manufacturing",
        )
        result = convert_inquiry(db_session, inquiry.id, req, actor.id)
        after_clients = db_session.query(Client).count()
        assert after_clients == before_clients + 1
        assert result["client"].name == "Brand New Client"
        assert result["client"].industry == "Manufacturing"
        assert result["client"].first_inquiry_id == inquiry.id
        assert result["project"].name == "New Project"
        assert result["project"].client_id == result["client"].id
        assert result["project"].estimated_value == Decimal("1000000")
        assert result["inquiry"].status == "Converted"
        assert result["inquiry"].converted_client_id == result["client"].id
        assert result["inquiry"].converted_project_id == result["project"].id

    def test_client_code_uses_reference_id_format(self, db_session):
        actor = _seed_user(db_session)
        inquiry = create_inquiry_service(
            db_session,
            InquiryCreate(inquiry_date=date(2026, 7, 1), client_name="NewCo"),
            actor.id,
        )
        req = InquiryConvertRequest(
            project_name="NewCo P1", project_code="NEWCO-1",
            client_primary_email="c@newco.com",
        )
        result = convert_inquiry(db_session, inquiry.id, req, actor.id)
        year = datetime.now(UTC).year
        assert result["client"].code == f"SWA-{year}-CLT-001"


class TestConvertInquiryAmbiguity:
    def test_two_clients_same_name_returns_ambiguous(self, db_session):
        actor = _seed_user(db_session)
        _seed_client(db_session, name="Acme", code="A1")
        _seed_client(db_session, name="Acme", code="A2")
        inquiry = create_inquiry_service(
            db_session,
            InquiryCreate(inquiry_date=date(2026, 7, 1), client_name="Acme"),
            actor.id,
        )
        req = InquiryConvertRequest(project_name="P", project_code="P-1")
        with pytest.raises(InquiryConversionError) as exc_info:
            convert_inquiry(db_session, inquiry.id, req, actor.id)
        assert exc_info.value.status_code == 300
        body = exc_info.value.body
        assert body["inquiry_client_name"] == "Acme"
        assert len(body["candidates"]) == 2
        codes = {c["code"] for c in body["candidates"]}
        assert codes == {"A1", "A2"}


class TestConvertInquiryRejections:
    def test_double_convert_returns_409(self, db_session):
        actor = _seed_user(db_session)
        inquiry = create_inquiry_service(
            db_session,
            InquiryCreate(inquiry_date=date(2026, 7, 1), client_name="Acme"),
            actor.id,
        )
        req = InquiryConvertRequest(
            project_name="P", project_code="P-1",
            client_primary_email="c@acme.com",
        )
        convert_inquiry(db_session, inquiry.id, req, actor.id)
        with pytest.raises(InquiryConversionError) as exc_info:
            convert_inquiry(db_session, inquiry.id, req, actor.id)
        assert exc_info.value.status_code == 409

    def test_missing_inquiry_returns_404(self, db_session):
        actor = _seed_user(db_session)
        req = InquiryConvertRequest(project_name="P", project_code="P-1")
        with pytest.raises(InquiryConversionError) as exc_info:
            convert_inquiry(db_session, uuid.uuid4(), req, actor.id)
        assert exc_info.value.status_code == 404


class TestInquiryApi:
    @pytest.mark.asyncio
    async def test_create_inquiry_endpoint(self, authed_pm_client, db_session):
        body = {
            "inquiry_date": "2026-07-01",
            "client_name": "API Co",
            "priority": "Medium",
        }
        r = await authed_pm_client.post("/api/inquiries", json=body)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["client_name"] == "API Co"
        assert data["reference_id"].startswith("SWA-")
        assert data["status"] == "New"

    @pytest.mark.asyncio
    async def test_list_inquiries_endpoint(self, authed_pm_client, db_session):
        await authed_pm_client.post(
            "/api/inquiries",
            json={"inquiry_date": "2026-07-01", "client_name": "Z"},
        )
        r = await authed_pm_client.get("/api/inquiries")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body
        assert body["total"] >= 1

    @pytest.mark.asyncio
    async def test_convert_endpoint_new_client(self, authed_pm_client, db_session):
        r = await authed_pm_client.post(
            "/api/inquiries",
            json={"inquiry_date": "2026-07-01", "client_name": "BrandX"},
        )
        iid = r.json()["id"]
        r2 = await authed_pm_client.post(
            f"/api/inquiries/{iid}/convert",
            json={
                "project_name": "BrandX Project",
                "project_code": "BX-1",
                "client_primary_email": "c@brandx.com",
            },
        )
        assert r2.status_code == 200, r2.text
        data = r2.json()
        assert data["inquiry"]["status"] == "Converted"
        assert "client_id" in data
        assert "project_id" in data

    @pytest.mark.asyncio
    async def test_convert_endpoint_ambiguous_returns_300(
        self, authed_pm_client, admin_user, db_session
    ):
        from src.backend.core.security import create_access_token

        token = create_access_token(admin_user.id)
        client_with_admin = authed_pm_client
        client_with_admin.headers["Authorization"] = f"Bearer {token}"
        for code in ("AMB-1", "AMB-2"):
            r = await client_with_admin.post(
                "/api/clients",
                json={"name": "Twin", "code": code, "primary_email": f"{code}@t.com"},
            )
            assert r.status_code == 201, r.text
        r = await client_with_admin.post(
            "/api/inquiries",
            json={"inquiry_date": "2026-07-01", "client_name": "Twin"},
        )
        iid = r.json()["id"]
        r2 = await client_with_admin.post(
            f"/api/inquiries/{iid}/convert",
            json={"project_name": "P", "project_code": "P-1"},
        )
        assert r2.status_code == 300, r2.text
        body = r2.json()
        # FastAPI wraps non-string detail as {"detail": <body>}
        detail = body["detail"] if isinstance(body.get("detail"), dict) else body
        assert detail["detail"] == "Ambiguous client match"
        assert len(detail["candidates"]) == 2

    @pytest.mark.asyncio
    async def test_viewer_cannot_create_inquiry(self, authed_viewer_client, db_session):
        r = await authed_viewer_client.post(
            "/api/inquiries",
            json={"inquiry_date": "2026-07-01", "client_name": "X"},
        )
        assert r.status_code == 403
