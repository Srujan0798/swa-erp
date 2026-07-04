"""Tests for Wave 6 Task 01 — Document Upload & Storage Backend."""
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


@pytest.fixture
def pm_headers(db_session):
    from src.backend.core.security import create_access_token
    from src.backend.models.user import User

    user = User(
        email=f"pm-{uuid.uuid4().hex[:6]}@test.com",
        name="PM User",
        password_hash="x",
        role="pm",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user.id, "pm")
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
    """Return a file upload tuple for TestClient: (filename, BytesIO, content_type)."""
    return ("file", (filename, io.BytesIO(content), "text/plain"))


class TestUploadDocument:
    def test_upload_document(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        resp = client.post(
            f"/api/projects/{project_id}/documents",
            headers=auth_headers,
            files=[_file_upload()],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["project_id"] == str(project_id)
        assert data["name"] == "test.txt"
        assert data["version_number"] == 1
        assert data["is_active"] is True
        assert data["file_size"] == len(b"hello world")

    def test_upload_document_with_folder(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)

        # Create a folder first
        folder_resp = client.post(
            f"/api/projects/{project_id}/folders",
            headers=auth_headers,
            json={"name": "Drawings", "project_id": str(project_id)},
        )
        assert folder_resp.status_code == 201
        folder_id = folder_resp.json()["id"]

        resp = client.post(
            f"/api/projects/{project_id}/documents",
            headers=auth_headers,
            files=[_file_upload()],
            data={"folder_id": folder_id},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["folder_id"] == folder_id

    def test_download_document(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        upload_resp = client.post(
            f"/api/projects/{project_id}/documents",
            headers=auth_headers,
            files=[_file_upload(b"downloadable content", "download.txt")],
        )
        assert upload_resp.status_code == 201
        doc_id = upload_resp.json()["id"]

        # Verify document metadata is retrievable
        get_resp = client.get(f"/api/documents/{doc_id}", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "download.txt"

    def test_list_documents_pagination(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        for i in range(5):
            client.post(
                f"/api/projects/{project_id}/documents",
                headers=auth_headers,
                files=[_file_upload(f"content{i}".encode(), f"file{i}.txt")],
            )

        resp = client.get(
            f"/api/projects/{project_id}/documents",
            headers=auth_headers,
            params={"page": 1, "page_size": 2},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 2

    def test_soft_delete_document(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        upload_resp = client.post(
            f"/api/projects/{project_id}/documents",
            headers=auth_headers,
            files=[_file_upload(b"delete me", "delete_me.txt")],
        )
        assert upload_resp.status_code == 201
        doc_id = upload_resp.json()["id"]

        delete_resp = client.delete(f"/api/documents/{doc_id}", headers=auth_headers)
        assert delete_resp.status_code == 204

        # Should not appear in listing
        list_resp = client.get(
            f"/api/projects/{project_id}/documents", headers=auth_headers
        )
        assert list_resp.status_code == 200
        items = list_resp.json()["items"]
        assert all(d["id"] != doc_id for d in items)

    def test_get_nonexistent_document(self, client, auth_headers, db_session):
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/api/documents/{fake_id}", headers=auth_headers)
        assert resp.status_code == 404


class TestCreateFolder:
    def test_create_folder(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        resp = client.post(
            f"/api/projects/{project_id}/folders",
            headers=auth_headers,
            json={"name": "Structural", "project_id": str(project_id)},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Structural"
        assert data["project_id"] == str(project_id)

    def test_list_folders(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)
        for name in ["A", "B", "C"]:
            client.post(
                f"/api/projects/{project_id}/folders",
                headers=auth_headers,
                json={"name": name, "project_id": str(project_id)},
            )

        resp = client.get(
            f"/api/projects/{project_id}/folders", headers=auth_headers
        )
        assert resp.status_code == 200
        folders = resp.json()
        assert len(folders) == 3
        names = [f["name"] for f in folders]
        assert names == ["A", "B", "C"]  # sorted alphabetically

    def test_delete_folder(self, client, pm_headers, db_session):
        project_id = _create_project(db_session)
        folder_resp = client.post(
            f"/api/projects/{project_id}/folders",
            headers=pm_headers,
            json={"name": "To Delete", "project_id": str(project_id)},
        )
        assert folder_resp.status_code == 201
        folder_id = folder_resp.json()["id"]

        delete_resp = client.delete(f"/api/folders/{folder_id}", headers=pm_headers)
        assert delete_resp.status_code == 204

    def test_delete_folder_soft_deletes_documents(self, client, pm_headers, db_session):
        project_id = _create_project(db_session)

        # Create folder
        folder_resp = client.post(
            f"/api/projects/{project_id}/folders",
            headers=pm_headers,
            json={"name": "Docs Folder", "project_id": str(project_id)},
        )
        folder_id = folder_resp.json()["id"]

        # Upload doc into folder
        upload_resp = client.post(
            f"/api/projects/{project_id}/documents",
            headers=pm_headers,
            files=[_file_upload(b"content", "in_folder.txt")],
            data={"folder_id": folder_id},
        )
        assert upload_resp.status_code == 201

        # Delete folder
        delete_resp = client.delete(f"/api/folders/{folder_id}", headers=pm_headers)
        assert delete_resp.status_code == 204

        # Doc should no longer appear in list
        list_resp = client.get(
            f"/api/projects/{project_id}/documents",
            headers=pm_headers,
            params={"folder_id": folder_id},
        )
        assert list_resp.status_code == 200
        items = list_resp.json()["items"]
        assert len(items) == 0
