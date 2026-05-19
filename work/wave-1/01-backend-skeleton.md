# Task 01 — Backend Skeleton + DB

## What to do
Scaffold the FastAPI backend with config, DB session, exception handlers, request ID middleware, Alembic migrations, and health endpoints. No business endpoints yet — just a runnable skeleton that other tasks build on.

Reference spec: `.specify/specs/wave-1/spec.md` (section: Data model, API surface — only `/healthz` and `/readyz` for now).

## Files to create
- CREATE: `src/backend/__init__.py` (empty)
- CREATE: `src/backend/main.py` (FastAPI app, CORS, middleware, router include)
- CREATE: `src/backend/core/__init__.py` (empty)
- CREATE: `src/backend/core/config.py` (Pydantic BaseSettings reading from env)
- CREATE: `src/backend/core/exceptions.py` (ClientError, ServerError, IntegrationError)
- CREATE: `src/backend/core/middleware.py` (request_id + structlog request logging)
- CREATE: `src/backend/db/__init__.py` (empty)
- CREATE: `src/backend/db/base.py` (SQLAlchemy declarative Base)
- CREATE: `src/backend/db/session.py` (engine, SessionLocal, get_db dependency)
- CREATE: `src/backend/models/__init__.py` (imports for Alembic autogen)
- CREATE: `src/backend/models/user.py` (User model — see schema below)
- CREATE: `src/backend/models/audit_log.py` (AuditLog model)
- CREATE: `src/backend/models/refresh_token.py` (RefreshToken model)
- CREATE: `src/backend/api/__init__.py` (router aggregator)
- CREATE: `src/backend/api/health.py` (/healthz, /readyz)
- CREATE: `src/backend/alembic.ini`
- CREATE: `src/backend/alembic/env.py` (reads DATABASE_URL from settings)
- CREATE: `src/backend/alembic/script.py.mako`
- CREATE: `src/backend/alembic/versions/0001_initial.py` (creates users, audit_log, refresh_tokens)
- CREATE: `tests/wave-1/__init__.py` (empty)
- CREATE: `tests/wave-1/conftest.py` (pytest fixtures: app, client, db_session)
- CREATE: `tests/wave-1/test_skeleton.py` (tests below)

## Files you must NOT touch
- `src/frontend/` (other task)
- `.github/workflows/` (other task)
- `Dockerfile`, `docker-compose.yml` (other task)
- `src/backend/api/auth.py`, `src/backend/api/users.py` (later tasks)
- `requirements.txt` (you may APPEND deps; don't reorder existing)

## Skills to use
- `tdd` (red → green → refactor)
- `fastapi-patterns` (router + dependency injection)
- `sqlalchemy-orm` (2.x declarative style)
- `alembic-migrations` (env.py setup, autogenerate)
- `pydantic-v2` (BaseSettings for config)
- `code-review` (self-review before submit)

## The core problem (inline — no external context needed)

### Tech stack (FIXED)
- Python 3.11
- FastAPI 0.115.*
- SQLAlchemy 2.0.* (NOT 1.x)
- Pydantic 2.8.* (NOT v1)
- pydantic-settings 2.4.*
- PostgreSQL via psycopg2-binary 2.9.*
- Alembic 1.13.*
- structlog 24.4.*

### Settings (`core/config.py`)
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "swa-erp"
    APP_ENV: str = "dev"  # dev | staging | prod
    DEBUG: bool = True
    SECRET_KEY: str = "change-me"  # JWT signing key
    DATABASE_URL: str = "postgresql://swa:swa@localhost:5432/swa_erp"
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_MIN: int = 60
    JWT_REFRESH_TTL_DAYS: int = 30

settings = Settings()
```

### DB session (`db/session.py`)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Models — User
```python
import uuid
from sqlalchemy import String, Boolean, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.backend.db.base import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # admin|pm|designer|auditor|viewer
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped["datetime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
```

### Models — AuditLog
```python
class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    before_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```
(Use `JSONB` from `sqlalchemy.dialects.postgresql` and `INET` from same.)

### Models — RefreshToken
```python
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at: Mapped["datetime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
```

### Main app (`main.py`)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.core.config import settings
from src.backend.core.middleware import RequestIdMiddleware
from src.backend.api.health import router as health_router

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
```

### Middleware (`core/middleware.py`)
- Adds `X-Request-ID` header on response (UUID per request)
- Logs request start/end via structlog with request_id

### Health endpoints (`api/health.py`)
- `GET /healthz` → `{"status": "ok"}` always
- `GET /readyz` → `{"status": "ok", "db": "ok"}` if `SELECT 1` succeeds; else 503

### Alembic initial migration (`alembic/versions/0001_initial.py`)
- Creates `users`, `audit_log`, `refresh_tokens` tables exactly per the schema above
- Adds indexes: `users(email)`, `refresh_tokens(user_id)`, `audit_log(entity_type, entity_id)`, `audit_log(created_at)`

### Tests (`tests/wave-1/test_skeleton.py`)
```python
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_healthz(client: AsyncClient):
    r = await client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

async def test_readyz_db_ok(client: AsyncClient):
    r = await client.get("/readyz")
    assert r.status_code == 200
    assert r.json()["db"] == "ok"

async def test_request_id_header(client: AsyncClient):
    r = await client.get("/healthz")
    assert "x-request-id" in r.headers
    # UUID-ish length
    assert len(r.headers["x-request-id"]) >= 32

async def test_cors_preflight(client: AsyncClient):
    r = await client.options(
        "/healthz",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code in (200, 204)
    assert "access-control-allow-origin" in r.headers

def test_user_model_has_required_columns():
    from src.backend.models.user import User
    cols = {c.name for c in User.__table__.columns}
    assert {"id", "email", "password_hash", "name", "role", "is_active",
            "created_at", "updated_at", "deleted_at", "version"} <= cols
```

### Conftest (`tests/wave-1/conftest.py`)
- Fixture `app` returns FastAPI app
- Fixture `client` returns AsyncClient bound to app (use httpx.ASGITransport)
- Fixture `db_session` returns a transactional session (rollback after test)
- Ensure tests run against a TEST DATABASE (separate env or testcontainers-postgres)

## Acceptance criteria (executable)
- [ ] `cd <project root> && pytest tests/wave-1/test_skeleton.py -v` → all pass
- [ ] `ruff check src/backend/` → clean
- [ ] `black --check src/backend/` → clean
- [ ] `mypy src/backend/` → no errors
- [ ] `alembic upgrade head` applies cleanly to a fresh database
- [ ] `uvicorn src.backend.main:app --port 8000` starts without errors
- [ ] `curl http://localhost:8000/healthz` returns `{"status": "ok"}`

## How to deliver
1. Implement all CREATE files
2. Append needed dependencies to `requirements.txt` (don't reorder)
3. Run the acceptance commands above
4. Write report to `work/reports/wave-1/01-backend-skeleton.report.md` using REPORT_TEMPLATE.md
5. Stop

## Constraints
- Time budget: 90 min
- No business logic — just skeleton + tests
- No additional packages beyond what's listed in `.specify/specs/wave-1/plan.md`
- Match patterns from FastAPI tutorial (https://fastapi.tiangolo.com/tutorial/) — clean, type-hinted, dependency-injected
- Python 3.11 features ok (PEP 604 unions, etc.)
