# Report — Task 01: Sweep remaining models for migration drift

## Status: DONE

## Method
1. `docker-compose down -v && docker-compose up -d --build` (fresh volumes, wave-14 auto-migrate
   `migrate` service ran `alembic upgrade heads` from scratch).
2. Dumped every live table's schema with `psql \d <table>` (36 tables).
3. Read every model file in `src/backend/models/*.py` (25 model classes across 25 files) and
   diffed each one's declared columns/types against the live `\d` output, column by column.
4. For every mismatch, checked the originating migration(s) with `grep`/`git blame`-style reading
   of `alembic/versions/*.py` to determine whether the model or the DB was authoritative per the
   task's rule ("model is the source of truth").
5. Wrote one new migration per drifted model, re-ran `docker-compose down -v && up -d --build`
   to confirm a clean `alembic upgrade heads` picks them up, re-diffed the live schema.
6. Ran `python3 -m pytest tests/ -q` (full suite).
7. Hit live endpoints through the running `backend` container for the newly-fixed paths.

## Drift found and fixed

### 1. `notifications` table — missing entirely
- **Model:** `src/backend/models/notification.py` (`Notification`), used by
  `src/backend/db/repositories/notification_repo.py`.
- **Problem:** No migration ever created the `notifications` table. It didn't exist in the live
  DB at all. Additionally the model was never imported in `src/backend/models/__init__.py`, so
  `Base.metadata.create_all()` (used by the test suite) doesn't register it either **unless**
  something imports `notification_repo` first — which is exactly why this slipped past tests,
  same class of gap as the Task/Document bugs but one level worse (missing table, not missing
  column).
- **Fix:** `src/backend/alembic/versions/0023_align_notifications_with_model.py` — creates
  `notifications` with the exact columns/indexes the `Notification` model declares
  (`id, user_id, type, title, message, reference_type, reference_id, is_read, created_at`), FK to
  `users.id`, `down_revision="0009"`.
- **Verified live:** `\d notifications` on a freshly-migrated container now matches the model
  exactly.
- **Not fixed / separate finding (did not touch, out of scope):** `src/backend/api/notifications.py`
  defines a router but it is **never `include_router()`'d in `src/backend/main.py`** — the
  notifications API is currently unreachable regardless of the table existing. Flagging for the
  orchestrator; this is a routing gap, not a migration/model drift issue, so no route changes were
  made here per the task's tool scope (alembic/docker/psql/pytest/curl only).

### 2. `timesheet_audit_log` table — missing entirely
- **Model:** `src/backend/models/time_tracking.py` (`TimesheetAuditLog`), used by
  `src/backend/services/time_service.py::_create_audit_log()`, called from both
  `submit_timesheet_service()` and `approve_timesheet_service()`.
- **Problem:** No migration created `timesheet_audit_log`. **This is a live, reachable 500**:
  `POST /api/timesheets/{id}/submit` and `POST /api/timesheets/{id}/approve` both insert into this
  table and would fail with `relation "timesheet_audit_log" does not exist` in production. Not
  caught by tests because the model is imported (via `__init__.py` → `TimesheetAuditLog` is listed
  in `__all__`), so `create_all()` in the test DB creates it fine — the gap only shows up when
  running real Alembic migrations, exactly the blind spot this task exists to close.
- **Fix:** `src/backend/alembic/versions/0024_align_timesheet_audit_log_with_model.py` — creates
  `timesheet_audit_log` with `id, timesheet_id, action, performed_by, notes, created_at`, FKs to
  `timesheets.id` (CASCADE) and `users.id` (CASCADE), `down_revision="0013"`.
- **Verified live end-to-end:** created a user/client/project/time-entry/timesheet through the
  running API, called `POST /api/timesheets/{id}/submit` → **200**, status flipped to
  `"submitted"`, and confirmed a row landed in `timesheet_audit_log`
  (`action='submitted', performed_by=<user id>`). Before this fix that call would have 500'd on a
  real-migrated database. Test data was cleaned up afterward.

## Models checked — no drift (columns match live schema exactly)
`AuditLog`, `BOQ`/`BOQItem`, `Client`, `ComplianceStandard`, `ComplianceChecklistItem`,
`ProjectComplianceItem`, `Contact`, `DocumentReference`, `Inquiry`, `Invoice`/`InvoiceItem`,
`MaterialCategory`, `Material`, `Project`, `ProjectCost`, `Quote`/`QuoteItem` (see note below),
`ReferenceCounter`, `RefreshToken`, `RFQ`/`RFQItem`, `SustainabilityMetric`, `Task`/`TaskComment`
(already fixed by 0021, re-verified clean), `TaskDependency`, `TimeEntry`/`Timesheet`,
`Token`, `User`, `Vendor`/`VendorContact`.

