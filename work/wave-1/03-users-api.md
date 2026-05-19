# Task 03 — Users API

## What to do
Implement CRUD endpoints for users (admin-only for list/create/delete; self-or-admin for read/update). Every mutation must create an audit log entry. Soft-delete only.

Reference spec: `.specify/specs/wave-1/spec.md` — US-1.2, US-1.4; API surface `/api/users/*`.

## Files to create
- CREATE: `src/backend/schemas/user.py` (UserCreate, UserUpdate, UserRead, UserListResponse)
- CREATE: `src/backend/schemas/common.py` (Pagination, ErrorResponse)
- CREATE: `src/backend/services/user_service.py` (list_users, create_user, get_user, update_user, soft_delete_user)
- CREATE: `src/backend/db/repositories/user_repo.py` (UPDATE: extend if exists with list/create/update/soft_delete)
- CREATE: `src/backend/api/users.py` (GET, POST, GET/:id, PATCH/:id, DELETE/:id)
- CREATE: `tests/wave-1/test_users.py` (test cases below)

## Files to modify
- MODIFY: `src/backend/main.py` (include users router)
- MODIFY: `src/backend/api/__init__.py` (export users router)

## Files you must NOT touch
- `src/backend/api/auth.py` (Task 02 — call its dependencies via core/deps.py)
- `src/backend/models/` (already created in Task 01)
- `src/frontend/` (Task 04)
- `Dockerfile`, `docker-compose.yml`, `.github/workflows/` (Task 05)

## Skills to use
- `tdd`
- `fastapi-patterns` (dependency injection, path/query params)
- `pydantic-v2` (UserCreate validates email, password length ≥ 8)
- `sqlalchemy-orm` (filters, soft-delete, pagination)
- `code-review`

## The core problem (inline)

### Schemas (`schemas/user.py`)
```python
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from src.backend.core.roles import Role

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: Role

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    role: Role | None = None
    is_active: bool | None = None

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr
    name: str
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserListResponse(BaseModel):
    items: list[UserRead]
    total: int
    page: int
    page_size: int
```

### Common (`schemas/common.py`)
```python
from pydantic import BaseModel

class Pagination(BaseModel):
    page: int = 1
    page_size: int = 20

class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
```

### Endpoints (`api/users.py`)

| Method | Path | Auth | Returns |
|---|---|---|---|
| GET | `/api/users` | admin | UserListResponse (paginated, filters: q, role, is_active) |
| POST | `/api/users` | admin | UserRead (201) |
| GET | `/api/users/{id}` | admin OR self | UserRead |
| PATCH | `/api/users/{id}` | admin OR self (self cannot change own role/is_active) | UserRead |
| DELETE | `/api/users/{id}` | admin (not allowed on self) | 204 |

- Pagination defaults: page=1, page_size=20, max page_size=100
- Search query `q` matches email OR name (ILIKE)
- Soft-delete sets `deleted_at`; lists exclude soft-deleted
- Email uniqueness enforced
- Audit log entries: `user.create`, `user.update`, `user.delete` with before/after JSON

### User service (`services/user_service.py`)
- All mutations transactional
- Audit log written in the SAME transaction as the mutation
- `create_user` hashes password before insert
- `update_user` ignores password (separate endpoint later, not in this task)

### Tests (`tests/wave-1/test_users.py`)

