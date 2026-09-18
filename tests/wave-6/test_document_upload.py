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
def viewer_headers(db_session):
    from src.backend.core.security import create_access_token
    from src.backend.models.user import User

    user = User(
        email=f"viewer-{uuid.uuid4().hex[:6]}@test.com",
        name="Viewer User",
        password_hash="x",
        role="viewer",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user.id, "viewer")
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


def _create_project(db: Session, pm_id=None) -> uuid.UUID:
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
        pm_id=pm_id,
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
        # Evidence: folder/document endpoints enforce project membership since
        # aa03e77 (_require_project_access); the fixture PM is not auto-assigned
        # to the helper-created project, so assign them — this test's contract
        # is folder lifecycle, not RBAC denial (unassigned-PM denial is pinned
        # in TestFolderWriteProjectScoping below).
        from src.backend.models.user import User

        pm = db_session.query(User).filter(User.role == "pm").one()
        project_id = _create_project(db_session, pm_id=pm.id)
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
        # Evidence: see test_delete_folder — PM must be a project member since
        # aa03e77; assign them so the test exercises folder+doc lifecycle.
        from src.backend.models.user import User

        pm = db_session.query(User).filter(User.role == "pm").one()
        project_id = _create_project(db_session, pm_id=pm.id)

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


class TestViewerCannotWriteDocuments:
    """L6-C (access matrix, docs/flows/02_auth_rbac.md): viewer is read-only.

    Every document write path is role-gated via require_role(DESIGNER|PM);
    role_includes(VIEWER, DESIGNER/PM) is False, so all writes must 403.
    Role dependencies fire before handler logic, so the target ids can be
    arbitrary here.
    """

    def test_viewer_cannot_upload_document(self, client, viewer_headers, db_session):
        project_id = _create_project(db_session)
        resp = client.post(
            f"/api/projects/{project_id}/documents",
            headers=viewer_headers,
            files=[_file_upload()],
        )
        assert resp.status_code == 403

    def test_viewer_cannot_reupload_document(self, client, viewer_headers, db_session):
        project_id = _create_project(db_session)
        resp = client.post(
            f"/api/projects/{project_id}/documents/re-upload",
            headers=viewer_headers,
            data={"original_name": "report.pdf"},
            files=[_file_upload(b"v2", "report.pdf")],
        )
        assert resp.status_code == 403

    def test_viewer_cannot_update_document(self, client, viewer_headers):
        resp = client.patch(
            f"/api/documents/{uuid.uuid4()}",
            headers=viewer_headers,
            json={"tags": "nope"},
        )
        assert resp.status_code == 403

    def test_viewer_cannot_delete_document(self, client, viewer_headers):
        resp = client.delete(f"/api/documents/{uuid.uuid4()}", headers=viewer_headers)
        assert resp.status_code == 403

    def test_viewer_cannot_rename_document(self, client, viewer_headers):
        resp = client.put(
            f"/api/documents/{uuid.uuid4()}/rename",
            headers=viewer_headers,
            json={"new_name": "nope.txt"},
        )
        assert resp.status_code == 403

    def test_viewer_cannot_move_documents(self, client, viewer_headers):
        resp = client.put(
            "/api/documents/move",
            headers=viewer_headers,
            json={"document_ids": [str(uuid.uuid4())], "target_folder_id": None},
        )
        assert resp.status_code == 403

    def test_viewer_cannot_create_folder(self, client, viewer_headers, db_session):
        project_id = _create_project(db_session)
        resp = client.post(
            f"/api/projects/{project_id}/folders",
            headers=viewer_headers,
            json={"name": "Nope", "project_id": str(project_id)},
        )
        assert resp.status_code == 403

    def test_viewer_cannot_rename_folder(self, client, viewer_headers):
        resp = client.put(
            f"/api/folders/{uuid.uuid4()}/rename",
            headers=viewer_headers,
            json={"new_name": "Nope"},
        )
        assert resp.status_code == 403

    def test_viewer_cannot_delete_folder(self, client, viewer_headers):
        resp = client.delete(f"/api/folders/{uuid.uuid4()}", headers=viewer_headers)
        assert resp.status_code == 403


class TestFolderWriteProjectScoping:
    """L6-C: folder rename/delete enforce project membership (aa03e77 follow-up).

    Commit aa03e77 added ``_require_project_access`` to every documents
    endpoint except ``PUT /api/folders/{id}/rename`` and
    ``DELETE /api/folders/{id}``. The fix resolves folder -> project before
    writing: a PM with no membership in the folder's project gets 403;
    admins bypass (documents.py ``_require_project_access``).
    """

    def _make_folder(self, client, headers, project_id, name="Scoped"):
        resp = client.post(
            f"/api/projects/{project_id}/folders",
            headers=headers,
            json={"name": name, "project_id": str(project_id)},
        )
        assert resp.status_code == 201, resp.text
        return resp.json()

    def test_unassigned_pm_cannot_delete_folder(self, client, auth_headers, pm_headers, db_session):
        project_id = _create_project(db_session)  # pm_id=None -> PM has no membership
        folder = self._make_folder(client, auth_headers, project_id)
        resp = client.delete(f"/api/folders/{folder['id']}", headers=pm_headers)
        assert resp.status_code == 403

    def test_unassigned_pm_cannot_rename_folder(self, client, auth_headers, pm_headers, db_session):
        project_id = _create_project(db_session)
        folder = self._make_folder(client, auth_headers, project_id)
        resp = client.put(
            f"/api/folders/{folder['id']}/rename",
            headers=pm_headers,
            json={"new_name": "Hacked"},
        )
        assert resp.status_code == 403

    def test_assigned_pm_can_rename_folder(self, client, pm_headers, db_session):
        from src.backend.models.user import User

        pm = db_session.query(User).filter(User.role == "pm").one()
        project_id = _create_project(db_session, pm_id=pm.id)
        folder = self._make_folder(client, pm_headers, project_id)
        resp = client.put(
            f"/api/folders/{folder['id']}/rename",
            headers=pm_headers,
            json={"new_name": "Renamed OK"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed OK"

    def test_admin_can_delete_folder_in_unassigned_project(self, client, auth_headers, db_session):
        project_id = _create_project(db_session)  # admin is not pm/designer/auditor
        folder = self._make_folder(client, auth_headers, project_id)
        resp = client.delete(f"/api/folders/{folder['id']}", headers=auth_headers)
        assert resp.status_code == 204
