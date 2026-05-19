# Task 02 — Auth + RBAC

## What to do
Implement JWT-based authentication with bcrypt password hashing, role-based access control (5 roles), and the auth endpoints: login, refresh, logout, /me. Add audit log entries for all auth events.

Reference spec: `.specify/specs/wave-1/spec.md` — US-1.1, US-1.4, US-1.5; API surface `/api/auth/*`.

## Files to create
- CREATE: `src/backend/core/security.py` (password hashing, JWT encode/decode)
- CREATE: `src/backend/core/roles.py` (Role enum, permission matrix)
- CREATE: `src/backend/core/deps.py` (`get_current_user`, `require_role`, `require_active_user`)
- CREATE: `src/backend/schemas/__init__.py`
- CREATE: `src/backend/schemas/auth.py` (LoginRequest, TokenResponse, RefreshRequest, UserPublic)
- CREATE: `src/backend/services/__init__.py`
- CREATE: `src/backend/services/auth_service.py` (login, refresh, logout, decode token)
- CREATE: `src/backend/services/audit_service.py` (record_event)
- CREATE: `src/backend/db/repositories/__init__.py`
- CREATE: `src/backend/db/repositories/user_repo.py` (get_by_email, get_by_id)
- CREATE: `src/backend/db/repositories/refresh_token_repo.py` (create, revoke, find_valid)
- CREATE: `src/backend/db/repositories/audit_repo.py` (create_entry)
- CREATE: `src/backend/api/auth.py` (POST /api/auth/login, /refresh, /logout, GET /api/auth/me)
- CREATE: `tests/wave-1/test_auth.py` (test cases below)

## Files to modify
- MODIFY: `src/backend/main.py` (include auth router)
- MODIFY: `src/backend/api/__init__.py` (export auth router)

## Files you must NOT touch
- `src/backend/api/users.py` (Task 03)
- `src/frontend/` (Task 04)
- Models in `src/backend/models/` (already created in Task 01)
- Alembic migration `0001_initial.py` (DO NOT EDIT — create a new one if needed)

## Skills to use
- `tdd` (write the test cases below FIRST, then implement)
- `fastapi-patterns` (dependencies, security utilities)
- `pydantic-v2` (request/response schemas)
- `jwt-handling` (encode/decode, expiry, claims)
- `code-review` (self-review before submit)

## The core problem (inline)

### Roles + permission matrix (`core/roles.py`)
```python
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    PM = "pm"
    DESIGNER = "designer"
    AUDITOR = "auditor"
    VIEWER = "viewer"

ROLE_HIERARCHY = {
    Role.ADMIN: {Role.ADMIN, Role.PM, Role.DESIGNER, Role.AUDITOR, Role.VIEWER},
    Role.PM: {Role.PM, Role.DESIGNER, Role.AUDITOR, Role.VIEWER},
    Role.DESIGNER: {Role.DESIGNER, Role.VIEWER},
    Role.AUDITOR: {Role.AUDITOR, Role.VIEWER},
    Role.VIEWER: {Role.VIEWER},
}

def role_includes(user_role: Role, required: Role) -> bool:
    return required in ROLE_HIERARCHY.get(user_role, set())
```

### Security (`core/security.py`)
```python
from datetime import datetime, timedelta, timezone
import uuid
from passlib.context import CryptContext
from jose import jwt, JWTError
from src.backend.core.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_access_token(user_id: uuid.UUID, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_ACCESS_TTL_MIN)).timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
```

### Dependencies (`core/deps.py`)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.backend.db.session import get_db
from src.backend.core.security import decode_token
from src.backend.core.roles import Role, role_includes
from src.backend.db.repositories.user_repo import get_by_id

security_scheme = HTTPBearer()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = decode_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Wrong token type")
    user = get_by_id(db, uuid.UUID(payload["sub"]))
    if not user or not user.is_active or user.deleted_at:
        raise HTTPException(status_code=401, detail="User not active")
    return user

def require_role(required: Role):
    def _checker(user = Depends(get_current_user)):
        if not role_includes(Role(user.role), required):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return _checker
```

### Auth endpoints (`api/auth.py`)

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/auth/login` | `{email, password}` | `{access_token, refresh_token, user: {id, email, name, role}}` |
| POST | `/api/auth/refresh` | `{refresh_token}` | `{access_token}` |
| POST | `/api/auth/logout` | (bearer auth) | `{message}` (revokes refresh token) |
| GET  | `/api/auth/me` | (bearer auth) | `{id, email, name, role}` |

- Login: lookup user by email, verify bcrypt, issue access + refresh tokens, store refresh hash in DB.
- Refresh: verify refresh token hash exists and not revoked, not expired, issue new access token (do NOT rotate refresh in MVP).
- Logout: revoke the current session's refresh token (set `revoked_at`).
- /me: return current user public fields.

