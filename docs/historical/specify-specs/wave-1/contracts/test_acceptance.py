"""
Wave 1 acceptance contracts. These tests are the source of truth for wave-1 completion.
The orchestrator runs these as part of /review before approving any wave-1 task report.

Workers should ensure these pass; orchestrator independently verifies via the verifier sub-agent.
"""
import pytest
from httpx import AsyncClient
from fastapi import status

# These tests assume the FastAPI app is importable from src.backend.main
# Workers will create the app; this file describes what MUST work.

pytestmark = pytest.mark.asyncio


async def test_healthz(client: AsyncClient):
    """Liveness endpoint returns 200."""
    r = await client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_readyz_with_db(client: AsyncClient):
    """Readiness checks DB connection."""
    r = await client.get("/readyz")
    assert r.status_code == 200
    assert r.json()["db"] == "ok"


async def test_login_success(client: AsyncClient, admin_user):
    """US-1.1: valid credentials return tokens."""
    r = await client.post(
        "/api/auth/login",
        json={"email": admin_user.email, "password": "admin123!"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["user"]["email"] == admin_user.email
    assert body["user"]["role"] == "admin"


async def test_login_wrong_password(client: AsyncClient, admin_user):
    """Login with wrong password returns 401."""
    r = await client.post(
        "/api/auth/login",
        json={"email": admin_user.email, "password": "wrong"},
    )
    assert r.status_code == 401


async def test_me_requires_auth(client: AsyncClient):
    """/api/auth/me without token returns 401."""
    r = await client.get("/api/auth/me")
    assert r.status_code == 401


async def test_admin_can_list_users(authed_admin_client: AsyncClient):
    """US-1.2 prerequisite: admin can list users."""
    r = await authed_admin_client.get("/api/users")
    assert r.status_code == 200
    assert isinstance(r.json()["items"], list)


async def test_admin_can_create_user(authed_admin_client: AsyncClient):
    """US-1.2: admin can create a new user."""
    r = await authed_admin_client.post(
        "/api/users",
        json={
            "email": "new@swa.local",
            "name": "New PM",
            "password": "secure123!",
            "role": "pm",
        },
    )
    assert r.status_code == 201
    assert r.json()["email"] == "new@swa.local"
    assert r.json()["role"] == "pm"


async def test_pm_cannot_list_users(authed_pm_client: AsyncClient):
    """US-1.4: PM gets 403 on /api/users."""
    r = await authed_pm_client.get("/api/users")
    assert r.status_code == 403


async def test_refresh_token(client: AsyncClient, admin_refresh_token: str):
    """Refresh token returns a new access token."""
    r = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": admin_refresh_token},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


async def test_expired_token_rejected(client: AsyncClient, expired_token: str):
    """US-1.5: expired JWT returns 401."""
    r = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert r.status_code == 401


async def test_audit_log_on_user_create(authed_admin_client: AsyncClient, db_session):
    """Audit log entry is created on user creation."""
    await authed_admin_client.post(
        "/api/users",
        json={
            "email": "audit-test@swa.local",
            "name": "Audit Test",
            "password": "audit123!",
            "role": "viewer",
        },
    )
    # Query audit_log for the create event
    from src.backend.models.audit_log import AuditLog
    audit = await db_session.execute(
        "SELECT action, entity_type FROM audit_log WHERE entity_type='user' AND action='user.create' ORDER BY created_at DESC LIMIT 1"
    )
    row = audit.first()
    assert row is not None
    assert row.action == "user.create"


async def test_soft_delete(authed_admin_client: AsyncClient):
    """DELETE on user soft-deletes (deleted_at set, row still in DB)."""
    # Create then delete
    r = await authed_admin_client.post(
        "/api/users",
        json={"email": "del@swa.local", "name": "Del Me", "password": "x12345!", "role": "viewer"},
    )
    user_id = r.json()["id"]
    r2 = await authed_admin_client.delete(f"/api/users/{user_id}")
    assert r2.status_code == 204
    # User should not appear in list
    r3 = await authed_admin_client.get("/api/users")
    emails = [u["email"] for u in r3.json()["items"]]
    assert "del@swa.local" not in emails
