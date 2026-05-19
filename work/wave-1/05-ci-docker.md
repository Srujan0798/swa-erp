# Task 05 — CI + Docker

## What to do
Set up Docker (backend + frontend), docker-compose for local dev (with postgres + redis + adminer), GitHub Actions CI workflows, and pre-commit hooks. This task can run in parallel with all other wave-1 tasks because it doesn't touch their files.

Reference spec: `.specify/specs/wave-1/spec.md` — "Docker Compose" + "CI green on first push".

## Files to create
- CREATE: `Dockerfile` (backend; multi-stage; python 3.11-slim)
- CREATE: `Dockerfile.frontend` (frontend; multi-stage; node 20-alpine + nginx)
- CREATE: `docker-compose.yml` (backend + frontend + postgres-16 + redis-7 + adminer)
- CREATE: `.dockerignore`
- CREATE: `.gitignore`
- CREATE: `.env.example` (template; no real values)
- CREATE: `.pre-commit-config.yaml` (ruff + black + check-yaml + detect-private-key)
- CREATE: `.github/workflows/ci.yml` (lint + test + acceptance contracts)
- CREATE: `.github/workflows/test.yml` (full test matrix)
- CREATE: `.github/workflows/security.yml` (pip-audit + npm audit + secrets scan)
- CREATE: `Makefile` (per template below)
- CREATE: `pyproject.toml` (Python tooling config)
- CREATE: `requirements.txt` (skeleton; deps will be added by Task 01)

## Files you must NOT touch
- `src/backend/` (Task 01-03 own this)
- `src/frontend/` (Task 04 owns this)
- `tests/` (Tasks 01-04 own these)
- `.specify/`, `plan/`, `docs/`, `orchestrator/` (orchestrator-owned)

## Skills to use
- `docker-compose` (multi-service with healthchecks + depends_on)
- `github-actions` (matrix jobs, caching)
- `pre-commit`
- `code-review`

## The core problem (inline)

### Dockerfile (backend)
```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH PYTHONPATH=/app
COPY src/backend ./src/backend
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8000/healthz || exit 1
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile.frontend
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY src/frontend/package*.json ./
RUN npm ci
COPY src/frontend ./
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY src/frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```
(Create a minimal `src/frontend/nginx.conf` that proxies `/api` to `http://backend:8000` and falls back to `index.html` for SPA routes. If Task 04 hasn't created src/frontend yet, the build will fail in dev — that's expected; this is for prod composition.)

### docker-compose.yml
```yaml
version: "3.9"
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: swa
      POSTGRES_PASSWORD: swa
      POSTGRES_DB: swa_erp
    ports: ["5432:5432"]
    volumes: ["pg_data:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U swa -d swa_erp"]
      interval: 5s
      timeout: 3s
      retries: 10

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10

  adminer:
    image: adminer
    ports: ["8080:8080"]
    depends_on:
      postgres:
        condition: service_healthy

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://swa:swa@postgres:5432/swa_erp
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY:-change-me-in-prod}
      CORS_ORIGINS: '["http://localhost:3000"]'
    ports: ["8000:8000"]
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports: ["3000:80"]
    depends_on:
      - backend

volumes:
  pg_data:
```

### .gitignore (key entries)
```
# Python
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Node
node_modules/
dist/
.vite/

# Env
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Project-specific
logs/*.log
results/local/
.hypothesis/
```

### .env.example
```
APP_NAME=swa-erp
APP_ENV=dev
DEBUG=true
SECRET_KEY=replace-with-openssl-rand-hex-32
DATABASE_URL=postgresql://swa:swa@localhost:5432/swa_erp
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=["http://localhost:3000"]
JWT_ALGORITHM=HS256
JWT_ACCESS_TTL_MIN=60
JWT_REFRESH_TTL_DAYS=30
```

### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.10
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
        files: ^src/backend/
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: detect-private-key
  - repo: local
    hooks:
      - id: block-secrets
        name: Block accidental secret commits
        entry: orchestrator/hooks/block-secrets.sh
        language: script
        pass_filenames: false
```

### .github/workflows/ci.yml
```yaml
name: CI
on: [push, pull_request]
jobs:
  backend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ruff black mypy
      - run: ruff check src/backend/
      - run: black --check src/backend/

  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: swa
          POSTGRES_PASSWORD: swa
          POSTGRES_DB: swa_erp_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U swa"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-asyncio httpx
      - env:
          DATABASE_URL: postgresql://swa:swa@localhost:5432/swa_erp_test
        run: |
          alembic upgrade head
          pytest tests/ -v

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - if: hashFiles('src/frontend/package.json') != ''
        working-directory: src/frontend
        run: |
          npm ci
          npm run lint
          npm run build
          npx tsc --noEmit
