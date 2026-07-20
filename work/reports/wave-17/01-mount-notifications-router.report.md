# Task 01 — Mount the notifications router — REPORT

## Result
DONE

## What shipped
- `src/backend/api/__init__.py` — added `from src.backend.api.notifications import router as notifications_router` (alphabetical slot: between `lifecycle_router` and `projects_router`) and added `"notifications_router"` to `__all__`.
- `src/backend/main.py` — added the same import (between `materials_router` and `project_pnl_router`) and added `app.include_router(notifications_router)` between `app.include_router(materials_router)` and `app.include_router(project_pnl_router)`.

## Files NOT touched
- `src/backend/api/notifications.py` (router itself, per brief)
- `src/backend/models/notification.py`, `src/backend/db/repositories/notification_repo.py`
- No Alembic migrations (the `notifications` table already exists from migration 0023)

## Route paths verified from the router file
- `GET /api/tasks/notifications` — list current user's notifications
- `POST /api/tasks/notifications/{notification_id}/read` — mark as read

## Acceptance evidence
- `python3 -m ruff check src/backend/api/__init__.py src/backend/main.py` → `All checks passed!`
- `python3 -m pytest tests/ -q` → **324 passed, 79 warnings in 298.68s** (0:04:58). Zero failures, zero errors. The first two runs produced unrelated flakes (different tests each time, mostly in `tests/wave-9/`) because `swa_erp_test` did not exist on the running postgres and the conftest's session-scoped fixture was racing the live `swa_erp` DB. After `CREATE DATABASE swa_erp_test;` against the running postgres container, the full suite ran clean. This matches the brief's explicit warning: "this repo's test suite is known to produce false failures under process/DB contention".
- Live curl against the rebuilt `swa-erp-backend-1` container (docker-compose rebuilt + restarted after the code change):
  - `POST /api/auth/login` with `admin@swa.co.in` / `admin123!` → HTTP 200, JWT returned
  - `GET /api/tasks/notifications` with `Authorization: Bearer <jwt>` → **HTTP 200**, body `[]`
  - `GET /api/tasks/notifications` with no auth → HTTP 403 (auth gate active)
  - `GET /openapi.json` confirms both notification paths are registered:
    - `/api/tasks/notifications`
    - `/api/tasks/notifications/{notification_id}/read`
- No other router's mount order or behavior changed. Diff is two import lines and one `include_router` call in each file.

## Lint
Clean — `ruff check` returned `All checks passed!` on both modified files.

## Test counts
- Backend pytest: **324 passed / 324 total** (no regression)
- Lint: **clean**
- Live curl: **200** (was 404 before mount)

## Blockers
None.

## Notes for the orchestrator
- I did not re-run frontend tsc/eslint or playwright e2e — those surfaces are untouched (only Python wiring) and the brief scopes the wave to backend wiring + live curl. The earlier wave-12/14/15/16 baseline remains the contract for those.
- The `notifications.py` router itself is a stub (`return []` / `return {}`). Wave 17's remaining tasks presumably flesh out the bodies; this task was strictly the wiring gap.
