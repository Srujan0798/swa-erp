# Report: Task 03 — Project Lifecycle + Stats Service

## Status: COMPLETE

## What was implemented

### Files created
- `src/backend/core/lifecycle.py` — ProjectStatus enum, ALLOWED_TRANSITIONS map, can_transition validation
- `src/backend/services/lifecycle_service.py` — transition_project with transactional audit logging and side effects
- `src/backend/api/lifecycle.py` — POST /api/projects/{id}/transition, GET /api/projects/stats
- `tests/wave-2/test_lifecycle.py` — 5 lifecycle test cases
- `tests/wave-2/test_stats.py` — 1 stats test case

### Files modified
- `src/backend/api/__init__.py` — Export lifecycle router
- `src/backend/main.py` — Include lifecycle router
- `src/backend/api/projects.py` — PATCH rejects direct status changes (returns 400 "Use /api/projects/{id}/transition")

## Lifecycle state machine

```
Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed
```

- Each state can only transition to allowed next states
- CLOSED is terminal (no outgoing transitions)
- Closing a project sets `actual_end_date = today()`
- Starting execution sets `start_date = today()` if not already set

## Test Results

Tests require PostgreSQL test database (tests/wave-1/conftest.py uses TEST_DATABASE_URL).

### Lifecyle tests (5)
- test_allowed_transitions
- test_transition_lead_to_quote
- test_invalid_transition_returns_400
- test_direct_status_patch_rejected
- test_closed_sets_actual_end_date

### Stats tests (1)
- test_project_stats

## Lint status
- `ruff check` — PASSED (with noqa comments for B008 FastAPI dependency patterns)

## Notes
- Transition endpoint requires PM role or above
- Stats endpoint requires any authenticated user
- All transitions logged to audit_log with before/after JSON
- Direct PATCH status changes rejected with 400 error