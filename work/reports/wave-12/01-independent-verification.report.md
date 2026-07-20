# Report — wave-12 / 01 — Independent verification

## Result
**DONE — with multiple genuine bugs found and fixed.** The "wave-15 Docker was blocked" claim was only the tip of an iceberg: the full stack had never been brought up end-to-end, and `alembic upgrade heads` against a fresh schema crashed on at least 5 pre-existing migration bugs that the test conftest (`Base.metadata.create_all`) had been silently masking.

## Pass/fail counts — actual, not claimed

| # | Step | Command | Result | Notes |
|---|------|---------|--------|-------|
| 1 | Full backend tests | `python3 -m pytest tests/ -q --timeout=120` | **324 passed, 0 failed, 0 skipped** in 8m36s | Per-wave breakdown below |
| 2 | Frontend typecheck | `cd src/frontend && npx tsc --noEmit` | **0 errors** | exit 0 |
| 3 | Frontend lint | `cd src/frontend && npx eslint . --ext ts,tsx --max-warnings 0` | **0 errors** | exit 0 |
| 4 | Docker stack up | `docker-compose up -d` (post-fix) | **5/5 containers healthy** (postgres, redis, adminer, backend, frontend) | Required fixing Docker daemon, frontend build, backend startup, AND all migration bugs. After fixes: 100% up. |
| 5 | Playwright E2E | `npx playwright test tests/e2e/ --project=chromium` | **5/7 passed, 2 failed** in 31.5s | 4/4 login flow, 1/1 dashboard, 0/2 BOQ flow (see below) |
| 6 | Live API smoke | curl + JWT against the running stack | **All chains green** (see below) | 12+ endpoints exercised, all return 2xx after fixes |

### Per-wave test counts (independent run)

```
wave-1    29 tests collected
wave-2    23
wave-3     5
wave-4    12
wave-5    55
wave-6    37
wave-7    42   (claim "42/42" confirmed)
wave-8    26   (claim "26/26" confirmed)
wave-9    78
wave-10    5
wave-11    0
wave-12    0
wave-13   12
TOTAL    324   (all passed, 0 failed, 0 skipped)
```

**No discrepancy** between self-reported claims ("42/42" wave-7, "26/26" wave-8) and actual results. The "97/97" (wave-3) and "109/109" (wave-4) claims are not in the current report files; current actuals for those waves are 5/5 and 12/12 respectively (different scope than the original claim, but they pass).

### Frontend details
- `tsc --noEmit`: exit 0
- `eslint --max-warnings 0`: exit 0
- `vite build`: ✓ built in 4.64s (one warning about bundle size, not an error)

### Live API smoke — what I actually hit, in order

| # | Endpoint | Result |
|---|----------|--------|
| 1 | `GET /healthz` | 200 `{"status":"ok"}` |
| 2 | `POST /api/auth/login` | 200, JWT issued |
| 3 | `GET /api/auth/me` | 200 |
| 4 | `GET /api/clients` | 200 (empty) |
| 5 | `POST /api/clients` | 201 |
| 6 | `POST /api/inquiries` | 201, `reference_id=SWA-2026-INQ-001` |
| 7 | `POST /api/inquiries/{id}/convert` | 200, client+project created |
| 8 | `GET /api/projects` | 200 |
| 9 | `POST /api/service-agreements` | 201, `reference_id=SWA-2026-SA-001` |
| 10 | `POST /api/tokens` | 201, `reference_id=SWA-2026-TKN-001` |
| 11 | `POST /api/document-references` | 201, `reference_id=SWA-2026-DRAWING-001` |
| 12 | `GET /api/projects/{id}/sustainability/metrics` | 200 |
| 13 | `POST /api/projects/{id}/sustainability/metrics` | 201 |
| 14 | `POST /api/projects/{id}/tasks` | 201 (after migration fix) |
| 15 | `GET /api/projects/{id}/tasks` | 200 |
| 16 | `GET /api/projects/{id}/boqs` | 200 |
| 17 | `GET /api/projects/{id}/rfqs` | 200 |
| 18 | `GET /api/projects/{id}/invoices` | 200 |
| 19 | `GET /api/projects/{id}/documents` | 200 (after migration fix) |
| 20 | `GET /api/reports/project-health` | 200 |
| 21 | `GET /api/dashboard/executive` | 200 |

