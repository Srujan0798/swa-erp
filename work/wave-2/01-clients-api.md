# Task 01 — Clients API + Contacts

## What to do
Implement the full Clients API with contacts. A client represents a company/organization. Each client has one or more contacts (people). Soft-delete only.

## Files to create
- CREATE: `src/backend/models/client.py` (Client model)
- CREATE: `src/backend/models/contact.py` (Contact model)
- CREATE: `src/backend/schemas/client.py` (ClientCreate, ClientUpdate, ClientRead, ClientListResponse)
- CREATE: `src/backend/schemas/contact.py` (ContactCreate, ContactUpdate, ContactRead)
- CREATE: `src/backend/db/repositories/client_repo.py` (list, get_by_id, create, update, soft_delete, search)
- CREATE: `src/backend/db/repositories/contact_repo.py` (create, update, delete, list_by_client)
- CREATE: `src/backend/services/client_service.py` (business logic + audit log)
- CREATE: `src/backend/services/contact_service.py` (business logic)
- CREATE: `src/backend/api/clients.py` (router with all endpoints)
- CREATE: `src/backend/alembic/versions/0002_add_clients_and_contacts.py`
- CREATE: `tests/wave-2/test_clients.py`

## Files to modify
- MODIFY: `src/backend/models/__init__.py` — import Client, Contact
- MODIFY: `src/backend/api/__init__.py` — export clients router
- MODIFY: `src/backend/main.py` — include clients router
- MODIFY: `src/backend/db/repositories/__init__.py` — export if needed
- MODIFY: `src/backend/services/__init__.py` — export if needed
- MODIFY: `src/backend/schemas/__init__.py` — export if needed

## Files you must NOT touch
- `src/backend/api/auth.py`, `src/backend/api/users.py` (existing auth)
- `src/backend/models/user.py` (existing)
- `src/frontend/` (other tasks)

## The core problem (inline)

### Client model (`models/client.py`)
```python
import uuid
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.backend.db.base import Base

class Client(Base):
    __tablename__ = "clients"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="India")
    gst_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    primary_email: Mapped[str] = mapped_column(String(320), nullable=False)
    primary_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped["datetime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
```

### Contact model (`models/contact.py`)
```python
class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
```

### Schemas (`schemas/client.py`)
```python
class ClientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    country: str = "India"
    gst_number: str | None = Field(default=None, max_length=50)
    primary_email: EmailStr
    primary_phone: str | None = Field(default=None, max_length=50)
    notes: str | None = None
    contacts: list[ContactCreate] = Field(default_factory=list)

class ClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    country: str | None = None
    gst_number: str | None = Field(default=None, max_length=50)
    primary_email: EmailStr | None = None
    primary_phone: str | None = Field(default=None, max_length=50)
    notes: str | None = None
    is_active: bool | None = None

class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    code: str
    address: str | None
    city: str | None
    state: str | None
    pincode: str | None
    country: str
    gst_number: str | None
    primary_email: str
    primary_phone: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    contacts: list[ContactRead] = []

class ClientListResponse(BaseModel):
    items: list[ClientRead]
    total: int
    page: int
    page_size: int
```

### Endpoints (`api/clients.py`)

| Method | Path | Auth | Returns |
|---|---|---|---|
| GET | `/api/clients` | admin/pm | ClientListResponse (paginated, q=name/code/email) |
| POST | `/api/clients` | admin/pm | ClientRead (201) |
| GET | `/api/clients/{id}` | any authenticated | ClientRead with contacts |
| PATCH | `/api/clients/{id}` | admin/pm | ClientRead |
| DELETE | `/api/clients/{id}` | admin | 204 soft-delete |
| POST | `/api/clients/{id}/contacts` | admin/pm | ContactRead (201) |
| PATCH | `/api/clients/{id}/contacts/{contact_id}` | admin/pm | ContactRead |
| DELETE | `/api/clients/{id}/contacts/{contact_id}` | admin/pm | 204 |

