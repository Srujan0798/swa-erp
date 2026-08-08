# Task 01 — Wire MinIO/S3 file storage (currently target-state only)

## Result
**DONE** — storage abstraction (`core/storage.py`) with `LocalStorage` + `MinIOStorage`
backends, `get_storage()` factory selected by `STORAGE_BACKEND`, a healthy MinIO service in
`docker-compose.yml`, and the file-writing services (`document_service`, `boq_service`) routed
through the abstraction. Default behavior (`local`) is byte-identical to before. Full suite:
**412 passed** (393 baseline + 19 new wave-31 tests), 0 failures. `ruff` clean. Local-disk files
written before this change are NOT auto-migrated (manual data-migration concern, noted below).
Not committed — orchestrator handles git.

## Item-by-item

### 1. `src/backend/core/config.py`
Added `STORAGE_BACKEND` (`"local"` default), `MINIO_ENDPOINT=localhost:9000`,
`MINIO_ACCESS_KEY`/`MINIO_SECRET_KEY=minioadmin`, `MINIO_BUCKET=swa-erp`, `MINIO_SECURE=False`.

### 2. `src/backend/core/storage.py` (new)
- `StorageBackend(Protocol)` — `save`/`read`/`delete`/`url` as specified in the brief.
- `LocalStorage` — wraps the historical `uploads/<key>` layout; `save` returns the
  `uploads/...`-prefixed relative path that services have always persisted in `file_path`
  columns, so DB values are unchanged under the default backend. `read`/`delete`/`url` also
  accept a bare key OR the stored path string (legacy `uploads/...` prefix), so both old DB rows
  and new writes resolve correctly.
- `MinIOStorage` — `minio` client (minio-py, lazy-imported), auto-creates the bucket.
  **Connection failure raises at construction** (`bucket_exists`/`make_bucket` on init) — no
  silent fallback to local disk.
- `get_storage()` — builds once at first use from `settings.STORAGE_BACKEND`; `local` →
  `LocalStorage`, `minio` → `MinIOStorage`, anything else raises `ValueError` (fail loudly).

### 3. `src/backend/services/document_service.py`
`upload_document` and `create_new_version` now write via
`get_storage().save(f"{project_id}/{stored_name}", file_bytes)` instead of `os.makedirs` +
`open(...)`. Under `local` the stored path is identical to today (`uploads/<pid>/<uuid>_<name>`).
Removed now-unused `import os`.

### 4. `src/backend/services/boq_service.py`
`upload_boq` now writes via `get_storage().save(f"boqs/{project_id}/{uuid}_{file_name}", ...)`
instead of `UPLOAD_DIR`/`Path.write_bytes`. Under `local` the stored path is identical to today
(`uploads/boqs/<pid>/<uuid>_<name>`). Removed `UPLOAD_DIR` constant.

### 5. Download endpoints (to satisfy the byte-identical API round-trip criterion)
There was no way to retrieve a stored file via the API, so two minimal read endpoints were added,
both reading through `get_storage()`:
- `GET /api/documents/{document_id}/download` (`src/backend/api/documents.py`)
- `GET /api/boqs/{boq_id}/download` (`src/backend/api/boqs.py`)

Both return the stored bytes with a `Content-Disposition` attachment header, mirroring the
existing `GET /quotes/{quote_id}/pdf` pattern.

### 6. `docker-compose.yml`
Added `minio` service (minio/minio:latest, `server /data`, dev creds `minioadmin`/`minioadmin`,
port 9000, named volume `minio_data`, curl-based healthcheck on `/minio/health/live` — the
MinIO-documented check, matching the postgres/redis healthcheck style). `backend` gains
`STORAGE_BACKEND=${STORAGE_BACKEND:-local}`, `MINIO_ENDPOINT=minio:9000`,
`MINIO_ACCESS_KEY`/`MINIO_SECRET_KEY` (env-overridable), and `depends_on` minio healthy. Volume
declared under `volumes:`.

### 7. `.env.example`
Filled the empty `MINIO_*` slots with dev defaults (`localhost:9000`, `minioadmin`) and added
`STORAGE_BACKEND=local` with a comment for the two accepted values.

### 8. `requirements.txt`
Added `minio==7.2.7` (the installed version in this environment) so the container image gets the
dependency; used lazily so `local`-only deployments don't require it at import time.

### 9. `tests/wave-31/test_storage_backend.py` (new, 19 tests)
- `LocalStorage`: save/read round-trip, `uploads/`-prefixed return value, reads accept stored
  path + legacy prefixed path, delete (and no-op on missing), url, nested dirs.
- `MinIOStorage` (skips cleanly if MinIO not reachable): save/read round-trip, binary payload,
  delete, presigned url.
- `get_storage()` factory: default local, minio selection, unknown backend raises.
- Fails-loudly: unreachable endpoint raises on `MinIOStorage()` init.
- API round-trips via real endpoints, byte-identical: local document, local BOQ, MinIO document.

## Acceptance criteria check

- [x] **`STORAGE_BACKEND=local` — all existing tests pass unchanged, 393+ baseline**
  Full run with default settings (local): `python3 -m pytest tests/ -q` →
  **412 passed, 0 failed, 42 warnings in 2:26** (393 pre-existing + 19 new). Run with no other
  pytest process active.
- [x] **`STORAGE_BACKEND=minio` against the docker-compose MinIO — uploaded file retrieved
  byte-identical via the API**
  `tests/wave-31/test_storage_backend.py::TestMinIOApiRoundTrip::test_document_upload_download_byte_identical`
  sets `STORAGE_BACKEND=minio`, uploads through `POST /api/projects/{id}/documents`, downloads
  via `GET /api/documents/{id}/download`, asserts exact byte equality — PASSED against the live
  compose MinIO. Local API round-trips (document + BOQ) also PASSED.
- [x] **`docker-compose up -d` — MinIO container healthy**
  `docker compose config -q` → valid (only pre-existing warning: `version` attribute is
  obsolete). `docker compose up -d minio` → `swa-erp-minio-1 Up ... (healthy)` confirmed via
  `docker compose ps minio`. Full-stack `up -d` not run because host postgres/redis already
  bind 5432/6379 (pre-existing environment state, unrelated to this change) and image builds
  would take many minutes; the MinIO acceptance point is verified from the same compose file.
- [x] **New tests cover both backends**
  19 tests in `tests/wave-31/test_storage_backend.py` covering `LocalStorage`,
  `MinIOStorage`, the factory, fails-loudly, and API round-trips for both backends.
- [x] **`ruff check` clean**
  `python3 -m ruff check src/backend/ tests/wave-31/` → **All checks passed!** (covers every
  file touched, including the new test module).

## Honest summary
- What landed is additive: default `local` behavior is unchanged, MinIO is opt-in via
  `STORAGE_BACKEND=minio` + the compose service, and MinIO failures fail loudly at startup.
- **Data migration NOT performed:** files already on local disk from before this change are not
  moved into MinIO — that is a separate, manual migration concern (the brief says so explicitly).
- **Full-stack `docker-compose up -d` not exercised** (port conflicts with host services +
  long image builds); the MinIO service itself was brought up healthy from the compose file and
  the full file validates. I did not touch `docker-compose.prod.yml` (in the "must NOT touch"
  list despite the parenthetical — noted for the orchestrator to confirm intent).
- No existing test needed modification; all 393 baseline tests pass unchanged.

## Time/tokens
- Elapsed: ~45 min wall (implement ~15 min, verify/run suites ~30 min; full suite ×2).
- Tokens: not tracked by this environment.
