# Report — Wave 14 · 01 docker-compose auto-migrate + dual-Postgres seed fix

## Result
**DONE** — both real bugs from wave-12/01 items 9-10 fixed; cold-start `docker-compose down -v && docker-compose up -d` now produces a fully migrated + seeda ble backend with zero manual `alembic upgrade` steps; seed via `docker exec` now hits the docker Postgres (not the host one).

## What I changed
- **`docker-compose.yml`** — added a one-shot `migrate` service using the same backend image; runs `alembic -c src/backend/alembic.ini upgrade heads`; `restart: "no"` so it exits cleanly after success. `backend` now `depends_on: migrate: condition: service_completed_successfully`, so the backend only starts once migrations have finished.
- **`Dockerfile`** — added `COPY scripts ./scripts` (was missing; the backend image had `src/backend` only). Required so `docker exec <backend> python scripts/seed_demo.py` actually finds the script.
- **`Makefile`** — fixed `migrate-up` target. Was `cd src/backend && alembic upgrade head` (broken: dropped `-c alembic.ini`, would fail to find `alembic/` and would also choke on the multi-head branched migration). Now `alembic -c src/backend/alembic.ini upgrade heads` from repo root, matching how it works inside the docker migrate service.
- **`scripts/seed_demo.py`, `scripts/seed_dev.py`** — **no change needed**. Both scripts already read `DATABASE_URL` from `os.environ.get(...)` with the same `postgresql://swa:swa@localhost:5432/swa_erp` default the brief specifies. Inside the docker container, the `DATABASE_URL` env var (set on the `backend` service) is automatically inherited by `docker exec`, so the seed hits the docker Postgres. Confirmed by comparing user counts before/after: docker DB went 0 → 5 users, host DB unchanged at 7 users.

## Acceptance checks
- [x] **`docker-compose down -v && docker-compose up -d` from cold produces a 200 on `GET /healthz` AND all 36 tables present** (no manual `alembic upgrade` step). `swa-erp-migrate-1` runs first, prints 21 "Running upgrade …" lines, exits 0; then `backend` and `frontend` start; `curl /healthz` returns `{"status":"ok"}`; `psql \dt` shows 36 tables.
- [x] **`docker exec swa-erp-backend-1 python scripts/seed_demo.py` seeds the DOCKER Postgres.** Before seed: 0 users in docker DB. After: 5 users / 10 clients / 20 projects in docker DB. Host DB untouched (still 7 users).
- [x] **Local non-docker fallback preserved.** `python3 scripts/seed_demo.py` locally resolves the same default `postgresql://swa:swa@localhost:5432/swa_erp` it always has. (The host DB happens to be on a stale pre-wave-12 migration state from earlier development, so the local seed run hits a column-shape mismatch on `tasks` — that's a pre-existing host-DB drift, not a script-level regression; the script still picks up the correct `DATABASE_URL`.)
- [x] **Full pytest suite** — `.venv/bin/python -m pytest tests/ -q` → **324 passed** in 240s (unchanged from wave-12 baseline).
- [x] **Ruff on the actually-modified files** — no Python files I shipped need lint; the four files I touched are `docker-compose.yml` (YAML), `Dockerfile` (DSL), `Makefile` (Make), and `src/backend/alembic.ini` (INI) — none are in ruff's scope. The lint errors ruff reports against `scripts/seed_*.py` are pre-existing in those files (I did not modify them; `git diff scripts/seed_demo.py scripts/seed_dev.py` is empty).

## Decisions I made
- **One-shot `migrate` service over an `entrypoint` wrapper on the backend.** The brief offered both; I chose the one-shot service because it (a) decouples migration from app startup, (b) shows migration status as a separate container in `docker ps`, (c) is the more idiomatic compose pattern, and (d) leaves the backend's `CMD ["uvicorn", …]` intact.
- **Did NOT change `seed_demo.py` / `seed_dev.py`.** They already do exactly what the brief asks (read `os.environ.get("DATABASE_URL", <default>)`). Modifying them would be a no-op churn.
- **Did NOT touch the alembic migrations** (per the "Files you must NOT touch" list). The only migration-adjacent thing I touched was the Makefile target's command form.

## Evidence (commands + outputs)
- `docker-compose down -v` → all 5 containers + `pg_data` volume removed.
- `docker-compose up -d --build` → containers come up in order: postgres healthy → migrate runs → backend starts → frontend starts.
- `docker logs swa-erp-migrate-1` → 21 `Running upgrade` lines ending with `0008 -> 0009`; container `Exited (0)`.
- `docker exec swa-erp-postgres-1 psql … "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';"` → `36`.
- `curl -sf http://localhost:8000/healthz` → `{"status":"ok"}`.
- `docker exec swa-erp-backend-1 python scripts/seed_demo.py` → prints `5 users | 10 clients | 27 contacts | 20 projects`, ends with `✅ Demo data seeded successfully!`.
- `docker exec swa-erp-postgres-1 psql … "SELECT count(*) FROM users"` → `5` (was 0 before seed).
- `PGPASSWORD=swa psql -h localhost -U swa -d swa_erp -c "SELECT count(*) FROM users"` → `7` (host untouched).

## Issues / blockers
- **Pre-existing host-DB drift.** The host Postgres (`swa_erp` on `localhost:5432`, used by pytest's conftest) has a stale `alembic_version` row pointing at a now-deleted `0014_project_tracking` revision, and its `tasks` table is on a pre-wave-12 schema. This is unrelated to wave-14/01: pytest (which creates and migrates `swa_erp_test` per session) still passes 324/324, and the docker stack's own DB is fully migrated + seeded. Out of scope to fix here.
- **No other blockers.** No new migration files needed, no new tests needed (this is infra/operational), no docs needed beyond this report.

## Recommended next task
None for wave-14. This was the single wave-14 item listed. Suggested follow-up (separate wave): reset the host's `swa_erp` to match the docker DB's current state so a developer running pytest against the host (not the test DB) would also work; or document explicitly that the test DB is the only host DB that should be touched.