Rules:
- `code` must be unique. Handle IntegrityError → 409.
- Search `q` matches `name` OR `code` OR `primary_email` (ILIKE).
- Lists exclude soft-deleted clients.
- GET `/api/clients/{id}` includes contacts where `client_id = id`.
- Audit log: `client.create`, `client.update`, `client.delete`, `contact.create`, `contact.update`, `contact.delete`.

### Tests (`tests/wave-2/test_clients.py`)

```python
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_admin_can_create_client(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "ACME Corp",
        "code": "ACME-001",
        "primary_email": "acme@example.com",
        "contacts": [{"name": "John", "email": "john@example.com", "is_primary": True}],
    })
    assert r.status_code == 201
    body = r.json()
    assert body["code"] == "ACME-001"
    assert len(body["contacts"]) == 1

async def test_duplicate_code_returns_409(authed_admin_client):
    await authed_admin_client.post("/api/clients", json={
        "name": "ACME", "code": "DUP-001", "primary_email": "a@example.com"
    })
    r = await authed_admin_client.post("/api/clients", json={
        "name": "Other", "code": "DUP-001", "primary_email": "b@example.com"
    })
    assert r.status_code == 409

async def test_search_clients(authed_admin_client):
    await authed_admin_client.post("/api/clients", json={
        "name": "SearchMe", "code": "SRCH-001", "primary_email": "s@example.com"
    })
    r = await authed_admin_client.get("/api/clients?q=SearchMe")
    assert r.status_code == 200
    assert len(r.json()["items"]) >= 1

async def test_soft_delete_client(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "DelMe", "code": "DEL-001", "primary_email": "d@example.com"
    })
    cid = r.json()["id"]
    r2 = await authed_admin_client.delete(f"/api/clients/{cid}")
    assert r2.status_code == 204
    r3 = await authed_admin_client.get("/api/clients")
    codes = [c["code"] for c in r3.json()["items"]]
    assert "DEL-001" not in codes

async def test_add_contact_to_client(authed_admin_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "ContactTest", "code": "CT-001", "primary_email": "ct@example.com"
    })
    cid = r.json()["id"]
    r2 = await authed_admin_client.post(f"/api/clients/{cid}/contacts", json={
        "name": "Jane", "email": "jane@example.com"
    })
    assert r2.status_code == 201
    r3 = await authed_admin_client.get(f"/api/clients/{cid}")
    assert len(r3.json()["contacts"]) == 1

async def test_viewer_can_read_client(authed_admin_client, authed_viewer_client):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "ViewerTest", "code": "VT-001", "primary_email": "vt@example.com"
    })
    cid = r.json()["id"]
    r2 = await authed_viewer_client.get(f"/api/clients/{cid}")
    assert r2.status_code == 200

async def test_pm_can_create_client(authed_pm_client):
    r = await authed_pm_client.post("/api/clients", json={
        "name": "PMClient", "code": "PM-001", "primary_email": "pmc@example.com"
    })
    assert r.status_code == 201

async def test_viewer_cannot_create_client(authed_viewer_client):
    r = await authed_viewer_client.post("/api/clients", json={
        "name": "X", "code": "X-001", "primary_email": "x@example.com"
    })
    assert r.status_code == 403
```

Add the `authed_viewer_client` fixture to `tests/wave-1/conftest.py` if needed (or include it inline in your test file).

## Acceptance criteria (executable)
- [ ] `pytest tests/wave-2/test_clients.py -v` → all pass
- [ ] `ruff check src/backend/` → clean
- [ ] `black --check src/backend/` → clean
- [ ] `mypy src/backend/` → no errors
- [ ] `alembic upgrade head` applies cleanly
- [ ] Manual: `curl` create client → get client with contacts → delete client

## How to deliver
1. Implement all files
2. Run acceptance commands
3. Write report to `work/reports/wave-2/01-clients-api.report.md`
4. Stop

## Constraints
- Time budget: 90 min
- Use Decimal(18,2) only for money (not in this task)
- Do NOT create frontend files
- Match existing patterns: router → service → repo → model → schema