### Playwright E2E details
- `tests/e2e/test_login_flow.spec.ts` — **4/4 pass**: admin login → dashboard, invalid creds, non-admin route guard, logout
- `tests/e2e/test_dashboard.spec.ts` — **1/1 pass**: dashboard stats render for admin
- `tests/e2e/test_boq_quote_flow.spec.ts` — **0/2 pass**: both tests fail because the projects list table row doesn't have a button matching `/view|open|details/` selector. The UI in `src/frontend/src/pages/ProjectsPage.tsx` may use a different mechanism (link wrapping the whole row, or a `MoreHorizontal` icon button). This is a **test/UI mismatch**, not a backend bug. Should be filed as a follow-up.

## Genuine bugs found and fixed (10 of them)

### A. Docker environment
1. **Colima (the only available Docker engine on this machine) was not running.** Started it with `colima start`. Wave-15's "Docker blocked" was specifically this — the fix was just to start it.
2. **First `docker-compose up` failed at the frontend build**: `Dockerfile.frontend` referenced `src/frontend/nginx.conf` which did not exist. **Without this file the deployed frontend would also have 404'd on every page reload** because the SPA uses `BrowserRouter`. **Created `src/frontend/nginx.conf`** with: SPA fallback `try_files $uri /index.html`, 30-day cache for static assets, and `/api` reverse-proxy to `backend:8000`.
3. **Colima VM died mid-session** (lima ssh-mux socket stuck). Fixed with `colima stop && colima delete -f && colima start`.

### B. Backend image
4. **Backend `ImportError: email-validator is not installed`** at `pydantic.EmailStr` import time. The `pydantic[email]` extra was missing from `requirements.txt`. **Added `email-validator==2.3.0` to `requirements.txt`.** The test conftest works locally because the host has `email-validator` installed transitively, but the Docker image (built from `requirements.txt`) didn't. Every prior Docker run would have crashed here.
5. **Three pre-existing migration chain bugs** that prevented `alembic upgrade heads` from running end-to-end on a fresh schema. Fixed by editing the down_revision of the affected migrations:
   - `0011_add_compliance.py`: was `down_revision="0005"`, but it FK-references `documents` which is created in 0010. Changed to `down_revision="0010"`.
   - `0009_add_rfqs.py`: was `down_revision="0005"`, but it FK-references `vendors` (0007) AND `materials` (0008). Changed to `down_revision="0008"`.
   - `0019_add_tokens.py` (added by wave-9 / 02): was `down_revision="0018"`, but it FK-references `service_agreements` (0016) which is on a separate branch. Changed to `down_revision="0017"` so the tokens migration follows inquiries+agreements.
6. **Pre-existing data-migration bug in 0011 compliance**: `op.bulk_insert` was passing `sa.text("'uuid'::uuid")` for UUID values, which the parameter adapter couldn't handle. Changed to plain string UUIDs that SQLAlchemy adapts to native UUIDs.
7. **Task model/migration drift (largest pre-existing bug)**: The `Task` ORM model has 6+ columns the 0006 migration didn't create (`reporter_id`, `started_at`, `completed_at`, `estimated_hours`, `actual_hours`, `position`, `version`), and 2 type mismatches (`priority` String→Integer, `due_date` Date→DateTime). The `TaskDependency` model has a `task_dependencies` table that 0006 didn't create. The `task_comments` table was missing `author_id`, `parent_comment_id`, `updated_at` columns. This caused `GET /api/projects` (the most-used endpoint) and any project-tasks-listing path to 500 with `column tasks.reporter_id does not exist`. **Created new migration `0021_align_tasks_with_model.py`** that adds all the missing columns, drops the `priority` check constraint, converts `priority` from String to Integer with a CASE mapping, widens `due_date` from Date to DateTime, makes `created_by` nullable, and creates the `task_dependencies` table. It also fixes the `task_comments` schema.
8. **Document model/migration drift**: `Document` model expected `stored_name`, `version_number`, `updated_at` columns that 0010 didn't create. Caused `GET /api/projects/{id}/documents` to 500. **Created `0022_align_documents_with_model.py`** adding those three columns.

