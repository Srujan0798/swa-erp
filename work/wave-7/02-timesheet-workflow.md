# Task 02 — Timesheet Submission & Approval Workflow

## Goal
Implement the weekly timesheet lifecycle: generate timesheets from time entries, submit for approval, manager approve/reject, lock after approval, and audit logging. Depends on Task 01 models being in place.

Reference spec: `.specify/specs/wave-7/spec.md` section Timesheet Workflow.

## Files to Create / Modify

### CREATE: `src/backend/services/timesheet_workflow_service.py`
Core workflow logic separated from basic CRUD:

```python
def generate_weekly_timesheet(db: Session, user_id: UUID, week_start: date) -> Timesheet:
    """Aggregate time_entries for the user + week, create/update timesheet with totals."""

def submit_timesheet(db: Session, timesheet_id: UUID, user_id: UUID) -> Timesheet:
    """Transition draft → submitted. Validate: all entries present, no gaps, totals match."""

def approve_timesheet(db: Session, timesheet_id: UUID, manager_id: UUID) -> Timesheet:
    """Transition submitted → approved. Lock the week: prevent new entries in approved range."""

def reject_timesheet(db: Session, timesheet_id: UUID, manager_id: UUID, reason: str) -> Timesheet:
    """Transition submitted → rejected. Allow user to fix and re-submit."""

def lock_week(db: Session, user_id: UUID, week_start: date) -> None:
    """Mark a week as locked — prevents time entry creation in that range."""
```

### MODIFY: `src/backend/services/time_tracking_service.py`
- `create_time_entry` — add check: reject if user has an approved timesheet covering the entry's date
- Wire `generate_timesheet`, `submit_timesheet`, `approve_timesheet`, `reject_timesheet` to the workflow service

### CREATE: `src/backend/core/timesheet_rules.py`
Business rules module:
```python
def compute_week_boundaries(reference_date: date) -> tuple[date, date]:
    """Return (monday, sunday) for the week containing reference_date."""

def validate_timesheet_entries(entries: list[TimeEntry], week_start: date, week_end: date) -> list[str]:
    """Return list of validation errors (empty = valid). Checks: no overlapping hours per day, no gaps if required."""

def is_week_locked(db: Session, user_id: UUID, week_start: date) -> bool:
    """Check if there's an approved timesheet for this user + week."""

def can_edit_entry(db: Session, entry: TimeEntry) -> bool:
    """Return True if the entry's week is not locked (no approved timesheet)."""
```

### MODIFY: `src/backend/api/timesheets.py`
- `POST /api/timesheets/{timesheet_id}/submit` — calls workflow service
- `POST /api/timesheets/{timesheet_id}/approve` — require manager/admin role
- `POST /api/timesheets/{timesheet_id}/reject` — require manager/admin role, accept optional `reason` in body
- `POST /api/timesheets/generate` — generate/refresh for current user + week (accept `week_start` in body)

### CREATE: `src/backend/schemas/timesheet.py` (if not already created in Task 01)
- `TimesheetGenerateRequest` — week_start: date
- `TimesheetSubmitRequest` — (empty body, timesheet_id from path)
- `TimesheetApproveRequest` — (empty body)
- `TimesheetRejectRequest` — reason: str (optional)
- `TimesheetRead` — full model with computed fields
- `TimesheetListResponse` — paginated list

### MODIFY: `src/backend/main.py`
Ensure timesheets router is registered with proper prefix.

### MODIFY: `src/backend/alembic/versions/0012_add_time_tracking.py`
If not already created in Task 01, add `timesheet_audit_log` table:
```python
class TimesheetAuditLog(Base):
    __tablename__ = "timesheet_audit_log"
    id: Mapped[UUID] = primary_key
    timesheet_id: Mapped[UUID] = FK → timesheets.id
    action: Mapped[str]  # "submitted", "approved", "rejected", "re-submitted"
    performed_by: Mapped[UUID] = FK → users.id
    notes: Mapped[str | None]
    created_at: Mapped[datetime]
```

