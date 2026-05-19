import pytest
from httpx import AsyncClient
from sqlalchemy import text

pytestmark = pytest.mark.asyncio


async def test_admin_can_list_users(authed_admin_client: AsyncClient, admin_user):
    r = await authed_admin_client.get("/api/users")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert any(u["email"] == "admin@swa.co.in" for u in body["items"])


async def test_pm_cannot_list_users(authed_pm_client: AsyncClient):
    r = await authed_pm_client.get("/api/users")
    assert r.status_code == 403


async def test_admin_can_create_user(authed_admin_client: AsyncClient):
    r = await authed_admin_client.post(
        "/api/users",
        json={
            "email": "designer@swa.co.in",
            "name": "Designer",
            "password": "design123!",
            "role": "designer",
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "designer@swa.co.in"
    assert body["role"] == "designer"
    assert "password" not in body
    assert "password_hash" not in body


async def test_create_user_duplicate_email(authed_admin_client: AsyncClient, admin_user):
    r = await authed_admin_client.post(
        "/api/users",
        json={
            "email": "admin@swa.co.in",
            "name": "Dup",
            "password": "x1234567!",
            "role": "viewer",
        },
    )
    assert r.status_code in (409, 400)


async def test_create_user_short_password(authed_admin_client: AsyncClient):
    r = await authed_admin_client.post(
        "/api/users",
        json={
            "email": "short@swa.co.in",
            "name": "Short",
            "password": "abc",
            "role": "viewer",
        },
    )
    assert r.status_code == 422


async def test_pm_cannot_create_user(authed_pm_client: AsyncClient):
    r = await authed_pm_client.post(
        "/api/users",
        json={
            "email": "x@swa.co.in",
            "name": "X",
            "password": "x1234567!",
            "role": "viewer",
        },
    )
    assert r.status_code == 403


async def test_self_can_read_own(authed_pm_client: AsyncClient, pm_user):
    r = await authed_pm_client.get(f"/api/users/{pm_user.id}")
    assert r.status_code == 200


async def test_pm_cannot_read_other(authed_pm_client: AsyncClient, admin_user):
    r = await authed_pm_client.get(f"/api/users/{admin_user.id}")
    assert r.status_code == 403


async def test_self_can_update_own_name(authed_pm_client: AsyncClient, pm_user):
    r = await authed_pm_client.patch(f"/api/users/{pm_user.id}", json={"name": "PM Renamed"})
    assert r.status_code == 200
    assert r.json()["name"] == "PM Renamed"


async def test_self_cannot_update_own_role(authed_pm_client: AsyncClient, pm_user):
    r = await authed_pm_client.patch(f"/api/users/{pm_user.id}", json={"role": "admin"})
    assert r.status_code == 403


async def test_soft_delete(authed_admin_client: AsyncClient, db_session):
    r = await authed_admin_client.post(
        "/api/users",
        json={
            "email": "del@swa.co.in",
            "name": "Del",
            "password": "x1234567!",
            "role": "viewer",
        },
    )
    user_id = r.json()["id"]
    r2 = await authed_admin_client.delete(f"/api/users/{user_id}")
    assert r2.status_code == 204
    r3 = await authed_admin_client.get("/api/users")
    emails = [u["email"] for u in r3.json()["items"]]
    assert "del@swa.co.in" not in emails
    row = db_session.execute(
        text("SELECT deleted_at FROM users WHERE email = :email"), {"email": "del@swa.co.in"}
    ).fetchone()
    assert row is not None
    assert row[0] is not None


async def test_admin_cannot_delete_self(authed_admin_client: AsyncClient, admin_user):
    r = await authed_admin_client.delete(f"/api/users/{admin_user.id}")
    assert r.status_code == 403


async def test_audit_log_on_create(authed_admin_client: AsyncClient, db_session):
    await authed_admin_client.post(
        "/api/users",
        json={
            "email": "audit@swa.co.in",
            "name": "Audit",
            "password": "x1234567!",
            "role": "viewer",
        },
    )
    rows = db_session.execute(
        text("SELECT after_json FROM audit_log WHERE action = 'user.create'")
    ).fetchall()
    assert len(rows) >= 1
    import json

    after_raw = rows[-1][0]
    after = json.loads(after_raw) if isinstance(after_raw, str) else after_raw
    assert after["email"] == "audit@swa.co.in"


async def test_pagination(authed_admin_client: AsyncClient):
    for i in range(25):
        await authed_admin_client.post(
            "/api/users",
            json={
                "email": f"page{i}@swa.co.in",
                "name": f"P{i}",
                "password": "x1234567!",
                "role": "viewer",
            },
        )
    r = await authed_admin_client.get("/api/users?page=1&page_size=10")
    assert r.json()["page"] == 1
    assert len(r.json()["items"]) == 10
    r2 = await authed_admin_client.get("/api/users?page=3&page_size=10")
    assert r2.json()["page"] == 3
