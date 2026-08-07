# Runbook

Operational guide for running and troubleshooting swa-erp.

## Local dev — first time setup
```bash
git clone <repo>
cd swa-erp
cp .env.example .env
# Generate a real SECRET_KEY:
python3 -c "import secrets; print(secrets.token_hex(32))" >> /tmp/secret
# Edit .env and paste the SECRET_KEY value

# Start services
docker-compose up postgres redis adminer -d

# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd src/backend
alembic upgrade head
cd ../..
uvicorn src.backend.main:app --reload --port 8000

# Frontend (separate terminal)
cd src/frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Seeding dev data
```bash
python3 scripts/seed_dev.py
# Creates admin@swa.local / admin123! and pm@swa.local / pm123!
```

## Running tests
```bash
make test                  # all tests
make test-wave wave=1      # wave-1 only
make test-e2e              # Playwright E2E (requires backend + frontend running)
```

## Running the full stack via Docker
```bash
docker-compose up --build
```
Then `http://localhost:3000` (frontend), `http://localhost:8000/docs` (API), `http://localhost:8080` (adminer).

## Common failures

### Postgres connection refused
- Check `docker-compose ps` — is postgres healthy?
- Check `DATABASE_URL` in `.env` matches the docker-compose service name (`postgres`) when running in containers, or `localhost` when running backend on host
- `docker-compose logs postgres` for clues

### Migrations not applied
```bash
cd src/backend
alembic current        # see current version
alembic upgrade head   # apply
```

### JWT decode errors
- Did `SECRET_KEY` change between sessions? Tokens issued with old key fail.
- Regenerate: clear tokens, log in again

### Frontend can't reach backend
- CORS: backend's `CORS_ORIGINS` must include the frontend origin
- Proxy: in dev, Vite proxies `/api` → `http://localhost:8000` (see `vite.config.ts`)

### Tests fail with "table doesn't exist"
- Test DB not migrated. `conftest.py` should handle this via fixture; if it doesn't:
  ```bash
  DATABASE_URL=postgresql://swa:swa@localhost:5432/swa_erp_test alembic upgrade head
  ```

## Production deployment (later wave)
Documented in `docs/deployment.md` (rewritten 2026-07-21 — no longer a wave-8 placeholder).

## Backups
**Corrected 2026-08-07** — wave-19 landed and wave-27 hardened it: real, tested backup
automation exists and is documented in `docs/runbook_backup_restore.md`. Use that document;
do not treat backups as manual.

- Postgres: `make backup-db` → `scripts/backup_db.sh` (pg_dump → timestamped `.sql.gz`,
  retention-pruned)
- File uploads: `make backup-files` → `scripts/backup_files.sh` (tar of `uploads/` at repo
  root, retention-pruned)
- Restore: `make restore-db file=<path>` → `scripts/restore_db.sh` (prints target before
  prompting; `--yes` for CI)
- Verified by `tests/wave-19/test_backup_scripts.py` (full round-trip) and
  `tests/wave-27/test_backup_script_safety.py`
- Audit log: never deleted; archived to cold storage after N years (TBD by legal)

## Health checks
- `/healthz` — liveness (just returns ok)
- `/readyz` — readiness (checks DB connection)
- `/metrics` — Prometheus (later wave)