```

### .github/workflows/security.yml
```yaml
name: Security
on:
  push: { branches: [main] }
  schedule:
    - cron: "0 6 * * 1"   # weekly Monday 6am UTC
jobs:
  pip-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install pip-audit
      - run: pip-audit -r requirements.txt --strict

  npm-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - if: hashFiles('src/frontend/package.json') != ''
        working-directory: src/frontend
        run: npm audit --audit-level=high
```

### Makefile
```makefile
.PHONY: help install dev test test-wave lint format migrate dispatch ship clean

help:
	@echo "swa-erp commands:"
	@echo "  make install        — install backend + frontend deps"
	@echo "  make dev            — docker-compose up"
	@echo "  make test           — run all tests"
	@echo "  make test-wave wave=N  — run wave-N tests"
	@echo "  make lint           — ruff + eslint"
	@echo "  make format         — black + prettier"
	@echo "  make migrate name=...  — create Alembic migration"
	@echo "  make migrate-up     — apply migrations"
	@echo "  make dispatch wave=N  — open orchestrator and /dispatch"
	@echo "  make ship wave=N      — open orchestrator and /ship"

install:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	@if [ -f src/frontend/package.json ]; then cd src/frontend && npm install; fi

dev:
	docker-compose up --build

test:
	pytest tests/ -v

test-wave:
	pytest tests/wave-$(wave)/ -v

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

test-e2e:
	npx playwright test tests/e2e/

lint:
	ruff check src/backend/
	@if [ -d src/frontend ]; then cd src/frontend && npm run lint; fi

format:
	black src/backend/
	ruff check --fix src/backend/
	@if [ -d src/frontend ]; then cd src/frontend && npx prettier --write src/; fi

migrate:
	cd src/backend && alembic revision --autogenerate -m "$(name)"

migrate-up:
	cd src/backend && alembic upgrade head

dispatch:
	@echo "Open Claude Code or Kimi and run: /dispatch wave-$(wave)"

ship:
	@echo "Open Claude Code or Kimi and run: /ship wave-$(wave)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
```

### pyproject.toml
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "swa-erp"
version = "0.1.0"
description = "Internal ERP for SWA Consultancy"
requires-python = ">=3.11"

[tool.ruff]
line-length = 100
target-version = "py311"
extend-exclude = ["alembic/versions"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "RUF"]
ignore = ["E501"]  # handled by formatter

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.mypy]
python_version = "3.11"
strict = true
exclude = ["alembic/versions"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --tb=short"
asyncio_mode = "auto"
```

### requirements.txt (skeleton — Task 01 will add the real list)
```
# Minimal — full list added by Task 01
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.34
alembic==1.13.2
psycopg2-binary==2.9.9
pydantic==2.8.2
pydantic-settings==2.4.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
celery==5.4.0
redis==5.0.8
structlog==24.4.0
pytest==8.3.2
pytest-asyncio==0.24.0
httpx==0.27.0
ruff==0.6.3
black==24.8.0
mypy==1.11.2
```

## Acceptance criteria (executable)
- [ ] `docker-compose up postgres redis adminer` brings up the data services (don't require backend image to build successfully yet — depends on Task 01)
- [ ] `docker-compose config` validates without errors
- [ ] `pre-commit install` succeeds; running `pre-commit run --all-files` works (may warn if files don't exist yet)
- [ ] `.github/workflows/ci.yml` is valid YAML (use `yamllint` or `actionlint` if available)
- [ ] `make help` prints all targets
- [ ] `make lint` exits 0 (with stub files — may warn)
- [ ] `.env.example` is present; `.env` is in `.gitignore`

## How to deliver
1. Create all files
2. Run acceptance commands
3. Write report to `work/reports/wave-1/05-ci-docker.report.md`
4. Stop

## Constraints
- Time budget: 60 min
- Use only well-known versions (postgres:16-alpine, redis:7-alpine, node:20-alpine, python:3.11-slim)
- Don't add to requirements.txt beyond the skeleton — Task 01 owns the full list
- nginx.conf for frontend should be minimal: serve static + proxy `/api` + SPA fallback
- No Kubernetes manifests yet (later wave if needed)