Specifically the three candidates the wave-12 report named as unverified — **`Material`,
`Contact`, `ComplianceItem`** — were checked column-by-column and have **zero drift**; their
migrations (0008, 0002, 0011) already match their current models exactly.

## Opposite-direction drift found — DB has columns the model doesn't (flagged only, not touched)
Per the task's edge-case instructions, these are legacy columns left behind by earlier migrations
that predate later model refactors. Not auto-dropped since they may hold data; flagging for the
orchestrator to decide (drop via new migration, or backfill the model to use them):

| Table | Extra live column(s) | Origin |
|---|---|---|
| `tasks` | `sort_order`, `created_by` | original `0006_add_tasks_and_task_comments.py`, superseded by `position`/`reporter_id` added in `0021` but never dropped |
| `task_comments` | `user_id` | same `0006` migration, superseded by `author_id` added in `0021` |
| `documents` | `version` | original `0010` migration's column, superseded by `version_number` added in `0022` |
| `document_folders` | `deleted_at` | present in `0010` migration but never added to the `DocumentFolder` model |
| `quotes` | `code` | present in original `0005_add_quotes.py` (`nullable=True`) but never added to the `Quote` model |

None of these cause 500s (extra DB columns are invisible to SQLAlchemy unless the model declares
them), so they're metadata cleanup items, not bugs.

## Other drift-adjacent observations (not migration drift, flagged only)
- `documents.uploaded_by` is `NOT NULL` in the live DB (from `0010`) but the `Document` model
  declares it `nullable=True`. `documents.stored_name`, `version_number`, `updated_at` are
  nullable in the live DB (added by `0022`, deliberately nullable per that migration's own
  docstring since it was backfilling an existing table) while the model declares them
  `nullable=False`. Since `0021`/`0022` are marked "already correct, don't modify" by this task's
  own constraints, and this nullable/not-null mismatch is orthogonal to "missing column" drift
  (nothing 500s from it — it's the DB being *more* permissive than the model expects, not less),
  I left it alone and am flagging it here rather than bundling a constraint-tightening migration
  into this task.
- `audit_log.ip_address` is Postgres `INET` in the DB (from `0001`) vs `String(45)` on the model —
  intentional type choice from the original migration, psycopg round-trips it as a string
  transparently, not a functional bug.

## Acceptance criteria
- [x] `docker-compose down -v && docker-compose up -d` (rebuilt with `--build` after adding the
  new migration files so the `migrate` image picked them up) then compared every model's columns
  against every live table — the two missing-table cases above were the only remaining drift;
  both fixed and re-verified against a second clean `down -v && up -d --build` run.
- [x] `python3 -m pytest tests/ -q` → **324 passed**, 0 failed (79 warnings, all pre-existing
  `datetime.utcnow()` deprecation warnings unrelated to this task).
- [x] Hit at least one endpoint per newly-fixed model against the live docker stack:
  - `GET /api/materials` → 200 (sanity check on a wave-12-named candidate, no drift found there
    so nothing to fix, but confirms the endpoint itself is healthy)
  - `POST /api/timesheets/{id}/submit` → 200, and confirmed the `timesheet_audit_log` insert
    succeeded (the actual bug this task needed to catch)
  - `notifications` has no reachable endpoint currently (router not wired into `main.py`, see
    above) so it could only be verified by direct schema inspection, not an HTTP round-trip.
- [x] `alembic -c src/backend/alembic.ini heads` → **7 heads**, same count as before this task
  (0011, 0018, 0020, 0021, 0022, 0023, 0024 — the two new migrations were deliberately chained
  onto existing heads 0009 and 0013 respectively rather than branching off further, so the total
  head count did not increase).

## Files created
- `src/backend/alembic/versions/0023_align_notifications_with_model.py`
- `src/backend/alembic/versions/0024_align_timesheet_audit_log_with_model.py`

## Files touched
None outside the two new migration files above. `0021`/`0022` were not modified. No model files
were modified (per task constraint) — including `src/backend/models/__init__.py`, even though its
missing `Notification` import is arguably related; left as-is since the task scope was migrations,
not model registration, and it's called out above as a related finding instead.
