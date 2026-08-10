# Wave 1 — Tasks (Ordered)

These 5 tasks can be dispatched mostly in parallel after Task 1 completes (which scaffolds the backend skeleton).

## Dependency graph

```
Task 1 (Backend skeleton + DB)
   │
   ├──→ Task 2 (Auth + RBAC)
   ├──→ Task 3 (Users API)
   ├──→ Task 5 (CI + Docker)         ← can start without Task 1
   │
   └──→ Task 4 (Frontend shell + auth flow)
            ↑
            └─── needs Task 2 endpoints to exist
```

## Tasks

### Task 1 — Backend skeleton + DB
**File:** `work/wave-1/01-backend-skeleton.md`
**Owner:** Backend worker (Python)
**Output:**
- `src/backend/{main.py, core/, db/, models/{user, audit_log, refresh_token}, alembic/}` scaffolded
- Initial Alembic migration applied
- `/healthz` and `/readyz` working
**Acceptance:** `pytest tests/wave-1/test_skeleton.py` passes; `uvicorn` starts cleanly.

### Task 2 — Auth + RBAC
**File:** `work/wave-1/02-auth-rbac.md`
**Owner:** Backend worker (Python)
**Depends on:** Task 1
**Output:**
- `core/security.py` (bcrypt + JWT)
- `core/roles.py` (role + permission matrix)
- `core/deps.py` (`get_current_user`, `require_role`)
- `api/auth.py` (login, refresh, logout, me)
- `services/auth_service.py`
**Acceptance:** `pytest tests/wave-1/test_auth.py` passes (all 5 US scenarios covered).

### Task 3 — Users API
**File:** `work/wave-1/03-users-api.md`
**Owner:** Backend worker (Python)
**Depends on:** Task 1, Task 2 (uses RBAC)
**Output:**
- `api/users.py` (full CRUD)
- `services/user_service.py`
- `schemas/user.py`
- Audit log entries on every mutation
**Acceptance:** `pytest tests/wave-1/test_users.py` passes (CRUD + RBAC + audit).

### Task 4 — Frontend shell + auth flow
**File:** `work/wave-1/04-frontend-shell.md`
**Owner:** Frontend worker (TypeScript / React)
**Depends on:** Task 2 (endpoints exist)
**Output:**
- `src/frontend/` scaffolded with Vite + React + TS + Tailwind + shadcn/ui
- Pages: `/login`, `/dashboard`, `/users` (admin only)
- API client with auto-refresh
- `ProtectedRoute` wrapper
- Layout with sidebar + topbar
**Acceptance:** `pytest tests/wave-1/e2e/test_login.py` (Playwright) passes.

### Task 5 — CI + Docker
**File:** `work/wave-1/05-ci-docker.md`
**Owner:** Infra worker (any stack-aware)
**Depends on:** none (can run in parallel)
**Output:**
- `Dockerfile` (backend)
- `Dockerfile.frontend` (frontend)
- `docker-compose.yml` (backend + frontend + postgres + redis + adminer)
- `.github/workflows/ci.yml`, `test.yml`, `security.yml`
- `.pre-commit-config.yaml`
**Acceptance:** `docker compose up` brings everything up; CI passes on push.

## Total

5 tasks. Tasks 1, 5 can start immediately in parallel. Tasks 2 & 3 chain after 1. Task 4 chains after 2. Expected total wall time with 3–4 parallel workers: ~1–2 days.
