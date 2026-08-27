"""Tests for RBAC and auth gap fixes - Wave 22"""
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest

from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.core.security import hash_password
from src.backend.core.roles import Role


def create_test_user(db: Session, role: Role) -> User:
    """Helper to create a test user with a specific role"""
    user = User(
        id=uuid.uuid4(),
        email=f"test-{role.value}@example.com",
        name=f"Test {role.value.title()}",
        password_hash=hash_password("test123!"),
        role=role,
        is_active=True,
        deleted_at=None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(client, email, password="test123!"):
    """Helper to login and get auth headers"""
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    if response.status_code == 200:
        token = response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
        return token
    return None


@pytest.fixture
def test_client(db_session):
    """Test client with DB override"""
    from src.backend.main import app
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


class TestMaterialsAuth:
    """Test materials endpoint authentication fixes"""

    def test_material_categories_requires_auth(self, test_client, db_session):
        """Test that material-categories endpoint requires auth"""
        response = test_client.get("/api/material-categories")
        # FastAPI HTTPBearer(auto_error=True) returns 403 when Authorization header is absent entirely.
        # 401 is reserved for malformed/invalid credentials. This asserts the real production behaviour.
        assert response.status_code == 403

    def test_materials_requires_auth(self, test_client, db_session):
        """Test that materials endpoint requires auth"""
        response = test_client.get("/api/materials")
        # FastAPI HTTPBearer(auto_error=True) returns 403 when Authorization header is absent entirely.
        # 401 is reserved for malformed/invalid credentials. This asserts the real production behaviour.
        assert response.status_code == 403

    def test_material_requires_auth(self, test_client, db_session):
        """Test that materials/{id} endpoint requires auth"""
        material_id = uuid.uuid4()
        response = test_client.get(f"/api/materials/{material_id}")
        # FastAPI HTTPBearer(auto_error=True) returns 403 when Authorization header is absent entirely.
        # 401 is reserved for malformed/invalid credentials. This asserts the real production behaviour.
        assert response.status_code == 403


class TestProjectPnlRoleEnforcement:
    """Test project PNL endpoint role enforcement"""

    def test_pnl_summary_pm_allowed(self, test_client, db_session):
        """Test that PM can access P&L summary"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        project_id = uuid.uuid4()
        response = test_client.get(f"/api/projects/{project_id}/pnl")
        assert response.status_code not in (401, 403)

    def test_pnl_summary_admin_allowed(self, test_client, db_session):
        """Test that Admin can access P&L summary"""
        create_test_user(db_session, Role.ADMIN)
        login_user(test_client, "test-admin@example.com")
        project_id = uuid.uuid4()
        response = test_client.get(f"/api/projects/{project_id}/pnl")
        assert response.status_code not in (401, 403)

    def test_pnl_summary_viewer_denied(self, test_client, db_session):
        """Test that Viewer is denied access to P&L summary"""
        create_test_user(db_session, Role.VIEWER)
        login_user(test_client, "test-viewer@example.com")
        project_id = uuid.uuid4()
        response = test_client.get(f"/api/projects/{project_id}/pnl")
        assert response.status_code == 403

    def test_add_cost_admin_allowed(self, test_client, db_session):
        """Test that Admin can add cost entry"""
        create_test_user(db_session, Role.ADMIN)
        login_user(test_client, "test-admin@example.com")
        project_id = uuid.uuid4()
        body = {"category": "test", "amount": 100.0}
        response = test_client.post(f"/api/projects/{project_id}/costs", json=body)
        assert response.status_code not in (401, 403)

    def test_add_cost_pm_allowed(self, test_client, db_session):
        """Test that PM can add cost entry (aligned with DELETE — ADMIN+PM)"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        project_id = uuid.uuid4()
        body = {"category": "test", "amount": 100.0}
        response = test_client.post(f"/api/projects/{project_id}/costs", json=body)
        assert response.status_code not in (401, 403)

    def test_delete_cost_viewer_denied(self, test_client, db_session):
        """VIEWER must not delete project costs"""
        create_test_user(db_session, Role.VIEWER)
        login_user(test_client, "test-viewer@example.com")
        project_id = uuid.uuid4()
        cost_id = uuid.uuid4()
        response = test_client.delete(f"/api/projects/{project_id}/costs/{cost_id}")
        assert response.status_code == 403

    def test_delete_cost_pm_allowed_auth(self, test_client, db_session):
        """PM is authorized to delete costs (404 if missing is fine)"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        project_id = uuid.uuid4()
        cost_id = uuid.uuid4()
        response = test_client.delete(f"/api/projects/{project_id}/costs/{cost_id}")
        assert response.status_code not in (401, 403)


class TestExportsRoleEnforcement:
    """Test exports endpoint role enforcement"""

    def test_export_summary_pm_allowed(self, test_client, db_session):
        """Test that PM can access export summary"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        project_id = uuid.uuid4()
        response = test_client.get(f"/api/exports/projects/{project_id}/summary.pdf")
        assert response.status_code not in (401, 403)

    def test_export_summary_admin_allowed(self, test_client, db_session):
        """Test that Admin can access export summary"""
        create_test_user(db_session, Role.ADMIN)
        login_user(test_client, "test-admin@example.com")
        project_id = uuid.uuid4()
        response = test_client.get(f"/api/exports/projects/{project_id}/summary.pdf")
        assert response.status_code not in (401, 403)

    def test_export_summary_viewer_denied(self, test_client, db_session):
        """Test that Viewer is denied for export summary"""
        create_test_user(db_session, Role.VIEWER)
        login_user(test_client, "test-viewer@example.com")
        project_id = uuid.uuid4()
        response = test_client.get(f"/api/exports/projects/{project_id}/summary.pdf")
        assert response.status_code == 403


class TestInvoicesRoleEnforcement:
    """Test invoices endpoint role enforcement"""

    def test_update_invoice_status_pm_allowed(self, test_client, db_session):
        """Test that PM can update invoice status"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        invoice_id = uuid.uuid4()
        body = {"status": "sent"}
        response = test_client.patch(f"/api/invoices/{invoice_id}/status", json=body)
        assert response.status_code not in (401, 403)

    def test_update_invoice_status_admin_allowed(self, test_client, db_session):
        """Test that Admin can update invoice status"""
        create_test_user(db_session, Role.ADMIN)
        login_user(test_client, "test-admin@example.com")
        invoice_id = uuid.uuid4()
        body = {"status": "paid"}
        response = test_client.patch(f"/api/invoices/{invoice_id}/status", json=body)
        assert response.status_code not in (401, 403)

    def test_update_invoice_status_viewer_denied(self, test_client, db_session):
        """Test that Viewer is denied for invoice status update"""
        create_test_user(db_session, Role.VIEWER)
        login_user(test_client, "test-viewer@example.com")
        invoice_id = uuid.uuid4()
        body = {"status": "sent"}
        response = test_client.patch(f"/api/invoices/{invoice_id}/status", json=body)
        assert response.status_code == 403


class TestInquiriesRoleEnforcement:
    """Test inquiries endpoint role enforcement"""

    def test_create_inquiry_pm_allowed(self, test_client, db_session):
        """Test that PM can create inquiry"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        body = {
            "client_id": str(uuid.uuid4()),
            "subject": "Test Inquiry",
            "description": "Test inquiry for RBAC fix",
        }
        response = test_client.post("/api/inquiries", json=body)
        assert response.status_code not in (401, 403)

    def test_create_inquiry_designer_allowed(self, test_client, db_session):
        """Test that Designer can create inquiry (after RBAC fix)"""
        create_test_user(db_session, Role.DESIGNER)
        login_user(test_client, "test-designer@example.com")
        body = {
            "client_id": str(uuid.uuid4()),
            "subject": "Test Inquiry",
            "description": "Test inquiry for RBAC fix",
        }
        response = test_client.post("/api/inquiries", json=body)
        assert response.status_code not in (401, 403)

    def test_create_inquiry_viewer_denied(self, test_client, db_session):
        """Test that Viewer is denied for creating inquiry"""
        create_test_user(db_session, Role.VIEWER)
        login_user(test_client, "test-viewer@example.com")
        body = {
            "client_id": str(uuid.uuid4()),
            "subject": "Test Inquiry",
            "description": "Test inquiry for RBAC fix",
        }
        response = test_client.post("/api/inquiries", json=body)
        assert response.status_code == 403


