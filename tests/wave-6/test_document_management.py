"""Tests for Wave 6 Task 02 — Document Management (CRUD, versioning, move, rename, search)."""
import io
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.backend.db.base import Base
from src.backend.db.session import get_db
from src.backend.main import app
import src.backend.models  # noqa: F401 - registers all models

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def _override_db():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def db_session():
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"DELETE FROM {table.name}"))
    with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(db_session):
    from src.backend.core.security import create_access_token
    from src.backend.models.user import User

    user = User(
        email=f"admin-{uuid.uuid4().hex[:6]}@test.com",
        name="Admin User",
        password_hash="x",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user.id, "admin")
    return {"Authorization": f"Bearer {token}"}


def _create_project(db: Session) -> uuid.UUID:
    from src.backend.models.project import Project
    from src.backend.models.client import Client

    client_obj = Client(
        name="Test Client",
        code=f"TC-{uuid.uuid4().hex[:6]}",
        primary_email="test@example.com",
    )
    db.add(client_obj)
    db.commit()
    db.refresh(client_obj)

    project = Project(
        client_id=client_obj.id,
        name="Test Project",
        code=f"TP-{uuid.uuid4().hex[:6]}",
        status="Lead",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project.id


def _file_upload(content: bytes = b"hello world", filename: str = "test.txt"):
    return ("file", (filename, io.BytesIO(content), "text/plain"))


def _upload_doc(client, auth_headers, project_id, filename="doc.pdf", content=b"data"):
    resp = client.post(
        f"/api/projects/{project_id}/documents",
        headers=auth_headers,
        files=[_file_upload(content, filename)],
    )
    assert resp.status_code == 201
    return resp.json()


class TestUpdateDocumentMetadata:
    def test_update_document_name(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        doc = _upload_doc(client, auth_headers, project_id)

        resp = client.patch(
            f"/api/documents/{doc['id']}",
            headers=auth_headers,
            json={"name": "renamed.pdf"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "renamed.pdf"

    def test_update_document_tags(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        doc = _upload_doc(client, auth_headers, project_id)

        resp = client.patch(
            f"/api/documents/{doc['id']}",
            headers=auth_headers,
            json={"tags": "structural,steel"},
        )
        assert resp.status_code == 200
        assert resp.json()["tags"] == "structural,steel"

    def test_update_nonexistent_document(self, client, auth_headers, db_session):
        fake_id = str(uuid.uuid4())
        resp = client.patch(
            f"/api/documents/{fake_id}",
            headers=auth_headers,
            json={"name": "nope.pdf"},
        )
        assert resp.status_code == 404


class TestReuploadCreatesVersion:
    def test_reupload_creates_v2(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        _upload_doc(client, auth_headers, project_id, "design.pdf", b"v1 content")

        # Re-upload same document name
        resp = client.post(
            f"/api/projects/{project_id}/documents/re-upload",
            headers=auth_headers,
            data={"original_name": "design.pdf"},
            files=[_file_upload(b"v2 content", "design.pdf")],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["version_number"] == 2
        assert data["parent_version_id"] is not None
        assert data["name"] == "design.pdf"

    def test_reupload_nonexistent_name(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        resp = client.post(
            f"/api/projects/{project_id}/documents/re-upload",
            headers=auth_headers,
            data={"original_name": "nonexistent.pdf"},
            files=[_file_upload(b"data", "nonexistent.pdf")],
        )
        assert resp.status_code == 404


class TestVersionHistory:
    def test_version_history(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        _upload_doc(client, auth_headers, project_id, "report.pdf", b"v1")

        # Re-upload to create v2
        client.post(
            f"/api/projects/{project_id}/documents/re-upload",
            headers=auth_headers,
            data={"original_name": "report.pdf"},
            files=[_file_upload(b"v2", "report.pdf")],
        )

        # Re-upload again to create v3
        client.post(
            f"/api/projects/{project_id}/documents/re-upload",
            headers=auth_headers,
            data={"original_name": "report.pdf"},
            files=[_file_upload(b"v3", "report.pdf")],
        )

        resp = client.get(
            f"/api/projects/{project_id}/documents/versions/report.pdf",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["current_version"] == 3
        assert len(data["versions"]) == 3
        versions = [v["version_number"] for v in data["versions"]]
        assert versions == [1, 2, 3]


class TestRenameDocument:
    def test_rename_document(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        doc = _upload_doc(client, auth_headers, project_id, "old_name.pdf")

        resp = client.put(
            f"/api/documents/{doc['id']}/rename",
            headers=auth_headers,
            json={"new_name": "new_name.pdf"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "new_name.pdf"

    def test_rename_nonexistent(self, client, auth_headers, db_session):
        fake_id = str(uuid.uuid4())
        resp = client.put(
            f"/api/documents/{fake_id}/rename",
            headers=auth_headers,
            json={"new_name": "x.pdf"},
        )
        assert resp.status_code == 404


class TestMoveDocuments:
    def test_move_documents(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)

        # Create two folders
        f1 = client.post(
            f"/api/projects/{project_id}/folders",
            headers=auth_headers,
            json={"name": "Folder A", "project_id": str(project_id)},
        ).json()
        f2 = client.post(
            f"/api/projects/{project_id}/folders",
            headers=auth_headers,
            json={"name": "Folder B", "project_id": str(project_id)},
        ).json()

        # Upload doc into Folder A
        doc = _upload_doc(client, auth_headers, project_id, "move_me.pdf")
        client.patch(
            f"/api/documents/{doc['id']}",
            headers=auth_headers,
            json={"folder_id": f1["id"]},
        )

        # Move to Folder B
        resp = client.put(
            "/api/documents/move",
            headers=auth_headers,
            json={
                "document_ids": [doc["id"]],
                "target_folder_id": f2["id"],
            },
        )
        assert resp.status_code == 200
        assert resp.json()["moved"] == 1

        # Verify doc is now in Folder B
        list_resp = client.get(
            f"/api/projects/{project_id}/documents",
            headers=auth_headers,
            params={"folder_id": f2["id"]},
        )
        assert list_resp.status_code == 200
        items = list_resp.json()["items"]
        assert any(d["id"] == doc["id"] for d in items)


class TestFolderRename:
    def test_folder_rename(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        folder = client.post(
            f"/api/projects/{project_id}/folders",
            headers=auth_headers,
            json={"name": "Old Name", "project_id": str(project_id)},
        ).json()

        resp = client.put(
            f"/api/folders/{folder['id']}/rename",
            headers=auth_headers,
            json={"new_name": "New Name"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"


class TestSearchDocuments:
    def test_search_by_name(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        _upload_doc(client, auth_headers, project_id, "report.pdf", b"data1")
        _upload_doc(client, auth_headers, project_id, "spec.pdf", b"data2")

        resp = client.get(
            f"/api/projects/{project_id}/documents/search",
            headers=auth_headers,
            params={"q": "report"},
        )
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 1
        assert results[0]["name"] == "report.pdf"

    def test_search_by_tags(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)

        doc1 = _upload_doc(client, auth_headers, project_id, "doc1.pdf")
        client.patch(
            f"/api/documents/{doc1['id']}",
            headers=auth_headers,
            json={"tags": "structural,steel"},
        )

        doc2 = _upload_doc(client, auth_headers, project_id, "doc2.pdf")
        client.patch(
            f"/api/documents/{doc2['id']}",
            headers=auth_headers,
            json={"tags": "architectural"},
        )

        resp = client.get(
            f"/api/projects/{project_id}/documents/search",
            headers=auth_headers,
            params={"tags": "steel"},
        )
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 1
        assert results[0]["id"] == doc1["id"]

    def test_search_empty_query_returns_all(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        _upload_doc(client, auth_headers, project_id, "a.pdf")
        _upload_doc(client, auth_headers, project_id, "b.pdf")

        resp = client.get(
            f"/api/projects/{project_id}/documents/search",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 2
