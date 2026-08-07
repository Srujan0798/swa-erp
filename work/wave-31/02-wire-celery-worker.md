# Task 02 — Wire a real Celery worker (currently an unused dependency)

## What to do
`celery==5.4.0` has been in `requirements.txt` since the project started, but there is no
Celery app, no `@task`, and no worker process anywhere — confirmed by grep, documented as a
known limitation in `deliverables/SUBMISSION.md` §4. Everything that could be async (PDF
generation for exports/invoices, report generation) currently runs synchronously on the request
thread. Wire up real background job processing for the slowest of these.

**Depends on wave-31 task 01 if it has landed** (Celery task results/file outputs should go
through the same storage abstraction) — check `work/reports/wave-31/` before starting; if task
01 hasn't landed yet, write PDF outputs to local disk directly as today and note the follow-up.

## Files to modify
- CREATE: `src/backend/workers/__init__.py`, `src/backend/workers/celery_app.py` — the Celery
  app instance, configured from `REDIS_URL` (already used as a cache, now doubles as the broker)
- CREATE: `src/backend/workers/tasks.py` — the actual `@app.task` functions
- `docker-compose.yml` — add a `worker` service running `celery -A src.backend.workers.celery_app worker`
- `src/backend/services/export_service.py` — the PDF-generation call sites: offer an async path
  (enqueue + return a job ID + status-polling endpoint) alongside the existing synchronous path,
  don't rip out sync entirely — some callers may still want to wait for the result
- CREATE: `src/backend/api/jobs.py` — `GET /api/jobs/{job_id}` to poll status/result of an
  enqueued task
- CREATE: `tests/wave-31/test_celery_tasks.py`

## Files you must NOT touch
- Any currently-synchronous export/report endpoint's existing response shape — this task adds
  an async option, it doesn't change what already works
- `HIERARCHY.md`'s note about Celery being unimplemented — update that note once this lands, but
  as part of this task's own doc updates, not a separate blind find-replace

## The core problem (inline)

### Celery app setup
Standard Celery + Redis broker/backend pattern:
```python
# workers/celery_app.py
from celery import Celery
app = Celery("swa_erp", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
app.autodiscover_tasks(["src.backend.workers"])
```

### Which operations to move to background
Pick the genuinely slow ones — PDF generation (WeasyPrint, per `deliverables/SUBMISSION.md`,
already noted as a candidate) is the clearest case. Don't try to async-ify everything; a
records/CRUD system doesn't need most operations backgrounded. Scope this to:
- Financial report PDF export (`api/exports.py`)
- Invoice PDF generation, if it isn't already fast enough to stay synchronous (check first —
  don't background something that's actually instant)

### Job status endpoint
```
POST /api/exports/projects/{id}/summary.pdf?async=true  -> 202 {"job_id": "..."}
GET  /api/jobs/{job_id}                                  -> {"status": "pending"|"success"|"failure", "result_url": "..."}
```
Keep the existing synchronous behavior as the default (no `?async=true`) so nothing currently
depending on immediate PDF bytes breaks.

## Edge cases
- Worker not running (dev forgot to start it) — an enqueued job should sit in `pending` state
  forever, not error; document this clearly in `docs/runbook.md` (make dev must now also start
  the worker — update the Makefile `dev` target or document the extra step)
- Task failure — the job status endpoint must surface the error, not just hang at `pending`

## Acceptance criteria
- [ ] `docker-compose up -d` — a `worker` container is healthy and processing jobs
- [ ] `POST .../summary.pdf?async=true` returns a job ID; polling `GET /api/jobs/{id}` reaches
  `success` with a downloadable result
- [ ] The existing synchronous PDF export path (no `?async=true`) is completely unchanged —
  verify with the existing tests, don't just assume
- [ ] `python3 -m pytest tests/ -q` — 393+ baseline, plus new Celery tests
- [ ] `docs/runbook.md` updated with the new worker-start step
- [ ] `HIERARCHY.md`'s "Celery unimplemented" note corrected to reflect what's now real

## How to deliver
1. Implement the worker app, one background task type, the job-status endpoint
2. Verify both the new async path AND that the existing sync path is untouched
3. Update the two docs noted above
4. Write report to `work/reports/wave-31/02-wire-celery-worker.report.md`
5. Stop — commit your work with git before writing the report

## Constraints
- Time budget: 120 min
- Scope to ONE background task type done well, not several done shallowly
- Don't remove the synchronous code path
- Allowed tools: file edit, docker, pytest, ruff