class TestDocumentReferencesRoleEnforcement:
    """Test document references endpoint role enforcement"""

    def test_create_dbr_kdr_pm_allowed(self, test_client, db_session):
        """Test that PM can create DBR/KDR document reference"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        body = {
            "project_id": str(uuid.uuid4()),
            "document_type": "DBR",
            "author_id": str(uuid.uuid4()),
            "doc_date": "2024-01-01",
        }
        response = test_client.post("/api/document-references", json=body)
        assert response.status_code not in (401, 403)

    def test_create_dbr_kdr_designer_allowed(self, test_client, db_session):
        """Test that Designer can create DBR/KDR document reference (after RBAC fix)"""
        create_test_user(db_session, Role.DESIGNER)
        login_user(test_client, "test-designer@example.com")
        body = {
            "project_id": str(uuid.uuid4()),
            "document_type": "KDR",
            "author_id": str(uuid.uuid4()),
            "doc_date": "2024-01-01",
        }
        response = test_client.post("/api/document-references", json=body)
        assert response.status_code not in (401, 403)

    def test_create_dbr_kdr_viewer_denied(self, test_client, db_session):
        """Test that Viewer is denied for creating DBR/KDR document reference"""
        create_test_user(db_session, Role.VIEWER)
        login_user(test_client, "test-viewer@example.com")
        body = {
            "project_id": str(uuid.uuid4()),
            "document_type": "DBR",
            "author_id": str(uuid.uuid4()),
            "doc_date": "2024-01-01",
        }
        response = test_client.post("/api/document-references", json=body)
        assert response.status_code == 403

    def test_create_reforge_auditor_allowed(self, test_client, db_session):
        """Test that Auditor can create Reforge document reference"""
        create_test_user(db_session, Role.AUDITOR)
        login_user(test_client, "test-auditor@example.com")
        body = {
            "project_id": str(uuid.uuid4()),
            "document_type": "Reforge",
            "author_id": str(uuid.uuid4()),
            "doc_date": "2024-01-01",
        }
        response = test_client.post("/api/document-references", json=body)
        assert response.status_code not in (401, 403)

    def test_create_reforge_designer_allowed(self, test_client, db_session):
        """Test that Designer can create Reforge document reference (after RBAC fix)"""
        create_test_user(db_session, Role.DESIGNER)
        login_user(test_client, "test-designer@example.com")
        body = {
            "project_id": str(uuid.uuid4()),
            "document_type": "Reforge",
            "author_id": str(uuid.uuid4()),
            "doc_date": "2024-01-01",
        }
        response = test_client.post("/api/document-references", json=body)
        assert response.status_code not in (401, 403)

    def test_create_reforge_pm_denied(self, test_client, db_session):
        """Test that PM is denied for creating Reforge document reference"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        body = {
            "project_id": str(uuid.uuid4()),
            "document_type": "Reforge",
            "author_id": str(uuid.uuid4()),
            "doc_date": "2024-01-01",
        }
        response = test_client.post("/api/document-references", json=body)
        assert response.status_code == 403

    def test_create_default_type_pm_allowed(self, test_client, db_session):
        """Test that PM can create default document reference type"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        body = {
            "project_id": str(uuid.uuid4()),
            "document_type": "Default",
            "author_id": str(uuid.uuid4()),
            "doc_date": "2024-01-01",
        }
        response = test_client.post("/api/document-references", json=body)
        assert response.status_code not in (401, 403)


class TestComplianceRoleEnforcement:
    """Test compliance endpoint role enforcement"""

    def test_review_item_auditor_allowed(self, test_client, db_session):
        """Test that Auditor can review compliance item"""
        create_test_user(db_session, Role.AUDITOR)
        login_user(test_client, "test-auditor@example.com")
        item_id = uuid.uuid4()
        body = {"notes": "Approved"}
        response = test_client.post(f"/api/compliance/items/{item_id}/review", json=body)
        assert response.status_code not in (401, 403)

    def test_review_item_designer_allowed(self, test_client, db_session):
        """Test that Designer can review compliance item (after RBAC fix)"""
        create_test_user(db_session, Role.DESIGNER)
        login_user(test_client, "test-designer@example.com")
        item_id = uuid.uuid4()
        body = {"notes": "Design approved"}
        response = test_client.post(f"/api/compliance/items/{item_id}/review", json=body)
        assert response.status_code not in (401, 403)

    def test_review_item_pm_denied(self, test_client, db_session):
        """Test that PM is denied for reviewing compliance item"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        item_id = uuid.uuid4()
        body = {"notes": "PM review"}
        response = test_client.post(f"/api/compliance/items/{item_id}/review", json=body)
        assert response.status_code == 403

    def test_review_item_viewer_denied(self, test_client, db_session):
        """Test that Viewer is denied for reviewing compliance item"""
        create_test_user(db_session, Role.VIEWER)
        login_user(test_client, "test-viewer@example.com")
        item_id = uuid.uuid4()
        body = {"notes": "Viewer review"}
        response = test_client.post(f"/api/compliance/items/{item_id}/review", json=body)
        assert response.status_code == 403


