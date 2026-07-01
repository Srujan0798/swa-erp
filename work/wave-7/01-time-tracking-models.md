# Task 01 — Time Tracking Models & CRUD API

## Goal
Create the `TimeEntry` and `Timesheet` database models, Pydantic schemas, repository, service, and REST API for CRUD operations on time entries. A `TimeEntry` represents a single block of work (15-minute increments) logged by a user against a project (optionally a task). A `Timesheet` aggregates entries into a weekly summary.

Reference spec: `.specify/specs/wave-7/spec.md` section Time Tracking.

## Files to Create / Modify

### CREATE: `src/backend/models/time_entry.py`
```python
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.db.base import Base


class TimeEntry(Base):
    __tablename__ = "time_entries"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    task_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    hours: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)  # 0.25 increments, max 24
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_billable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

### CREATE: `src/backend/models/timesheet.py`
```python
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Date, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.db.base import Base


class Timesheet(Base):
    __tablename__ = "timesheets"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    week_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    total_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=Decimal("0.00"))
    billable_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=Decimal("0.00"))
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

### MODIFY: `src/backend/models/__init__.py`
Add imports for `TimeEntry` and `Timesheet`.

### CREATE: `src/backend/schemas/time_tracking.py`
- `TimeEntryCreate` — project_id, task_id (optional), date, hours, description, is_billable
- `TimeEntryUpdate` — date, hours, description, is_billable (all optional)
- `TimeEntryRead` — full model with user_name, project_name
- `TimeEntryListResponse` — paginated list
- `TimesheetRead` — full model with user_name, approved_by_name
- `TimesheetListResponse` — paginated list

### CREATE: `src/backend/db/repositories/time_tracking_repo.py`
- `create_time_entry(db, data) -> TimeEntry`
- `get_time_entry_by_id(db, entry_id) -> TimeEntry | None`
- `update_time_entry(db, entry_id, data) -> TimeEntry | None`
- `soft_delete_time_entry(db, entry_id) -> bool`
- `list_time_entries(db, project_id, user_id, start_date, end_date, page, page_size) -> tuple[list, int, int, int]`
- `list_user_entries_for_week(db, user_id, week_start) -> list[TimeEntry]`
- `get_timesheet_by_id(db, timesheet_id) -> Timesheet | None`
- `get_timesheet_by_user_week(db, user_id, week_start) -> Timesheet | None`
- `create_or_update_timesheet(db, user_id, week_start, entries) -> Timesheet`

### CREATE: `src/backend/services/time_tracking_service.py`
- `create_time_entry(db, user_id, data) -> TimeEntryRead` — validate hours in 0.25 increments, validate date not in locked timesheet week
- `update_time_entry(db, entry_id, user_id, data) -> TimeEntryRead` — only owner can update, only draft timesheet
- `delete_time_entry(db, entry_id, user_id) -> bool` — only owner, only draft
- `list_time_entries(db, filters) -> TimeEntryListResponse`
- `generate_timesheet(db, user_id, week_start) -> TimesheetRead` — aggregate entries for the week, compute totals
- `submit_timesheet(db, timesheet_id, user_id) -> TimesheetRead` — draft → submitted
- `approve_timesheet(db, timesheet_id, manager_id) -> TimesheetRead` — submitted → approved
- `reject_timesheet(db, timesheet_id, manager_id) -> TimesheetRead` — submitted → rejected

### CREATE: `src/backend/api/time_entries.py`
- `POST /api/time-entries` — create entry (authenticated user)
- `GET /api/time-entries` — list entries (filter by project_id, user_id, start_date, end_date)
- `GET /api/time-entries/{entry_id}` — get single entry
- `PATCH /api/time-entries/{entry_id}` — update entry (owner only)
- `DELETE /api/time-entries/{entry_id}` — soft delete (owner only)

