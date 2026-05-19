# Wave 1 — Foundation: Spec

## Goal
Ship a bootable backend + frontend with auth, RBAC, users, and an empty app shell. No business features yet. By the end of wave-1, a developer can `make dev`, log in as admin, see the dashboard shell, and create another user.

## User stories

### US-1.1 — As any user, I can log in
**Given** I have valid credentials
**When** I POST `/api/auth/login` with `{email, password}`
**Then** I receive `{access_token, refresh_token, user}` and the access token is valid for 1 hour.

### US-1.2 — As an admin, I can create users
**Given** I am logged in as an admin
**When** I POST `/api/users` with `{email, name, password, role}`
**Then** the user is created and I can see them in `/api/users` list.

### US-1.3 — As any user, I see the dashboard after login
**Given** I have just logged in
**When** my browser is redirected to `/dashboard`
**Then** I see my name, role, and a placeholder welcome card (real widgets come in later waves).

### US-1.4 — As a non-admin, I cannot list users
**Given** I am logged in as a PM (not admin)
**When** I GET `/api/users`
**Then** I receive `403 Forbidden`.

### US-1.5 — As any user, my JWT expires after 1h
**Given** I logged in 61 minutes ago and didn't refresh
**When** I make any authenticated request
**Then** I receive `401 Unauthorized` and the frontend redirects me to login.

## In scope (wave-1 only)

- FastAPI backend skeleton with config, db session, exception handlers, request_id middleware
- Alembic migrations setup; first migration creates `users` and `audit_log` tables
- Auth endpoints: `/auth/login`, `/auth/refresh`, `/auth/me`, `/auth/logout`
- Users endpoints: `/users` (list, create), `/users/{id}` (read, update, delete)
- RBAC enforced via FastAPI dependency `require_role(...)`
- Roles seeded: `admin`, `pm`, `designer`, `auditor`, `viewer`
- React frontend with Vite, TS strict, Tailwind, shadcn/ui base components
- Frontend pages: `/login`, `/dashboard`, `/users` (admin only)
- API client with auto-refresh interceptor
- Docker Compose: backend + frontend + postgres + redis
- Health endpoints: `/healthz`, `/readyz`

## Out of scope (wave-1)
- Clients, projects, BOQ, quotes, tasks, vendors, inventory, documents, compliance, timesheets, invoices, reports — ALL later waves
- Password reset email — wave-2
- Social login — never (constitution)
- Multi-tenant — out per constitution

## Success criteria

- [ ] `make dev` starts all services successfully
- [ ] Login flow works end-to-end (frontend → backend → DB → JWT)
- [ ] Admin can create a PM user via UI; PM can log in but gets 403 on `/api/users`
- [ ] JWT expires after 1h; refresh token works
- [ ] `pytest tests/wave-1/` passes 100%
- [ ] `make lint` clean
- [ ] CI green on push
- [ ] Docker images build cleanly

## Performance budgets

- Login response: < 200ms (P95)
- /users list: < 100ms (P95) for up to 100 users
- Dashboard load: < 500ms (P95)
- DB queries per request: ≤ 3 (excluding migrations)

## Data model (wave-1)

```sql
-- users
id           UUID PK
email        TEXT UNIQUE NOT NULL
password_hash TEXT NOT NULL
name         TEXT NOT NULL
role         TEXT NOT NULL CHECK (role IN ('admin','pm','designer','auditor','viewer'))
is_active    BOOLEAN NOT NULL DEFAULT TRUE
created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
deleted_at   TIMESTAMPTZ NULL
version      INT NOT NULL DEFAULT 1

-- audit_log
id           BIGSERIAL PK
user_id      UUID NULL REFERENCES users(id)
action       TEXT NOT NULL          -- e.g., "user.create", "user.update"
entity_type  TEXT NOT NULL          -- e.g., "user"
entity_id    UUID NULL
before_json  JSONB NULL
after_json   JSONB NULL
ip_address   INET NULL
user_agent   TEXT NULL
created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()

-- refresh_tokens
id           UUID PK
user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
token_hash   TEXT NOT NULL
expires_at   TIMESTAMPTZ NOT NULL
created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
revoked_at   TIMESTAMPTZ NULL
```

## API surface (wave-1)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/login` | none | Returns access + refresh tokens |
| POST | `/api/auth/refresh` | refresh token | Returns new access token |
| POST | `/api/auth/logout` | bearer | Revokes refresh token |
| GET  | `/api/auth/me` | bearer | Returns current user |
| GET  | `/api/users` | bearer + admin | Lists users (paginated) |
| POST | `/api/users` | bearer + admin | Creates user |
| GET  | `/api/users/{id}` | bearer + admin or self | Reads user |
| PATCH| `/api/users/{id}` | bearer + admin or self | Updates user |
| DELETE | `/api/users/{id}` | bearer + admin | Soft-deletes user |
| GET  | `/healthz` | none | Liveness check |
| GET  | `/readyz` | none | Readiness check (DB connection) |
