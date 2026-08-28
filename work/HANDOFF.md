# Handoff — post-professional-grade close

**Last updated:** 2026-08-28 (wave-47 seal)
**Engine version:** v1.0.1
**Close HEAD:** `96852fe` (wave-47 step 2: 401/403 fix) on worktree `w47`.

## State of the repo

| Area | Status |
|---|---|
| Backend | 572 passed / 1 skipped / **0 failed** · 85% coverage · ruff/mypy/black clean |
| Frontend | 523 vitest passed / 0 failed · tsc/eslint/vite-build clean |
| Migrations | Single Alembic head `0033` · model↔migration drift sweep done |
| CI | `.github/workflows/ci.yml` gates ruff/black/mypy/pytest/vitest/tsc/eslint/vite |
| Storage | Local default; MinIO opt-in via `STORAGE_BACKEND=minio` |
| Workers | Celery app `src/backend/workers/` with async export endpoints |
| Evals | `evals/` scaffold — 5 task specs + 3 graders + GitHub Actions |

## Secrets / environment

- **Docker available.** `docker compose up -d postgres redis minio` brings up the
  full stack. Test DB: `swa_erp_test` (create manually:
  `psql -h localhost -U swa -d postgres -c "CREATE DATABASE swa_erp_test OWNER swa;"`).
- **Local Postgres only** (no Docker): tests target
  `postgresql://swa:***@localhost:5432/swa_erp_test`.
- `SECRET_KEY` — set to `"test-secret-key"` for tests; production value is
  external (Viraj / no IT dept). See `docs/INSTALL_NO_IT.md` for no-IT-dept install.

## What is external (DO NOT block on)

1. **Server access / deploy** — Viraj holds the server facts (8 items). No IT
   department on the client side. `docs/IT_BRIEF.md` has the full brief.
2. **Excel data migration** — owner pending Viraj's freeze date. The importer
   (`make migrate-data`) is ready (dry-run by default).
3. **Client-box load test** — the Locust runs in `docs/PERFORMANCE.md` were on
   the dev machine, not the client's box.

## What to do next

- If you need to re-verify, run `python3 -m pytest tests/ -q --tb=no` from the
  repo root with a Postgres + Redis running.
- Gate commands are in `work/wave-47/01-final-seal.md` step 1.
- This is the final wave. The project is **CLOSED for internship submission**.
