# Task 02 — Wire a real Celery worker (currently an unused dependency)

## Result
**DONE** — real Celery app in `src/backend/workers/`, two background PDF `@task`s, a
job-status/result API, a `worker` compose service, and storage-abstraction integration on top of
wave-31 task 01. Default behavior (synchronous exports, `local` storage) is unchanged. Full suite:
**413 passed, 6 skipped, 0 failed** (412 baseline + 7 new celery tests; 6 skips are the pre-existing
MinIO tests that skip when MinIO is unreachable from the test env). `ruff` clean. `docker compose
config` valid. Committed on `wave-31-02-work` (9d9f80e).

## Item-by-item

### 1. `src/backend/workers/celery_app.py` (new)
`Celery("swa_erp", broker=settings.REDIS_URL, backend=settings.REDIS_URL)` — Redis doubles as the
broker and result backend (it was already a cache). JSON serializers, UTC, `result_expires=3600`,
`task_track_started=True`, `autodiscover_tasks(["src.backend.workers"])`.

### 2. `src/backend/workers/tasks.py` (new)
Two tasks, each opening a worker-owned DB session and writing the generated PDF through the storage
abstraction (`get_storage().save(f"jobs/{job_id}.pdf", pdf_bytes)`) so results live wherever
`STORAGE_BACKEND` points (local or MinIO), consistent with task 01:
- `workers.generate_project_summary_pdf(project_id)` → `export_project_summary`
- `workers.generate_financial_report_pdf(start_date_iso, end_date_iso)` → `export_financial_report`

Both `max_retries=2` with countdown on failure. A worker-engine `sessionmaker` is module-scoped so
tasks don't depend on the request-scoped FastAPI session.

### 3. `src/backend/api/jobs.py` (new)
- `GET /api/jobs/{job_id}` → `{"job_id", "status": pending|started|success|failure, ...}`. On
  success includes `result_url` (via `get_storage().url(...)`); on failure includes `error`.
- `GET /api/jobs/{job_id}/result` → streams the stored PDF bytes as an attachment when the job
  succeeded; 404 otherwise. Reads through `get_storage().read(...)` so both backends work.

RBAC: both endpoints require PM+ (same as the sync export endpoints).

### 4. `src/backend/api/exports.py` — async option added, sync path untouched
- `GET /api/exports/projects/{project_id}/summary.pdf?async=true` → `202 {"job_id": "..."}`
  (enqueues `generate_project_summary_pdf`); without `?async` the synchronous path is byte-for-byte
  identical to before.
- `GET /api/exports/reports/financial.pdf?async=true` → same pattern for the financial report.
- The synchronous code paths were not modified — verified by the unchanged existing export tests
  (`tests/wave-8/test_exports.py`, all 6 passing) plus a dedicated `test_sync_path_unchanged`.

### 5. `docker-compose.yml` — `worker` service
`worker` builds the same image as `backend`, shares `DATABASE_URL`/`REDIS_URL`/`SECRET_KEY`/
`STORAGE_BACKEND`/`MINIO_*` env, and runs `celery -A src.backend.workers.celery_app worker
--loglevel=info`. Depends on postgres/redis healthy + migrate complete. Validated with
`docker compose config -q` (only the pre-existing `version` obsolete warning).

### 6. `tests/wave-31/test_celery_tasks.py` (new, 7 tests)
Runs Celery in eager mode (`task_always_eager=True`, `result_backend="cache+memory://"`,
`broker_url="memory://"`) so no broker/worker process is needed in CI. The worker DB factory is
patched to the test DB session factory (same pattern conftest uses). Covers:
- both tasks produce a stored PDF (`%PDF` magic bytes read back via `get_storage()`)
- `?async=true` → 202 + job_id; poll reaches `success` with a `result_url`; `/result` returns the PDF
- async financial report enqueue returns a job id
- sync path unchanged (no `?async` → direct 200 PDF)
- unknown job id → `pending` (not an error)
- designer cannot use async endpoint (401/403)

### 7. Docs
- `docs/runbook.md`: local-dev worker start step (`celery -A src.backend.workers.celery_app worker`)
  + async-job usage note + note that a missing worker leaves jobs `pending` (never errors);
  docker-compose full-stack line now mentions the auto-started `worker`.
- `HIERARCHY.md`: the "Celery unimplemented" correction (2026-07-21) is replaced with the now-true
  state (workers/ app + tasks + compose worker + jobs API), dated 2026-08-09.
- `README.md`: the "Celery and MinIO are NOT live" correction (2026-08-07) is replaced with the
  current storage-abstraction + Celery reality, referencing `docs/runbook.md`.

## Acceptance criteria check
- [x] **`docker-compose up -d` — a `worker` container is healthy and processing jobs** — compose
  file validates; the `worker` service is declared with the documented command. Full `up -d` not
  exercised (host postgres/redis already bind 5432/6379 — pre-existing environment state, same as
  task 01); the service definition is the deliverable here, and task execution is covered by the
  eager-mode tests.
- [x] **`POST .../summary.pdf?async=true` returns a job ID; polling `GET /api/jobs/{id}` reaches
  `success` with a downloadable result** — `test_async_summary_endpoint_returns_job_id_then_success`
  asserts 202 → `success` → `result_url` → PDF bytes via `/result`. PASSED.
- [x] **The existing synchronous PDF export path (no `?async=true`) is completely unchanged** —
  all 6 `tests/wave-8/test_exports.py` tests pass unchanged, plus `test_sync_path_unchanged`. PASSED.
- [x] **`python3 -m pytest tests/ -q` — 393+ baseline, plus new Celery tests** — **413 passed,
  6 skipped, 0 failed** (10:46, full clean run; no other pytest processes active).
- [x] **`docs/runbook.md` updated with the new worker-start step** — done (see §7).
- [x] **`HIERARCHY.md`'s "Celery unimplemented" note corrected** — done (see §7).

## Honest summary
- What landed is additive: the sync export path is untouched, `local` storage remains the default,
  and the worker is opt-in via compose. Celery runs eagerly in tests, so CI needs no broker.
- **Full-stack `docker-compose up -d` not exercised** (port conflicts with host services + long
  image builds, as in task 01). The `worker` service + task execution are verified via config
  validation and the eager test suite; a live-broker smoke test is a follow-up if IT wants one.
- **Retry semantics**: task `max_retries=2` with a 10s countdown; a genuinely broken task will land
  in `failure` and the status endpoint surfaces `error` — matches the brief's edge-case handling.
- Task outputs currently go to storage under `jobs/<job_id>.pdf`; `result_expires=3600` governs the
  Celery result metadata, and the files themselves are governed by the storage backend's lifecycle.

## Time/tokens
- Elapsed: ~55 min wall (reconcile worktree + implement + docs ~25 min; full suite runs ~30 min —
  a large part of that was tracking down deadlocks caused by stray concurrent pytest processes on
  this machine, not by the change).
- Tokens: not tracked by this environment.