### CREATE: `src/backend/api/timesheets.py`
- `GET /api/timesheets` — list timesheets (filter by user_id, status)
- `GET /api/timesheets/{timesheet_id}` — get timesheet with entries
- `POST /api/timesheets/generate` — generate/refresh for current user + week
- `POST /api/timesheets/{timesheet_id}/submit` — submit
- `POST /api/timesheets/{timesheet_id}/approve` — approve (manager/admin only)
- `POST /api/timesheets/{timesheet_id}/reject` — reject (manager/admin only)

### MODIFY: `src/backend/main.py`
Register both routers.

### CREATE: `src/backend/alembic/versions/0012_add_time_tracking.py`
- Create `time_entries` table
- Create `timesheets` table

## Files you must NOT touch
- `src/backend/models/user.py`
- `src/backend/models/project.py`
- `src/backend/models/client.py`
- `src/backend/api/auth.py`
- `src/backend/core/security.py`

## Skills to use
- `tdd` — write tests first, then implement
- `code-review` — self-review before declaring done

## The core problem (inline)

### Hours validation
Hours must be in 0.25 increments (15-minute blocks). Validate: `hours % 0.25 == 0 and 0 < hours <= 24`.

### Week boundaries
A timesheet week runs Monday 00:00 to Sunday 23:59. Given a date, compute `week_start` as the Monday of that week.

### Soft delete
Time entries use soft delete via `deleted_at` timestamp. Queries must filter `deleted_at IS NULL`.

### Inputs available

```python
# TimeEntry fields
project_id: UUID (required, FK → projects.id)
task_id: UUID (optional, no FK yet — reserved for wave-4)
user_id: UUID (required, FK → users.id)
date: date (required)
hours: Decimal (required, 0.25 increments, max 24)
description: str (required, min 1 char)
is_billable: bool (default True)

# Timesheet fields
user_id: UUID
week_start: date (Monday)
week_end: date (Sunday)
status: "draft" | "submitted" | "approved" | "rejected"
total_hours: Decimal (auto-computed)
billable_hours: Decimal (auto-computed)
```

### Edge cases
- User logs entry for a date that falls in an already-approved timesheet week → reject
- Hours must be 0.25 increment and between 0 and 24
- A user can only have one draft/active timesheet per week
- Only the entry owner can update/delete their own entries
- Only managers/admins can approve/reject

## Acceptance criteria (executable, not prose)
- [ ] `pytest tests/wave-7/test_time_tracking.py` passes
- [ ] `make lint` clean (ruff + eslint)
- [ ] Can create a time entry, list it, update it, soft-delete it
- [ ] Hours not in 0.25 increment return 422
- [ ] Can generate a weekly timesheet from entries
- [ ] Submit/approve/reject workflow transitions correctly
- [ ] Approval locks the week — no new entries in approved week

## Test File
Create `tests/wave-7/test_time_tracking.py` with at least:
- `test_create_time_entry` — valid entry, verify response
- `test_create_entry_invalid_hours` — 0.33 hours returns 422
- `test_create_entry_hours_exceed_24` — 25 hours returns 422
- `test_list_time_entries_by_project` — filter works
- `test_update_time_entry` — owner can update
- `test_delete_time_entry` — soft delete, entry not in list
- `test_generate_timesheet` — entries aggregate to correct totals
- `test_submit_timesheet` — draft → submitted
- `test_approve_timesheet` — submitted → approved
- `test_reject_timesheet` — submitted → rejected
- `test_cannot_edit_entry_in_approved_week` — rejected
- `test_non_owner_cannot_update_entry` — 403

## How to deliver
1. Implement models, schemas, repo, service, API, migration + tests
2. Run `pytest tests/wave-7/test_time_tracking.py` — all pass
3. Run `make lint` — clean
4. Write report to `work/reports/wave-7/01-time-tracking-models.report.md`
5. Stop

## Constraints
- Time budget: 45 min
- No new dependencies without flagging
- Match existing patterns (see `src/backend/models/project.py`, `src/backend/api/projects.py`, `src/backend/db/repositories/project_repo.py`)
- Allowed tools: `ruff`, `black`, `pytest`, `alembic`
