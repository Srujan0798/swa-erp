import uuid
from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from src.backend.models.client import Client
from src.backend.models.document_reference import DocumentReference
from src.backend.models.project import Project
from src.backend.models.token import Token
from src.backend.models.user import User
from src.backend.schemas.document_reference import (
    DocumentReferenceCreate,
    DocumentReferenceUpdate,
)
from src.backend.services.document_reference_service import (
    ProjectNotFoundError,
    TokenNotFoundError,
    create_document_reference_service,
    get_document_reference_service,
    list_document_references_service,
    soft_delete_document_reference_service,
    update_document_reference_service,
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


def _seed_project(db, client, name="PRJ-A", code=None):
    pid = uuid.uuid4()
    p = Project(
        id=pid,
        client_id=client.id,
        name=name,
        code=code or f"P-{pid.hex[:6]}",
        status="Awarded",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _seed_token(db, project, actor):
    from src.backend.models.agreement import ServiceAgreement

    aid = uuid.uuid4()
    a = ServiceAgreement(
        id=aid,
        reference_id=f"SWA-{datetime.now(UTC).year}-SA-{aid.hex[:6]}",
        client_id=project.client_id,
        service_name="APEX",
        start_date=date(2026, 7, 1),
        status="Active",
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    tid = uuid.uuid4()
    t = Token(
        id=tid,
        reference_id=f"SWA-{datetime.now(UTC).year}-TKN-EXIST-{tid.hex[:6]}",
        agreement_id=a.id,
        token_date=date(2026, 7, 1),
        project_id=project.id,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


class TestDocumentReferenceModel:
    def test_create_assigns_reference_id_via_service(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client)
        doc_ref = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                doc_date=date(2026, 7, 1),
                document_type="DBR",
                description="DBR for project A",
            ),
            actor.id,
        )
        year = datetime.now(UTC).year
        assert doc_ref.reference_id == f"SWA-{year}-DBR-001"
        assert doc_ref.revision == "R0"
        assert doc_ref.status == "Draft"
        assert doc_ref.token_id is None

    def test_token_id_is_optional(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client)
        doc_ref = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                doc_date=date(2026, 7, 1),
                document_type="DBR",
            ),
            actor.id,
        )
        assert doc_ref.token_id is None
        assert doc_ref.project_id == project.id

    def test_token_id_can_be_set(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client)
        token = _seed_token(db_session, project, actor)
        doc_ref = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                token_id=token.id,
                doc_date=date(2026, 7, 1),
                document_type="DBR",
            ),
            actor.id,
        )
        assert doc_ref.token_id == token.id

    def test_project_id_must_exist(self, db_session):
        actor = _seed_user(db_session)
        with pytest.raises(ProjectNotFoundError):
            create_document_reference_service(
                db_session,
                DocumentReferenceCreate(
                    project_id=uuid.uuid4(),
                    doc_date=date(2026, 7, 1),
                    document_type="DBR",
                ),
                actor.id,
            )

    def test_token_id_must_exist_when_provided(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client)
        with pytest.raises(TokenNotFoundError):
            create_document_reference_service(
                db_session,
                DocumentReferenceCreate(
                    project_id=project.id,
                    token_id=uuid.uuid4(),
                    doc_date=date(2026, 7, 1),
                    document_type="DBR",
                ),
                actor.id,
            )


class TestDocumentReferenceNumbering:
    def test_dbr_then_kdr_share_counter(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client)
        a = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                doc_date=date(2026, 7, 1),
                document_type="DBR",
            ),
            actor.id,
        )
        b = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                doc_date=date(2026, 7, 1),
                document_type="KDR",
            ),
            actor.id,
        )
        year = datetime.now(UTC).year
        assert a.reference_id == f"SWA-{year}-DBR-001"
        assert b.reference_id == f"SWA-{year}-DBR-002"
        assert a.document_type == "DBR"
        assert b.document_type == "KDR"

    def test_other_doc_type_uses_independent_counter(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client)
        dbr = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                doc_date=date(2026, 7, 1),
                document_type="DBR",
            ),
            actor.id,
        )
        ged = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                doc_date=date(2026, 7, 1),
                document_type="GED",
            ),
            actor.id,
        )
        year = datetime.now(UTC).year
        assert dbr.reference_id == f"SWA-{year}-DBR-001"
        assert ged.reference_id == f"SWA-{year}-GED-001"

    def test_two_dbr_sequential(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client)
        a = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                doc_date=date(2026, 7, 1),
                document_type="DBR",
            ),
            actor.id,
        )
        b = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                doc_date=date(2026, 7, 1),
                document_type="DBR",
            ),
            actor.id,
        )
        year = datetime.now(UTC).year
        assert a.reference_id == f"SWA-{year}-DBR-001"
        assert b.reference_id == f"SWA-{year}-DBR-002"