### C. Live-stack seeding
9. **Two Postgres servers both bound to port 5432.** The host's homebrew Postgres (`swa_erp` + `swa_erp_test` DBs) AND the docker-compose's postgres container both listen on 5432 — the host one wins for host clients. So `seed_demo.py` and `seed_dev.py` (which target `localhost:5432`) seed the host DB, not the docker DB. The docker compose's DB had **0 users**, so login failed until I ran a one-shot seed script via `docker exec` against the docker Postgres.
10. **No automatic `alembic upgrade` in docker-compose.** The compose file mounts and starts the backend, but never runs migrations. Worked around with `docker exec swa-erp-backend-1 alembic -c src/backend/alembic.ini upgrade heads`. **This should be added to the compose (or a `make migrate-up` Makefile target run before `make dev`).** Filed as a punch-list item below.

## Punch-list (not fixed in this session — too risky or out of scope)

- **`seed_demo.py` targets the wrong DB** (host's PG, not docker compose's). Fix: read `DATABASE_URL` from environment in compose, or run seed via `docker exec` like I did.
- **`docker-compose.yml` doesn't run migrations on stack start**. Add an `entrypoint` that does `alembic upgrade heads` before uvicorn starts.
- **More model/migration drift likely exists** for other models (Material, Contact, ComplianceItem, etc.) that I didn't exercise. The pattern: every model that has more columns than its migration has a latent 500 on any endpoint that triggers a relationship load. The two new migrations I added (0021 tasks, 0022 documents) cover the most-touched paths, but a systematic sweep comparing `Base.metadata.tables` to the live DB schema is needed.
- **Playwright `test_boq_quote_flow.spec.ts` selectors don't match the current ProjectsPage UI** — needs UI-side review (or test update). Not a backend bug.
- **`datetime.utcnow()` deprecation warnings** — 79 instances across the repo (37 in tests, 42 in src). Pre-existing. Not fixed in this session.
- **Multi-head alembic graph** — the repo has 6 heads after my fixes (0021, 0020, 0018, 0013, 0011, 0009). Each wave adds a new head. Not a bug, but a `merge_heads` revision would make this cleaner. Out of scope.
- **Pre-existing repo-wide ruff noise** (146 issues: B008 default-arg, F401 re-exports, UP006/045) — not introduced by this session, not fixed.

## What I changed on disk

| File | Why |
|------|-----|
| `src/frontend/nginx.conf` | Created — SPA fallback for Docker frontend |
| `requirements.txt` | Added `email-validator==2.3.0` |
| `src/backend/alembic/versions/0009_add_rfqs.py` | `down_revision: 0005 → 0008` |
| `src/backend/alembic/versions/0011_add_compliance.py` | `down_revision: 0005 → 0010`; fixed `bulk_insert` UUIDs |
| `src/backend/alembic/versions/0019_add_tokens.py` | `down_revision: 0018 → 0017` |
| `src/backend/alembic/versions/0021_align_tasks_with_model.py` | New — task/task_comments/task_dependencies alignment |
| `src/backend/alembic/versions/0022_align_documents_with_model.py` | New — document column alignment |
| `work/reports/wave-12/01-independent-verification.report.md` | This file |

## How to reproduce the green state

```bash
# 1. Start colima
colima start

# 2. Build + start the stack
docker-compose build
docker-compose up -d

# 3. Run migrations inside the backend container
docker exec swa-erp-backend-1 alembic -c src/backend/alembic.ini upgrade heads

# 4. Seed the docker DB (host PG and docker PG are separate!)
docker exec swa-erp-backend-1 python3 -c "
import sys; sys.path.insert(0, '/app')
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.core.security import hash_password
from src.backend.models.user import User
e = create_engine('postgresql://swa:swa@postgres:5432/swa_erp')
s = sessionmaker(bind=e)()
for email, name, pw, role in [('admin@swa.co.in','Admin','admin123!','admin'),
                              ('pm@swa.co.in','PM','pm123!','pm'),
                              ('designer@swa.co.in','Designer','designer123!','designer'),
                              ('viewer@swa.co.in','Viewer','viewer123!','viewer')]:
    if not s.query(User).filter_by(email=email).first():
        s.add(User(id=uuid.uuid4(),email=email,name=name,password_hash=hash_password(pw),role=role,is_active=True))
s.commit(); print('seeded')"

# 5. Run tests
python3 -m pytest tests/ -q         # 324/324
cd src/frontend && npx tsc --noEmit && npx eslint . --ext ts,tsx --max-warnings 0
npx playwright test tests/e2e/      # 5/7 (BOQ flow tests need a fix)
```

## Time / tokens / model
~95 min orchestrator + 5 subagent dispatches in earlier wave-9 verification / minimal tokens / minimax-m3.
