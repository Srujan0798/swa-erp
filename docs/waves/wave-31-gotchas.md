# Wave 31 — Gotchas

> **Source:** Harvested from `work/reports/wave-31/01-wire-minio-storage.report.md` + `02-wire-celery-worker.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### Object storage abstraction: local default, minio opt-in
`src/backend/core/storage.py` — `local` is the default backend; `minio` is opt-in via `STORAGE_BACKEND=minio`. Don't assume MinIO is active without checking the env var.

### Celery app in src/backend/workers/
`workers/celery_app.py` defines the Celery app (Redis broker/backend). `workers/tasks.py` has `@task`s for project-summary and financial-report PDF generation.

### Async export endpoints
Async export endpoints (`?async=true`) enqueue jobs tracked via `api/jobs.py`. Results are written through the storage abstraction.

### Docker-compose has worker service
`docker-compose.yml` has a `worker` service running `celery -A src.backend.workers.celery_app worker`.

### Version cut 1.0.1
Version cut at 1.0.1 after wave-31. See `CHANGELOG.md`.
