# Task 03 — Project Lifecycle + Stats Service

## What to do
Implement the project lifecycle state machine, transition validation, and dashboard stats endpoint. This task builds on the Project model from Task 02 — it adds business logic, NOT new models (except an Alembic migration if you need to add an index).

## Files to create
- CREATE: `src/backend/core/lifecycle.py` (ProjectStatus enum, ALLOWED_TRANSITIONS, transition validation)
- CREATE: `src/backend/services/lifecycle_service.py` (transition logic + audit log + side effects)
- CREATE: `src/backend/api/lifecycle.py` (router: POST /api/projects/{id}/transition, GET /api/projects/stats)
- CREATE: `tests/wave-2/test_lifecycle.py`
- CREATE: `tests/wave-2/test_stats.py`

## Files to modify
- MODIFY: `src/backend/api/__init__.py` — export lifecycle router
- MODIFY: `src/backend/main.py` — include lifecycle router
- MODIFY: `src/backend/api/projects.py` — optionally add `PATCH /api/projects/{id}` status validation (reject direct status changes that bypass lifecycle rules)

## Files you must NOT touch
- `src/backend/models/project.py` (created in Task 02 — read-only for you)
- `src/frontend/` (other tasks)

## The core problem (inline)

### Lifecycle states
```
Lead ──→ Quote ──→ Awarded ──→ Design ──→ Vendor ──→ Execution ──→ Validation ──→ Closed
```

### Allowed transitions (`core/lifecycle.py`)
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

ALLOWED_TRANSITIONS = {
    ProjectStatus.LEAD: {ProjectStatus.QUOTE},
    ProjectStatus.QUOTE: {ProjectStatus.LEAD, ProjectStatus.AWARDED},
    ProjectStatus.AWARDED: {ProjectStatus.DESIGN, ProjectStatus.QUOTE},
    ProjectStatus.DESIGN: {ProjectStatus.VENDOR, ProjectStatus.AWARDED},
    ProjectStatus.VENDOR: {ProjectStatus.EXECUTION, ProjectStatus.DESIGN},
    ProjectStatus.EXECUTION: {ProjectStatus.VALIDATION, ProjectStatus.VENDOR},
    ProjectStatus.VALIDATION: {ProjectStatus.CLOSED, ProjectStatus.EXECUTION},
    ProjectStatus.CLOSED: set(),  # terminal
}

def can_transition(from_status: ProjectStatus, to_status: ProjectStatus) -> bool:
    return to_status in ALLOWED_TRANSITIONS.get(from_status, set())
```

### Transition service (`services/lifecycle_service.py`)
```python
def transition_project(
    db: Session,
    project_id: uuid.UUID,
    to_status: ProjectStatus,
    actor_id: uuid.UUID,
    reason: str | None = None,
) -> Project:
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if project.deleted_at:
        raise HTTPException(404, "Project not found")

    current = ProjectStatus(project.status)
    if not can_transition(current, to_status):
        raise HTTPException(400, f"Cannot transition from {current.value} to {to_status.value}")

    before_json = {"status": project.status}
    project.status = to_status.value

    # Side effects
    if to_status == ProjectStatus.CLOSED:
        from datetime import date
        project.actual_end_date = date.today()
    if to_status == ProjectStatus.EXECUTION and not project.start_date:
        from datetime import date
        project.start_date = date.today()

    db.commit()
    db.refresh(project)

    after_json = {"status": project.status}
    if project.actual_end_date:
        after_json["actual_end_date"] = str(project.actual_end_date)
    if project.start_date:
        after_json["start_date"] = str(project.start_date)

    create_entry(
        db,
        action="project.transition",
        entity_type="project",
        entity_id=project.id,
        user_id=actor_id,
        before_json=before_json,
        after_json=after_json,
    )

    return project