### Audit log
Every auth event (login_success, login_fail, logout, token_refresh) → `audit_service.record_event(...)`.

### Tests (`tests/wave-1/test_auth.py`)

```python
import pytest
from httpx import AsyncClient
from src.backend.core.security import hash_password
from src.backend.models.user import User

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def admin_user(db_session):
    u = User(email="admin@swa.local", name="Admin",
             password_hash=hash_password("admin123!"), role="admin")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u

@pytest.fixture
async def pm_user(db_session):
    u = User(email="pm@swa.local", name="PM",
             password_hash=hash_password("pm123!"), role="pm")
    db_session.add(u); db_session.commit(); db_session.refresh(u)
    return u

async def test_login_success(client: AsyncClient, admin_user):
    r = await client.post("/api/auth/login",
        json={"email": "admin@swa.local", "password": "admin123!"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["user"]["email"] == "admin@swa.local"
    assert body["user"]["role"] == "admin"

async def test_login_wrong_password(client: AsyncClient, admin_user):
    r = await client.post("/api/auth/login",
        json={"email": "admin@swa.local", "password": "wrong"})
    assert r.status_code == 401

async def test_login_unknown_email(client: AsyncClient):
    r = await client.post("/api/auth/login",
        json={"email": "nope@swa.local", "password": "x"})
    assert r.status_code == 401

async def test_me_requires_bearer(client: AsyncClient):
    r = await client.get("/api/auth/me")
    assert r.status_code in (401, 403)  # depending on HTTPBearer behavior

async def test_me_with_valid_token(client: AsyncClient, admin_user):
    r = await client.post("/api/auth/login",
        json={"email": "admin@swa.local", "password": "admin123!"})
    token = r.json()["access_token"]
    r2 = await client.get("/api/auth/me",
        headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["email"] == "admin@swa.local"

async def test_refresh_token(client: AsyncClient, admin_user):
    r = await client.post("/api/auth/login",
        json={"email": "admin@swa.local", "password": "admin123!"})
    refresh = r.json()["refresh_token"]
    r2 = await client.post("/api/auth/refresh",
        json={"refresh_token": refresh})
    assert r2.status_code == 200
    assert "access_token" in r2.json()

async def test_logout_revokes_refresh(client: AsyncClient, admin_user):
    r = await client.post("/api/auth/login",
        json={"email": "admin@swa.local", "password": "admin123!"})
    access = r.json()["access_token"]
    refresh = r.json()["refresh_token"]
    await client.post("/api/auth/logout",
        headers={"Authorization": f"Bearer {access}"})
    # After logout, refresh should fail
    r2 = await client.post("/api/auth/refresh",
        json={"refresh_token": refresh})
    assert r2.status_code == 401

async def test_audit_log_on_login(client: AsyncClient, admin_user, db_session):
    await client.post("/api/auth/login",
        json={"email": "admin@swa.local", "password": "admin123!"})
    from src.backend.models.audit_log import AuditLog
    rows = db_session.query(AuditLog).filter(AuditLog.action == "auth.login_success").all()
    assert len(rows) >= 1

async def test_role_hierarchy():
    from src.backend.core.roles import Role, role_includes
    assert role_includes(Role.ADMIN, Role.VIEWER)
    assert role_includes(Role.PM, Role.DESIGNER)
    assert not role_includes(Role.VIEWER, Role.ADMIN)
    assert not role_includes(Role.DESIGNER, Role.PM)
```

## Acceptance criteria (executable)
- [ ] `pytest tests/wave-1/test_auth.py -v` → all pass
- [ ] `ruff check src/backend/` → clean
- [ ] `mypy src/backend/` → no errors
- [ ] Manual: `curl -X POST http://localhost:8000/api/auth/login -d '{"email":"admin@swa.local","password":"admin123!"}' -H "Content-Type: application/json"` returns tokens
- [ ] Manual: `curl http://localhost:8000/api/auth/me -H "Authorization: Bearer <token>"` returns user info
- [ ] JWT decode rejects expired tokens (write a unit test that mints a token with past `exp` and expects 401)

## How to deliver
1. Implement files (TDD: write tests first if you prefer)
2. Run acceptance commands
3. Write report to `work/reports/wave-1/02-auth-rbac.report.md`
4. Stop

## Constraints
- Time budget: 90 min
- No new packages beyond: `python-jose[cryptography]`, `passlib[bcrypt]` (already in requirements per plan.md)
- All passwords must be bcrypt cost 12
- JWT must be HS256 with `SECRET_KEY` from settings
- Access token TTL 60 min, refresh token TTL 30 days (per settings)
