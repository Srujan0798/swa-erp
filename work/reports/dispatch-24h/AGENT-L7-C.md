# AGENT-L7-C

Repo: `/Users/srujansai/Desktop/swa-erp` (main). NO pytest. MAY EDIT: docs/INSTALL_NO_IT.md, docs/DEPLOYMENT_CHECKLIST.md, src/backend/core/storage.py, src/backend/core/config.py.

## Summary of changes

1. **src/backend/core/config.py:35** — `STORAGE_BACKEND: str = "local"` (line 35). Default is local. No forced override.

2. **src/backend/core/storage.py:140-152** — `get_storage()` checks `settings.STORAGE_BACKEND`; `"local"` → `LocalStorage()`, `"minio"` → `MinIOStorage()`, anything else → `ValueError`. MinIO only activates when env var explicitly set.

3. **Compose** — `docker-compose.yml` lines 76, 103: `STORAGE_BACKEND: ${STORAGE_BACKEND:-local}` (defaults local). `docker-compose.prod.yml` has no STORAGE_BACKEND/MINIO_* vars at all — production defaults local. `.env.example` line 27: `STORAGE_BACKEND=local`. Local uploads/ works out of the box; MinIO is opt-in only.

3. **Docs updated** — `docs/INSTALL_NO_IT.md` table row now: "Local `uploads/` directory default; set `STORAGE_BACKEND=minio` + `MINIO_*` env vars to enable MinIO". `docs/DEPLOYMENT_CHECKLIST.md` now has explicit storage paragraph: "Storage: local uploads/ directory is the default; set STORAGE_BACKEND=minio and the MINIO_* env vars to enable MinIO. Local uploads/ works out of the box — do not force MinIO on laptop demo."

## Verification

- `ruff` — all checks passed (exit 0)
- `black` — 2 files unchanged (exit 0)
- `mypy` — pre-existing error `Source file found twice under different module names: "backend.core.config" and "src.backend.core.config"` (exit 2) from `src/backend/__init__.py` dual-import layout — unrelated to storage, not introduced by this task.

## NOT MEASURED

- MinIO integration (env var not set, no MinIO container running) — environmental, not a bug.
- Local uploads/ on production Windows Server (not tested — requires live server) — environmental.

Report written to `work/reports/dispatch-24h/AGENT-L7-C.md`.