# Task 01 — Mount the notifications router

## What to do
`src/backend/api/notifications.py` defines a working router (list/read notifications) but it's
never wired up: it's not exported from `src/backend/api/__init__.py` and never
`app.include_router()`'d in `src/backend/main.py`. Flagged during wave-16's model/migration
drift sweep (`work/reports/wave-16/01-model-migration-drift-sweep.report.md`) — the underlying
`notifications` table now exists (migration `0023`, already merged), the model and repo already
exist, only the router mounting is missing. This is a small, mechanical fix.

## Files to modify
- MODIFY: `src/backend/api/__init__.py` — import and export `notifications_router` from
  `src.backend.api.notifications`, following the exact pattern used for every other router in
  that file (check how `tokens_router` or `sustainability_metrics_router` are imported/exported
  as the reference — same module, same style)
- MODIFY: `src/backend/main.py` — add `app.include_router(notifications_router)` in the existing
  alphabetically-ish ordered block of `include_router` calls (see lines ~42-68); insert it in
  the same relative position it would sort into (after `materials_router`, before
  `project_pnl_router` — check current file for the exact live ordering before inserting)

## Files you must NOT touch
- `src/backend/api/notifications.py` — the router itself is already correct, don't change its
  routes or logic
- `src/backend/models/notification.py`, `src/backend/db/repositories/notification_repo.py` —
  already correct
- Any Alembic migration file — the table already exists (migration 0023), no schema change needed

## The core problem (inline)
This is purely a wiring gap, not a logic bug. `notifications.py`'s router currently defines
endpoints at `/api/tasks/notifications` (check the actual path prefix used inside that file
before assuming — read the file first, the path shown above is from a live grep but verify all
route decorators in the file for the true prefix). Once mounted, `GET` on that path should
return notifications for the current user instead of 404.

## Acceptance criteria
- [ ] `python3 -m pytest tests/ -q` — 324/324 still pass (no regression)
- [ ] `ruff check src/backend/api/__init__.py src/backend/main.py` — clean
- [ ] Against a running stack (`docker-compose up -d` or `make dev`), an authenticated
  `GET` request to the notifications endpoint (exact path per the router file) returns 200, not
  404 — verify with curl + a real JWT, not just a passing unit test
- [ ] No other router's mount order or behavior changes

## How to deliver
1. Read `src/backend/api/notifications.py` in full to confirm the real route paths
2. Wire up the export + mount
3. Run the acceptance commands above, including the live curl check
4. Write report to `work/reports/wave-17/01-mount-notifications-router.report.md`
5. Stop

## Constraints
- Time budget: 20 min — this should be a genuinely small change
- Before claiming DONE, run pytest with NO other pytest process running against the same
  database and with a freshly reset test DB if anything looks like a deadlock or an unrelated
  mass failure — this repo's test suite is known to produce false failures under process/DB
  contention (see `docs/PROJECT_HISTORY.md`); don't report a false regression the way a prior
  wave-15 worker did
- Allowed tools: file edit, pytest, ruff, docker, curl