class TestDocumentReferenceCrud:
    def test_get_by_id_returns_none_when_missing(self, db_session):
        assert get_document_reference_service(db_session, uuid.uuid4()) is None

    def test_soft_delete(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client)
        doc_ref = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                doc_date=date(2026, 7, 1),
                document_type="DBR",
            ),
            actor.id,
        )
        assert soft_delete_document_reference_service(
            db_session, doc_ref.id, actor.id
        ) is True
        assert get_document_reference_service(db_session, doc_ref.id) is None

    def test_list_filters_by_project(self, db_session):
        actor = _seed_user(db_session)
        c1 = _seed_client(db_session, name="C1", code="C1")
        c2 = _seed_client(db_session, name="C2", code="C2")
        p1 = _seed_project(db_session, c1, name="P1", code="P1")
        p2 = _seed_project(db_session, c2, name="P2", code="P2")
        create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=p1.id, doc_date=date(2026, 7, 1), document_type="DBR"
            ),
            actor.id,
        )
        create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=p1.id, doc_date=date(2026, 7, 1), document_type="KDR"
            ),
            actor.id,
        )
        create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=p2.id, doc_date=date(2026, 7, 1), document_type="GED"
            ),
            actor.id,
        )
        items, total, _, _ = list_document_references_service(
            db_session, 1, 20, p1.id, None, None, None
        )
        assert total == 2
        assert all(d.project_id == p1.id for d in items)

    def test_list_filters_by_token(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client)
        token = _seed_token(db_session, project, actor)
        with_t = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                token_id=token.id,
                doc_date=date(2026, 7, 1),
                document_type="DBR",
            ),
            actor.id,
        )
        create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id,
                doc_date=date(2026, 7, 1),
                document_type="KDR",
            ),
            actor.id,
        )
        items, total, _, _ = list_document_references_service(
            db_session, 1, 20, None, token.id, None, None
        )
        assert total == 1
        assert items[0].id == with_t.id

    def test_list_filters_by_document_type(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client)
        create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id, doc_date=date(2026, 7, 1), document_type="DBR"
            ),
            actor.id,
        )
        create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id, doc_date=date(2026, 7, 1), document_type="GED"
            ),
            actor.id,
        )
        items, total, _, _ = list_document_references_service(
            db_session, 1, 20, None, None, "GED", None
        )
        assert total == 1
        assert items[0].document_type == "GED"


class TestDocumentReferenceUpdate:
    def test_update_changes_status_and_revision(self, db_session):
        actor = _seed_user(db_session)
        client = _seed_client(db_session)
        project = _seed_project(db_session, client)
        doc_ref = create_document_reference_service(
            db_session,
            DocumentReferenceCreate(
                project_id=project.id, doc_date=date(2026, 7, 1), document_type="DBR"
            ),
            actor.id,
        )
        updated = update_document_reference_service(
            db_session,
            doc_ref.id,
            DocumentReferenceUpdate(status="Submitted", revision="R1"),
            actor.id,
        )
        assert updated.status == "Submitted"
        assert updated.revision == "R1"

    def test_update_missing_returns_none(self, db_session):
        actor = _seed_user(db_session)
        result = update_document_reference_service(
            db_session,
            uuid.uuid4(),
            DocumentReferenceUpdate(status="Submitted"),
            actor.id,
        )
        assert result is None


class TestDocumentReferenceSchema:
    def test_type_alias_roundtrip(self):
        schema = DocumentReferenceCreate(
            project_id=uuid.uuid4(),
            doc_date=date(2026, 7, 1),
            document_type="DBR",
            type="Submittal",
        )
        dumped = schema.model_dump(by_alias=True)
        assert dumped["type"] == "Submittal"
        assert "type_" not in dumped

    def test_document_type_required(self):
        with pytest.raises(ValidationError):
            DocumentReferenceCreate(
                project_id=uuid.uuid4(),
                doc_date=date(2026, 7, 1),
                document_type="",
            )


class TestDocumentReferenceApi:
    @pytest.mark.asyncio
    async def test_create_endpoint_with_only_project(
        self, authed_pm_client, db_session
    ):
        actor = _seed_user(db_session)
        client_obj = _seed_client(db_session)
        project = _seed_project(db_session, client_obj)
        r = await authed_pm_client.post(
            "/api/document-references",
            json={
                "project_id": str(project.id),
                "doc_date": "2026-07-01",
                "document_type": "DBR",
                "description": "Test DBR",
            },
        )
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["project_id"] == str(project.id)
        assert data["token_id"] is None
        assert data["document_type"] == "DBR"
        assert data["revision"] == "R0"
        assert data["status"] == "Draft"
        assert data["reference_id"].startswith("SWA-")
        assert "-DBR-" in data["reference_id"]

    @pytest.mark.asyncio
    async def test_create_endpoint_dbr_kdr_sequential(
        self, authed_pm_client, db_session
    ):
        actor = _seed_user(db_session)
        client_obj = _seed_client(db_session)
        project = _seed_project(db_session, client_obj)
        r1 = await authed_pm_client.post(
            "/api/document-references",
            json={
                "project_id": str(project.id),
                "doc_date": "2026-07-01",
                "document_type": "DBR",
            },
        )
        assert r1.status_code == 201, r1.text
        r2 = await authed_pm_client.post(
            "/api/document-references",
            json={
                "project_id": str(project.id),
                "doc_date": "2026-07-01",
                "document_type": "KDR",
            },
        )
        assert r2.status_code == 201, r2.text
        seq1 = int(r1.json()["reference_id"].split("-")[-1])
        seq2 = int(r2.json()["reference_id"].split("-")[-1])
        assert seq2 == seq1 + 1

    @pytest.mark.asyncio
    async def test_create_endpoint_missing_project_returns_404(
        self, authed_pm_client, db_session
    ):
        r = await authed_pm_client.post(
            "/api/document-references",
            json={
                "project_id": str(uuid.uuid4()),
                "doc_date": "2026-07-01",
                "document_type": "DBR",
            },
        )
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_list_endpoint(self, authed_pm_client, db_session):
        r = await authed_pm_client.get("/api/document-references")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body

    @pytest.mark.asyncio
    async def test_viewer_cannot_create(self, authed_viewer_client, db_session):
        r = await authed_viewer_client.post(
            "/api/document-references",
            json={
                "project_id": str(uuid.uuid4()),
                "doc_date": "2026-07-01",
                "document_type": "DBR",
            },
        )
        assert r.status_code == 403
