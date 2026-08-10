# Wave 1 — Foundation: Technical Plan

## Technical decisions

| Decision | Choice | Rationale |
|---|---|---|
| Backend framework | FastAPI 0.115+ | Constitution; great DX; pydantic v2 native |
| ORM | SQLAlchemy 2 + Alembic | Constitution; explicit declarative |
| DB | PostgreSQL 16 | Constitution |
| Auth | JWT (HS256 dev / RS256 prod) | Stateless; simple; well-supported |
| Password hashing | bcrypt cost 12 | Standard; sufficient security |
| Background jobs | Celery + Redis | Used in later waves; install now |
| Frontend framework | React 18 + Vite + TS strict | Constitution |
| UI library | shadcn/ui + Radix | Composable; not a closed framework |
| Routing | React Router v6 | Standard; mature |
| Server state | TanStack Query v5 | Standard; great DX |
| Forms | react-hook-form + zod | Type-safe forms |
| Styling | Tailwind CSS 3 | Constitution |
| HTTP client | fetch wrapper (no axios) | Reduce deps; native is fine |

## Backend file layout (after wave-1)

```
src/backend/
├── main.py                          # FastAPI app entry, CORS, middleware
├── core/
│   ├── config.py                    # Settings (Pydantic BaseSettings)
│   ├── security.py                  # JWT encode/decode, bcrypt
│   ├── deps.py                      # FastAPI dependencies (get_db, get_current_user, require_role)
│   ├── exceptions.py                # Custom exception types
│   ├── middleware.py                # request_id, audit logging
│   └── roles.py                     # Role definitions + permission matrix
├── db/
│   ├── base.py                      # SQLAlchemy Base
│   ├── session.py                   # Engine, SessionLocal, get_db
│   └── repositories/
│       ├── __init__.py
│       ├── user_repo.py
│       └── audit_repo.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── audit_log.py
│   └── refresh_token.py
├── schemas/
│   ├── __init__.py
│   ├── auth.py                      # LoginRequest, TokenResponse, etc.
│   ├── user.py                      # UserCreate, UserRead, UserUpdate, etc.
│   └── common.py                    # Pagination, ErrorResponse
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── user_service.py
│   └── audit_service.py
├── api/
│   ├── __init__.py
│   ├── auth.py                      # /api/auth/* endpoints
│   ├── users.py                     # /api/users/* endpoints
│   └── health.py                    # /healthz, /readyz
├── workers/
│   ├── __init__.py
│   ├── celery_app.py                # Celery config
│   └── tasks.py                     # (empty in wave-1; placeholder)
└── alembic/
    ├── env.py
    ├── script.py.mako
    └── versions/
        └── 0001_initial.py
```

## Frontend file layout (after wave-1)

```
src/frontend/src/
├── main.tsx                         # Entry, QueryClient, BrowserRouter
├── App.tsx                          # Routes
├── components/
│   ├── ui/                          # shadcn primitives (button, input, card, ...)
│   ├── layout/
│   │   ├── AppShell.tsx
│   │   ├── Sidebar.tsx
│   │   └── Topbar.tsx
│   └── auth/
│       └── ProtectedRoute.tsx
├── pages/
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   └── UsersPage.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useUsers.ts
│   └── useCurrentUser.ts
├── lib/
│   ├── api.ts                       # fetch wrapper with token refresh
│   ├── auth.ts                      # token storage (localStorage in dev)
│   └── utils.ts
└── types/
    ├── api.ts                       # API request/response types
    └── domain.ts                    # User, Role
```

## Dependencies to add

### Backend (`requirements.txt`)
```
fastapi==0.115.*
uvicorn[standard]==0.30.*
sqlalchemy==2.0.*
alembic==1.13.*
psycopg2-binary==2.9.*
pydantic==2.8.*
pydantic-settings==2.4.*
python-jose[cryptography]==3.3.*
passlib[bcrypt]==1.7.*
python-multipart==0.0.9
celery==5.4.*
redis==5.0.*
structlog==24.4.*

# dev
pytest==8.3.*
pytest-asyncio==0.24.*
httpx==0.27.*
ruff==0.6.*
black==24.8.*
mypy==1.11.*
```

### Frontend (`package.json` snippet)
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.26.0",
    "@tanstack/react-query": "^5.51.0",
    "react-hook-form": "^7.52.0",
    "zod": "^3.23.0",
    "@hookform/resolvers": "^3.9.0",
    "tailwindcss": "^3.4.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "lucide-react": "^0.428.0"
  }
}
```

(shadcn/ui components added by CLI as needed)

## Migration plan (Alembic)

- `alembic init alembic`
- Configure `env.py` to read DATABASE_URL from settings
- `alembic revision --autogenerate -m "initial: users, audit_log, refresh_tokens"`
- Apply: `alembic upgrade head`

## Seed data (dev only)

After migrations, seed via `scripts/seed_dev.py`:
- One admin user: `admin@swa.local` / `admin123!` (warning printed)
- One PM user: `pm@swa.local` / `pm123!`

Production deployment does NOT run this script.

## Testing strategy

| Test file | Purpose |
|---|---|
| `tests/unit/test_security.py` | bcrypt, JWT encode/decode |
| `tests/unit/test_roles.py` | Permission matrix |
| `tests/integration/test_auth.py` | Login, refresh, logout flows |
| `tests/integration/test_users.py` | CRUD + RBAC |
| `tests/integration/test_audit.py` | Audit log entries created |
| `tests/e2e/test_login_flow.py` | Playwright: login → dashboard |

Acceptance contracts live in `.specify/specs/wave-1/contracts/`.

## Risk register (wave-1 only)

| Risk | Mitigation |
|---|---|
| JWT secret leaks | `.env` gitignored, generated via `openssl rand -hex 32` |
| Alembic autogenerate drift | Always review migration before commit |
| CORS misconfig blocks frontend | Explicit allowlist; tested in dev |
| Postgres not ready when API starts | docker-compose `depends_on` + `healthcheck` |

## Definition of done

- All 5 tasks merged via `/merge`
- All acceptance contracts pass in CI
- `make dev` works on a clean clone
- README + HOW_TO_RUN reflect current state
- `plan/EXECUTION.md` wave-1 marked DONE
- `CHANGELOG.md` updated
- `HANDOFF.md` "Active wave" bumped to wave-2
