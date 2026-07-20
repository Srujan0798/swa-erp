# Task 01 — Docker Compose auto-migrate + fix dual-Postgres seed bug

## What to do
Two real bugs found during independent verification (`work/reports/wave-12/01-independent-verification.report.md`,
items 9-10): (1) `docker-compose up` never runs Alembic migrations, so a fresh stack has no
schema until someone manually runs `alembic upgrade heads` inside the container; (2) the seed
scripts connect to `localhost:5432`, which on a dev machine running both a host Postgres AND the
docker-compose Postgres silently seeds the WRONG database (the host one), leaving the docker
Postgres with zero users and login broken.

## Files to modify
- MODIFY: `docker-compose.yml` — add a migration step before the backend starts serving traffic
- MODIFY: `scripts/seed_demo.py`, `scripts/seed_dev.py` (or wherever these live — check `scripts/`)
  — read `DATABASE_URL` from environment instead of hardcoding `localhost:5432`
- MODIFY: `Makefile` — add a `make migrate-up` target if one doesn't exist, wire it into `make dev`

## Files you must NOT touch
- Alembic migration version files themselves (`src/backend/alembic/versions/*.py`) — this task
  is about running migrations reliably, not changing what they do
- `src/backend/models/`

## The core problem (inline)
### docker-compose fix
Add either:
- an `entrypoint`/`command` wrapper on the backend service that runs
  `alembic -c src/backend/alembic.ini upgrade heads && uvicorn ...` (simplest), or
- a dedicated one-shot `migrate` service in the compose file that the backend `depends_on`
  with `condition: service_completed_successfully`

Prefer the entrypoint wrapper unless the compose file already has a pattern for one-shot init
containers — match whatever's more consistent with the existing file structure.

### Seed script fix
Both seed scripts currently hardcode `postgresql://...@localhost:5432/...` (verify exact
connection string in the files). Change to read `os.environ.get("DATABASE_URL", <same default
as before for local non-docker use>)` so:
- Running `python scripts/seed_demo.py` locally (no Docker) still works exactly as before (falls
  back to the same default)
- Running it via `docker exec <container> python scripts/seed_demo.py` picks up the container's
  own `DATABASE_URL` env var (already set for the backend service in docker-compose.yml) and
  seeds the correct (docker) Postgres instance

## Acceptance criteria
- [ ] `docker-compose down -v && docker-compose up -d` (fresh volumes) results in a backend that
  responds 200 on `GET /healthz` AND has all tables present (verify with
  `docker exec <postgres-container> psql -U swa -d swa_erp -c '\dt'` showing all expected tables)
  without any manual `alembic upgrade` step
- [ ] `docker exec <backend-container> python scripts/seed_demo.py` seeds the DOCKER Postgres
  (verify by querying users table inside the docker postgres container, not the host one)
- [ ] Running the same seed script locally without Docker still works against the local dev DB
- [ ] `python3 -m pytest tests/ -q` — full suite still passes, no regressions

## How to deliver
1. Implement both fixes
2. Tear down and rebuild the full docker stack from scratch to prove the fix works cold
3. Write report to `work/reports/wave-14/01-docker-migrations-and-seed-fix.report.md`
4. Stop

## Constraints
- Time budget: 60 min
- Don't change the default connection string used for non-Docker local dev — only add the
  environment-variable override path
- Allowed tools: file edit, docker, docker-compose, psql, pytest