## Files you must NOT touch
- `src/backend/models/user.py`
- `src/backend/models/project.py`
- `src/backend/api/auth.py`
- `src/backend/core/security.py`
- `src/frontend/` (frontend is Task 05)

## Skills to use
- `tdd` — red → green → refactor
- `code-review` — self-review before declaring done

## The core problem (inline)

### Timesheet generation algorithm
```python
def generate_weekly_timesheet(db, user_id, week_start):
    week_end = week_start + timedelta(days=6)
    entries = db.query(TimeEntry).filter(
        TimeEntry.user_id == user_id,
        TimeEntry.date >= week_start,
        TimeEntry.date <= week_end,
        TimeEntry.deleted_at.is_(None),
    ).all()

    total = sum(e.hours for e in entries)
    billable = sum(e.hours for e in entries if e.is_billable)

    timesheet = get_or_create_timesheet(db, user_id, week_start, week_end)
    timesheet.total_hours = total
    timesheet.billable_hours = billable
    db.commit()
    return timesheet
```

### State machine
```
draft ──submit──→ submitted ──approve──→ approved (locked)
                       │
                       └──reject──→ rejected ──submit──→ submitted
```

### Lock enforcement
When a timesheet is approved:
1. Set `status = "approved"`
2. Set `approved_by = manager_id`, `approved_at = now()`
3. Any `create_time_entry` call with `date` in `[week_start, week_end]` for that user → reject with 409

### Audit log entries
Every state transition writes to `timesheet_audit_log`:
```python
audit = TimesheetAuditLog(
    timesheet_id=timesheet.id,
    action="submitted",  # or "approved", "rejected"
    performed_by=user_id,
    notes=None,  # or rejection reason
)
db.add(audit)
```

### Edge cases
- Submit with zero entries → reject (must have at least 1 entry)
- Approve already-approved timesheet → 400
- Reject already-rejected timesheet → 400
- Generate for future week → allow (draft)
- User tries to submit another user's timesheet → 403

## Acceptance criteria (executable, not prose)
- [ ] `pytest tests/wave-7/test_timesheet_workflow.py` passes
- [ ] `make lint` clean
- [ ] Generate timesheet aggregates hours correctly
- [ ] Submit transitions draft → submitted
- [ ] Approve transitions submitted → approved, sets approved_by and approved_at
- [ ] Reject transitions submitted → rejected with optional reason
- [ ] After approval, new time entries in locked week return 409
- [ ] Audit log records every transition with correct action and performer

## Test File
Create `tests/wave-7/test_timesheet_workflow.py` with at least:
- `test_generate_timesheet_from_entries` — verify totals
- `test_generate_empty_week` — zero entries, total = 0
- `test_submit_draft_timesheet` — status changes to submitted
- `test_submit_non_draft_returns_400` — can't submit approved timesheet
- `test_approve_submitted_timesheet` — sets approved_by, approved_at
- `test_approve_requires_manager_role` — regular user gets 403
- `test_reject_submitted_timesheet` — status changes to rejected
- `test_cannot_create_entry_in_approved_week` — 409 response
- `test_audit_log_on_submit` — audit entry created
- `test_audit_log_on_approve` — audit entry created
- `test_audit_log_on_reject` — audit entry created with reason

## How to deliver
1. Implement workflow service, rules module, schemas, migration update + tests
2. Run `pytest tests/wave-7/test_timesheet_workflow.py` — all pass
3. Run `make lint` — clean
4. Write report to `work/reports/wave-7/02-timesheet-workflow.report.md`
5. Stop

## Constraints
- Time budget: 40 min
- No new dependencies without flagging
- Match existing patterns (see `src/backend/services/lifecycle_service.py` for state machine pattern)
- Allowed tools: `ruff`, `black`, `pytest`, `alembic`
