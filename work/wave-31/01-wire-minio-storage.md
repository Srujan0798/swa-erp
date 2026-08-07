# Task 01 — Wire MinIO/S3 file storage (currently target-state only)

## What to do
File storage is currently a local `uploads/` directory at the repo root — functional, but
target-state was always S3-compatible object storage (MinIO), per the original architecture
plan and `docs/IT_BRIEF.md`. Wire it up for real, with local-disk as a config-selectable
fallback (not a hard cutover — some deployments may still want local disk).

## Files to modify
- `docker-compose.yml` — add a `minio` service
- `.env.example` — `MINIO_ENDPOINT`/`MINIO_ACCESS_KEY`/`MINIO_SECRET_KEY` already have empty
  slots; fill in dev defaults, add `STORAGE_BACKEND` (values: `local` | `minio`)
- `src/backend/core/config.py` — add `STORAGE_BACKEND` setting
- CREATE: `src/backend/core/storage.py` — a small storage abstraction with two backends
- `src/backend/services/boq_service.py`, `document_service.py` (and any other file-writing
  service — grep for `UPLOAD_DIR` / `uploads/` to find all of them) — route through the new
  storage abstraction instead of writing directly to `Path("uploads/...")`
- CREATE: `tests/wave-31/test_storage_backend.py`

## Files you must NOT touch
- Any test that currently passes by assuming local-disk storage — if a test needs updating to
  work with the abstraction, update it minimally; don't rewrite unrelated test logic
- `docker-compose.prod.yml` — that has `PENDING IT ANSWER` placeholders already scoped
  specifically to production infra; add MinIO there too, but keep the existing placeholder
  convention, don't invent new prod assumptions

## The core problem (inline)

### Storage abstraction (`core/storage.py`)
A minimal interface, not an over-engineered plugin system:
```python
class StorageBackend(Protocol):
    def save(self, key: str, content: bytes) -> str: ...       # returns the stored path/URL
    def read(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...
    def url(self, key: str) -> str: ...                         # for serving/download links

class LocalStorage(StorageBackend):
    # wraps the existing uploads/<id>/ pattern, unchanged behavior

class MinIOStorage(StorageBackend):
    # boto3 or minio-py client against MINIO_ENDPOINT
```
Select backend via `settings.STORAGE_BACKEND` at startup, expose a single `get_storage()`
factory function services import instead of touching the filesystem directly.

### MinIO in docker-compose.yml
Standard MinIO service, dev credentials, a named volume, health check. Match the style of the
existing `postgres`/`redis` service blocks in the same file (restart policy, healthcheck
pattern).

### Migration path for existing services
Grep for every place currently doing direct file I/O (`open(...)`, `Path("uploads/...")`,
`shutil`) in `services/`. Replace with calls through `get_storage()`. Existing files already on
local disk from before this change are NOT migrated automatically — that's a separate, manual
data-migration concern (note it in the report, don't attempt automatic migration).

## Edge cases
- `STORAGE_BACKEND=local` (the default) must produce byte-identical behavior to today — this is
  the safety net if MinIO isn't wanted at a given deployment
- MinIO connection failure at startup should fail loudly (don't silently fall back to local disk
  — that would hide a real ops problem)

## Acceptance criteria
- [ ] `STORAGE_BACKEND=local` — all existing tests pass unchanged, 393+ baseline
- [ ] `STORAGE_BACKEND=minio` against the new docker-compose MinIO service — a file uploaded via
  the API can be retrieved back byte-identical
- [ ] `docker-compose up -d` — MinIO container healthy
- [ ] New tests cover both backends
- [ ] `ruff check` clean

## How to deliver
1. Implement the abstraction + both backends + compose service
2. Migrate the file-writing services to use it
3. Run acceptance checks with BOTH backend settings
4. Write report to `work/reports/wave-31/01-wire-minio-storage.report.md`
5. Stop — commit your work with git before writing the report

## Constraints
- Time budget: 120 min
- Default behavior (local disk) must not change — this is additive, not a replacement
- Allowed tools: file edit, docker, pytest, ruff