```python
import pytest
from httpx import AsyncClient
from src.backend.core.security import hash_password
from src.backend.models.user import User

pytestmark = pytest.mark.asyncio

# Reuse fixtures from conftest.py: admin_user, pm_user, authed_admin_client, authed_pm_client

async def test_admin_can_list_users(authed_admin_client: AsyncClient, admin_user):
    r = await authed_admin_client.get("/api/users")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert any(u["email"] == "admin@swa.local" for u in body["items"])

async def test_pm_cannot_list_users(authed_pm_client: AsyncClient):
    r = await authed_pm_client.get("/api/users")
    assert r.status_code == 403

async def test_admin_can_create_user(authed_admin_client: AsyncClient):
    r = await authed_admin_client.post("/api/users", json={
        "email": "designer@swa.local",
        "name": "Designer",
        "password": "design123!",
        "role": "designer",
    })
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "designer@swa.local"
    assert body["role"] == "designer"
    assert "password" not in body
    assert "password_hash" not in body

async def test_create_user_duplicate_email(authed_admin_client: AsyncClient, admin_user):
    r = await authed_admin_client.post("/api/users", json={
        "email": "admin@swa.local",
        "name": "Dup", "password": "x12345!", "role": "viewer",
    })
    assert r.status_code in (409, 400)

async def test_create_user_short_password(authed_admin_client: AsyncClient):
    r = await authed_admin_client.post("/api/users", json={
        "email": "short@swa.local",
        "name": "Short", "password": "abc", "role": "viewer",
    })
    assert r.status_code == 422

async def test_pm_cannot_create_user(authed_pm_client: AsyncClient):
    r = await authed_pm_client.post("/api/users", json={
        "email": "x@swa.local", "name": "X", "password": "x12345!", "role": "viewer",
    })
    assert r.status_code == 403

async def test_self_can_read_own(authed_pm_client: AsyncClient, pm_user):
    r = await authed_pm_client.get(f"/api/users/{pm_user.id}")
    assert r.status_code == 200

async def test_pm_cannot_read_other(authed_pm_client: AsyncClient, admin_user):
    r = await authed_pm_client.get(f"/api/users/{admin_user.id}")
    assert r.status_code == 403

async def test_self_can_update_own_name(authed_pm_client: AsyncClient, pm_user):
    r = await authed_pm_client.patch(f"/api/users/{pm_user.id}",
        json={"name": "PM Renamed"})
    assert r.status_code == 200
    assert r.json()["name"] == "PM Renamed"

async def test_self_cannot_update_own_role(authed_pm_client: AsyncClient, pm_user):
    r = await authed_pm_client.patch(f"/api/users/{pm_user.id}",
        json={"role": "admin"})
    assert r.status_code == 403

async def test_soft_delete(authed_admin_client: AsyncClient, db_session):
    r = await authed_admin_client.post("/api/users", json={
        "email": "del@swa.local", "name": "Del", "password": "x12345!", "role": "viewer",
    })
    user_id = r.json()["id"]
    r2 = await authed_admin_client.delete(f"/api/users/{user_id}")
    assert r2.status_code == 204
    # Should not appear in list
    r3 = await authed_admin_client.get("/api/users")
    emails = [u["email"] for u in r3.json()["items"]]
    assert "del@swa.local" not in emails
    # But row still in DB
    from src.backend.models.user import User
    row = db_session.query(User).filter_by(email="del@swa.local").first()
    assert row is not None
    assert row.deleted_at is not None

async def test_admin_cannot_delete_self(authed_admin_client: AsyncClient, admin_user):
    r = await authed_admin_client.delete(f"/api/users/{admin_user.id}")
    assert r.status_code == 403

async def test_audit_log_on_create(authed_admin_client: AsyncClient, db_session):
    await authed_admin_client.post("/api/users", json={
        "email": "audit@swa.local", "name": "Audit", "password": "x12345!", "role": "viewer",
    })
    from src.backend.models.audit_log import AuditLog
    rows = db_session.query(AuditLog).filter_by(action="user.create").all()
    assert len(rows) >= 1
    assert rows[-1].after_json["email"] == "audit@swa.local"

async def test_pagination(authed_admin_client: AsyncClient):
    # Create 25 users
    for i in range(25):
        await authed_admin_client.post("/api/users", json={
            "email": f"page{i}@swa.local", "name": f"P{i}", "password": "x12345!", "role": "viewer",
        })
    r = await authed_admin_client.get("/api/users?page=1&page_size=10")
    assert r.json()["page"] == 1
    assert len(r.json()["items"]) == 10
    r2 = await authed_admin_client.get("/api/users?page=3&page_size=10")
    assert r2.json()["page"] == 3
```

## Acceptance criteria (executable)
- [ ] `pytest tests/wave-1/test_users.py -v` → all pass
- [ ] `ruff check src/backend/` → clean
- [ ] `mypy src/backend/` → no errors
- [ ] All endpoints return JSON matching the schemas (no leaked password_hash, no extra fields)
- [ ] Audit log entries exist after create/update/delete

## How to deliver
1. Implement files
2. Run acceptance commands
3. Write report to `work/reports/wave-1/03-users-api.report.md`
4. Stop

## Constraints
- Time budget: 90 min
- No new packages beyond what Task 02 added
- Pagination via SQL OFFSET/LIMIT (fine for wave-1 scale; revisit in wave-5+)
- Email uniqueness via DB constraint (handle IntegrityError → 409)
