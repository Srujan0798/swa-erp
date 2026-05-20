# Task 02 — Projects API

## What to do
Implement the full Projects API. Projects belong to a client, have a lifecycle status, and can be assigned to a PM, designer, and auditor. Soft-delete only.

## Files to create
- CREATE: `src/backend/models/project.py` (Project model)
- CREATE: `src/backend/schemas/project.py` (ProjectCreate, ProjectUpdate, ProjectRead, ProjectListResponse, ProjectStatus enum)
- CREATE: `src/backend/db/repositories/project_repo.py` (list, get_by_id, create, update, soft_delete, search, filter_by_status)
- CREATE: `src/backend/services/project_service.py` (business logic + audit log)
- CREATE: `src/backend/api/projects.py` (router with all endpoints)
- CREATE: `src/backend/alembic/versions/0003_add_projects.py`
- CREATE: `tests/wave-2/test_projects.py`

## Files to modify
- MODIFY: `src/backend/models/__init__.py` — import Project
- MODIFY: `src/backend/api/__init__.py` — export projects router
- MODIFY: `src/backend/main.py` — include projects router

## Files you must NOT touch
- `src/backend/api/auth.py`, `src/backend/api/users.py`, `src/backend/api/clients.py` (existing)
- `src/frontend/` (other tasks)

## The core problem (inline)

### ProjectStatus enum (`schemas/project.py`)
```python
from enum import Enum

class ProjectStatus(str, Enum):
    LEAD = "Lead"
    QUOTE = "Quote"
    AWARDED = "Awarded"
    DESIGN = "Design"
    VENDOR = "Vendor"
    EXECUTION = "Execution"
    VALIDATION = "Validation"
    CLOSED = "Closed"
```

### Project model (`models/project.py`)
```python
import uuid
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Text, Numeric, Date, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.backend.db.base import Base

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Lead")
    pm_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    designer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    auditor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estimated_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    actual_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    start_date: Mapped["date | None"] = mapped_column(Date, nullable=True)
    target_end_date: Mapped["date | None"] = mapped_column(Date, nullable=True)
    actual_end_date: Mapped["date | None"] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped["datetime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
```

### Schemas (`schemas/project.py`)
```python
class ProjectCreate(BaseModel):
    client_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    description: str | None = None
    status: ProjectStatus = ProjectStatus.LEAD
    pm_id: uuid.UUID | None = None
    designer_id: uuid.UUID | None = None
    auditor_id: uuid.UUID | None = None
    location: str | None = Field(default=None, max_length=255)
    estimated_value: Decimal | None = None
    start_date: date | None = None
    target_end_date: date | None = None

class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    status: ProjectStatus | None = None
    pm_id: uuid.UUID | None = None
    designer_id: uuid.UUID | None = None
    auditor_id: uuid.UUID | None = None
    location: str | None = Field(default=None, max_length=255)
    estimated_value: Decimal | None = None
    actual_value: Decimal | None = None
    start_date: date | None = None
    target_end_date: date | None = None
    actual_end_date: date | None = None
    is_active: bool | None = None

class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    code: str
    description: str | None
    status: ProjectStatus
    pm_id: uuid.UUID | None
    designer_id: uuid.UUID | None
    auditor_id: uuid.UUID | None
    location: str | None
    estimated_value: Decimal | None
    actual_value: Decimal | None
    start_date: date | None
    target_end_date: date | None
    actual_end_date: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # Nested read-only fields (populated by service)
    client_name: str | None = None
    pm_name: str | None = None
    designer_name: str | None = None
    auditor_name: str | None = None

class ProjectListResponse(BaseModel):
    items: list[ProjectRead]
    total: int
    page: int
    page_size: int
```

### Endpoints (`api/projects.py`)

| Method | Path | Auth | Returns |
|---|---|---|---|
| GET | `/api/projects` | admin/pm | ProjectListResponse (paginated, q, status filter) |
| POST | `/api/projects` | admin/pm | ProjectRead (201) |
| GET | `/api/projects/{id}` | any authenticated | ProjectRead |
| PATCH | `/api/projects/{id}` | admin/pm | ProjectRead |
| DELETE | `/api/projects/{id}` | admin | 204 soft-delete |

