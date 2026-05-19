import uuid
from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt
from sqlalchemy import text

from src.backend.core.config import settings
from src.backend.core.roles import Role, role_includes
from src.backend.core.security import decode_token

pytestmark = pytest.mark.asyncio


async def test_login_success(client_with_db, admin_user):
    r = await client_with_db.post(
        "/api/auth/login",
        json={"email": "admin@swa.co.in", "password": "admin123!"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["user"]["email"] == "admin@swa.co.in"
    assert body["user"]["role"] == "admin"


async def test_login_wrong_password(client_with_db, admin_user):
    r = await client_with_db.post(
        "/api/auth/login",
        json={"email": "admin@swa.co.in", "password": "wrong"},
    )
    assert r.status_code == 401


async def test_login_unknown_email(client_with_db):
    r = await client_with_db.post(
        "/api/auth/login",
        json={"email": "nope@swa.co.in", "password": "x"},
    )
    assert r.status_code == 401


async def test_me_requires_bearer(client):
    r = await client.get("/api/auth/me")
    assert r.status_code in (401, 403)


async def test_me_with_valid_token(client_with_db, admin_user):
    r = await client_with_db.post(
        "/api/auth/login",
        json={"email": "admin@swa.co.in", "password": "admin123!"},
    )
    token = r.json()["access_token"]
    r2 = await client_with_db.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200
    assert r2.json()["email"] == "admin@swa.co.in"


async def test_refresh_token(client_with_db, admin_user):
    r = await client_with_db.post(
        "/api/auth/login",
        json={"email": "admin@swa.co.in", "password": "admin123!"},
    )
    refresh = r.json()["refresh_token"]
    r2 = await client_with_db.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert r2.status_code == 200
    assert "access_token" in r2.json()


async def test_logout_revokes_refresh(client_with_db, admin_user):
    r = await client_with_db.post(
        "/api/auth/login",
        json={"email": "admin@swa.co.in", "password": "admin123!"},
    )
    access = r.json()["access_token"]
    refresh = r.json()["refresh_token"]
    await client_with_db.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access}"},
    )
    r2 = await client_with_db.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert r2.status_code == 401


async def test_audit_log_on_login(client_with_db, admin_user, db_session):
    await client_with_db.post(
        "/api/auth/login",
        json={"email": "admin@swa.co.in", "password": "admin123!"},
    )
    rows = db_session.execute(
        text("SELECT * FROM audit_log WHERE action = 'auth.login_success'")
    ).fetchall()
    assert len(rows) >= 1


def test_role_hierarchy():
    assert role_includes(Role.ADMIN, Role.VIEWER)
    assert role_includes(Role.PM, Role.DESIGNER)
    assert not role_includes(Role.VIEWER, Role.ADMIN)
    assert not role_includes(Role.DESIGNER, Role.PM)


def test_expired_token_rejected():
    past = datetime.now(UTC) - timedelta(hours=1)
    payload = {
        "sub": str(uuid.uuid4()),
        "role": "admin",
        "iat": int(past.timestamp()),
        "exp": int(past.timestamp()),
        "type": "access",
    }
    expired = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    with pytest.raises(jwt.JWTError):
        decode_token(expired)