```

### Stats endpoint (`api/lifecycle.py`)
```python
@router.get("/api/projects/stats")
def project_stats(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # Return counts by status + total active + total value
    from sqlalchemy import func
    from src.backend.models.project import Project

    query = db.query(Project.status, func.count(Project.id)).filter(
        Project.deleted_at.is_(None), Project.is_active == True
    ).group_by(Project.status)

    status_counts = {status: 0 for status in ProjectStatus}
    for status, count in query.all():
        status_counts[status] = count

    total_active = sum(status_counts.values())
    total_estimated = db.query(func.sum(Project.estimated_value)).filter(
        Project.deleted_at.is_(None), Project.is_active == True
    ).scalar() or 0

    return {
        "total_active": total_active,
        "by_status": status_counts,
        "total_estimated_value": float(total_estimated),
    }
```

### Transition endpoint (`api/lifecycle.py`)
```python
class TransitionRequest(BaseModel):
    to_status: ProjectStatus
    reason: str | None = None

@router.post("/api/projects/{project_id}/transition", response_model=ProjectRead)
def transition(
    project_id: uuid.UUID,
    body: TransitionRequest,
    db: Session = Depends(get_db),
    user = Depends(require_role(Role.PM)),
):
    project = transition_project(db, project_id, body.to_status, user.id, body.reason)
    return ProjectRead.model_validate(project)
```

**IMPORTANT:** Also modify `api/projects.py` `PATCH` endpoint to REJECT direct `status` changes. If `body.status` is provided in a PATCH, return 400 with message "Use /api/projects/{id}/transition to change status."

### Tests (`tests/wave-2/test_lifecycle.py`)

```python
import pytest
from httpx import AsyncClient
from src.backend.core.lifecycle import ProjectStatus, can_transition

pytestmark = pytest.mark.asyncio

async def test_allowed_transitions():
    assert can_transition(ProjectStatus.LEAD, ProjectStatus.QUOTE)
    assert can_transition(ProjectStatus.QUOTE, ProjectStatus.AWARDED)
    assert not can_transition(ProjectStatus.LEAD, ProjectStatus.CLOSED)
    assert not can_transition(ProjectStatus.CLOSED, ProjectStatus.LEAD)

async def test_transition_lead_to_quote(authed_admin_client, db_session):
    # Setup: create client + project
    r = await authed_admin_client.post("/api/clients", json={
        "name": "LifecycleClient", "code": "LC-001", "primary_email": "lc@example.com"
    })
    cid = r.json()["id"]
    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "LifecycleProj", "code": "TL-001", "status": "Lead"
    })
    pid = r2.json()["id"]
    r3 = await authed_admin_client.post(f"/api/projects/{pid}/transition", json={
        "to_status": "Quote"
    })
    assert r3.status_code == 200
    assert r3.json()["status"] == "Quote"

async def test_invalid_transition_returns_400(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "BadClient", "code": "BC-001", "primary_email": "bc@example.com"
    })
    cid = r.json()["id"]
    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "BadProj", "code": "TB-001", "status": "Lead"
    })
    pid = r2.json()["id"]
    r3 = await authed_admin_client.post(f"/api/projects/{pid}/transition", json={
        "to_status": "Closed"
    })
    assert r3.status_code == 400

async def test_direct_status_patch_rejected(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "PatchClient", "code": "PC-002", "primary_email": "pc2@example.com"
    })
    cid = r.json()["id"]
    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "PatchProj", "code": "TP-001", "status": "Lead"
    })
    pid = r2.json()["id"]
    r3 = await authed_admin_client.patch(f"/api/projects/{pid}", json={"status": "Quote"})
    assert r3.status_code == 400

async def test_closed_sets_actual_end_date(authed_admin_client, db_session):
    r = await authed_admin_client.post("/api/clients", json={
        "name": "CloseClient", "code": "CC-001", "primary_email": "cc@example.com"
    })
    cid = r.json()["id"]
    # Create project and advance through all statuses
    r2 = await authed_admin_client.post("/api/projects", json={
        "client_id": str(cid), "name": "CloseProj", "code": "TC-001", "status": "Lead"
    })
    pid = r2.json()["id"]
    for s in ["Quote", "Awarded", "Design", "Vendor", "Execution", "Validation"]:
        await authed_admin_client.post(f"/api/projects/{pid}/transition", json={"to_status": s})
    r3 = await authed_admin_client.post(f"/api/projects/{pid}/transition", json={"to_status": "Closed"})
    assert r3.status_code == 200
    assert r3.json()["actual_end_date"] is not None
```

### Stats tests (`tests/wave-2/test_stats.py`)

```python
import pytest
pytestmark = pytest.mark.asyncio

async def test_project_stats(authed_admin_client, db_session):
    r = await authed_admin_client.get("/api/projects/stats")
    assert r.status_code == 200
    body = r.json()
    assert "total_active" in body
    assert "by_status" in body
    assert "total_estimated_value" in body
    assert isinstance(body["by_status"], dict)
```

## Acceptance criteria (executable)
- [ ] `pytest tests/wave-2/test_lifecycle.py -v` → all pass
- [ ] `pytest tests/wave-2/test_stats.py -v` → all pass
- [ ] `ruff check src/backend/` → clean
- [ ] `black --check src/backend/` → clean
- [ ] `mypy src/backend/` → no errors
- [ ] PATCH /api/projects/{id} with status returns 400
- [ ] POST /api/projects/{id}/transition with valid move returns 200
- [ ] POST /api/projects/{id}/transition with invalid move returns 400
- [ ] GET /api/projects/stats returns counts and values

## How to deliver
1. Implement all files
2. Run acceptance commands
3. Write report to `work/reports/wave-2/03-lifecycle-service.report.md`
4. Stop

## Constraints
- Time budget: 60 min
- No new models — use existing Project model from Task 02
- Do NOT create frontend files
- Terminal state (Closed) cannot transition anywhere
- Closing a project sets actual_end_date = today()