Rules:
- `code` must be unique. Handle IntegrityError → 409.
- Search `q` matches `name` OR `code` OR `location` (ILIKE).
- Filter `status` accepts a single status string (e.g., `?status=Lead`).
- Lists exclude soft-deleted projects.
- `ProjectRead` should include `client_name`, `pm_name`, `designer_name`, `auditor_name` (joined in service/repo).
- Audit log: `project.create`, `project.update`, `project.delete` with before/after JSON.

### Tests (`tests/wave-2/test_projects.py`)

```python
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_create_project(authed_admin_client, db_session):
    # Create a client first
    r = await authed_admin_client.post("/api/clients", json={
        "name": "ProjectClient", "code": "PC-001", "primary_email": "pc@example.com"
    })
    client_id = r.json()["id"]
    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(client_id),
        "name": "Insulation Audit",
        "code": "PRJ-001",
        "status": "Lead",
    })
    assert r2.status_code == 201
    body = r2.json()
    assert body["code"] == "PRJ-001"
    assert body["status"] == "Lead"
    assert body["client_name"] == "ProjectClient"

async def test_duplicate_project_code(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "DupClient", "code": "DC-001", "primary_email": "dc@example.com"
    })
    cid = r.json()["id"]
    await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "A", "code": "DUP-PRJ", "status": "Lead"
    })
    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "B", "code": "DUP-PRJ", "status": "Lead"
    })
    assert r2.status_code == 409

async def test_filter_by_status(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "FilterClient", "code": "FC-001", "primary_email": "fc@example.com"
    })
    cid = r.json()["id"]
    await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "LeadProj", "code": "FL-001", "status": "Lead"
    })
    await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "AwardedProj", "code": "FA-001", "status": "Awarded"
    })
    r = await authed_admin_client.get("/api/projects?status=Lead")
    assert r.status_code == 200
    assert all(p["status"] == "Lead" for p in r.json()["items"])

async def test_search_projects(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "SearchClient", "code": "SC-001", "primary_email": "sc@example.com"
    })
    cid = r.json()["id"]
    await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "Searchable Project", "code": "FS-001", "status": "Lead"
    })
    r = await authed_admin_client.get("/api/projects?q=Searchable")
    assert r.status_code == 200
    assert len(r.json()["items"]) >= 1

async def test_soft_delete_project(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "DelProjClient", "code": "DPC-001", "primary_email": "dpc@example.com"
    })
    cid = r.json()["id"]
    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "DelProj", "code": "FD-001", "status": "Lead"
    })
    pid = r2.json()["id"]
    r3 = await authed_admin_client.delete(f"/api/projects/{pid}")
    assert r3.status_code == 204
    r4 = await authed_admin_client.get("/api/projects")
    codes = [p["code"] for p in r4.json()["items"]]
    assert "FD-001" not in codes

async def test_assign_pm_to_project(authed_admin_client, admin_user, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "AssignClient", "code": "AC-001", "primary_email": "ac@example.com"
    })
    cid = r.json()["id"]
    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "AssignProj", "code": "FA-001", "status": "Lead",
        "pm_id": str(admin_user.id)
    })
    assert r2.status_code == 201
    assert r2.json()["pm_id"] == str(admin_user.id)
```

**Note:** For tests, you need a client in the DB first. Create clients via `/api/clients` in your test fixtures or setup.

## Acceptance criteria (executable)
- [ ] `pytest tests/wave-2/test_projects.py -v` → all pass
- [ ] `ruff check src/backend/` → clean
- [ ] `black --check src/backend/` → clean
- [ ] `mypy src/backend/` → no errors
- [ ] `alembic upgrade head` applies cleanly
- [ ] Manual: create client → create project → assign PM → search by status

## How to deliver
1. Implement all files
2. Run acceptance commands
3. Write report to `work/reports/wave-2/02-projects-api.report.md`
4. Stop

## Constraints
- Time budget: 90 min
- Use `Decimal(18,2)` for estimated_value and actual_value
- Use `Date` (not DateTime) for start_date, target_end_date, actual_end_date
- Project code must be unique
- Do NOT create frontend files