class TestTasksRoleEnforcement:
    """Test tasks endpoint role enforcement"""

    def test_transition_task_pm_allowed(self, test_client, db_session):
        """Test that PM can transition task"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        task_id = uuid.uuid4()
        body = {"to_status": "in_progress"}
        response = test_client.post(f"/api/tasks/{task_id}/transition", json=body)
        assert response.status_code not in (401, 403)

    def test_reorder_task_pm_allowed(self, test_client, db_session):
        """Test that PM can reorder task"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        task_id = uuid.uuid4()
        body = {"status": "completed", "sort_order": 1}
        response = test_client.post(f"/api/tasks/{task_id}/reorder", json=body)
        assert response.status_code not in (401, 403)

    def test_add_comment_pm_allowed(self, test_client, db_session):
        """Test that PM can add comment to task"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        task_id = uuid.uuid4()
        body = {"content": "Comment"}
        response = test_client.post(f"/api/tasks/{task_id}/comments", json=body)
        assert response.status_code not in (401, 403)

    def test_transition_task_viewer_denied(self, test_client, db_session):
        """Test that Viewer is denied for task transition"""
        create_test_user(db_session, Role.VIEWER)
        login_user(test_client, "test-viewer@example.com")
        task_id = uuid.uuid4()
        body = {"to_status": "in_progress"}
        response = test_client.post(f"/api/tasks/{task_id}/transition", json=body)
        assert response.status_code == 403


class TestRFQsRoleEnforcement:
    """Test RFQs endpoint role enforcement"""

    def test_send_rfq_pm_allowed(self, test_client, db_session):
        """Test that PM can send RFQ"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        rfq_id = uuid.uuid4()
        response = test_client.post(f"/api/rfqs/{rfq_id}/send")
        assert response.status_code not in (401, 403)

    def test_respond_rfq_pm_allowed(self, test_client, db_session):
        """Test that PM can respond to RFQ"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        rfq_id = uuid.uuid4()
        body = []
        response = test_client.post(f"/api/rfqs/{rfq_id}/respond", json=body)
        assert response.status_code not in (401, 403)

    def test_compare_rfq_pm_allowed(self, test_client, db_session):
        """Test that PM can compare RFQ"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        rfq_id = uuid.uuid4()
        response = test_client.post(f"/api/rfqs/{rfq_id}/compare")
        assert response.status_code not in (401, 403)

    def test_close_rfq_pm_allowed(self, test_client, db_session):
        """Test that PM can close RFQ"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        rfq_id = uuid.uuid4()
        response = test_client.post(f"/api/rfqs/{rfq_id}/close")
        assert response.status_code not in (401, 403)

    def test_cancel_rfq_pm_allowed(self, test_client, db_session):
        """Test that PM can cancel RFQ"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        rfq_id = uuid.uuid4()
        response = test_client.post(f"/api/rfqs/{rfq_id}/cancel")
        assert response.status_code not in (401, 403)

    def test_send_rfq_viewer_denied(self, test_client, db_session):
        """Test that Viewer is denied for sending RFQ"""
        create_test_user(db_session, Role.VIEWER)
        login_user(test_client, "test-viewer@example.com")
        rfq_id = uuid.uuid4()
        response = test_client.post(f"/api/rfqs/{rfq_id}/send")
        assert response.status_code == 403

    def test_award_rfq_pm_allowed(self, test_client, db_session):
        """Test that PM can award RFQ"""
        create_test_user(db_session, Role.PM)
        login_user(test_client, "test-pm@example.com")
        rfq_id = uuid.uuid4()
        response = test_client.post(f"/api/rfqs/{rfq_id}/award")
        assert response.status_code not in (401, 403)

