.PHONY: help install dev test test-wave test-unit test-integration test-e2e lint format migrate migrate-up dispatch ship clean

help:
	@echo "swa-erp commands:"
	@echo "  make install           — install backend + frontend deps"
	@echo "  make dev               — docker-compose up (full stack)"
	@echo "  make dev-services      — only postgres + redis (run backend/frontend separately)"
	@echo "  make test              — run all tests"
	@echo "  make test-wave wave=N  — run wave-N tests"
	@echo "  make test-unit         — unit tests only"
	@echo "  make test-integration  — integration tests only"
	@echo "  make test-e2e          — Playwright E2E"
	@echo "  make lint              — ruff + eslint"
	@echo "  make format            — black + prettier"
	@echo "  make migrate name=...  — create Alembic migration"
	@echo "  make migrate-up        — apply migrations"
	@echo "  make dispatch wave=N   — reminder to open orchestrator"
	@echo "  make ship wave=N       — reminder to open orchestrator"
	@echo "  make clean             — remove caches"

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt
	@if [ -f src/frontend/package.json ]; then cd src/frontend && npm install; fi

dev:
	docker-compose up --build

dev-services:
	docker-compose up postgres redis adminer -d

test:
	pytest tests/ -v

test-wave:
	pytest tests/wave-$(wave)/ -v

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

test-e2e:
	@if [ -f playwright.config.ts ]; then npx playwright test tests/e2e/; else echo "Playwright not yet configured (Task 04)"; fi

lint:
	ruff check src/backend/ 2>/dev/null || true
	@if [ -d src/frontend ]; then cd src/frontend && npm run lint 2>/dev/null || true; fi

format:
	black src/backend/ 2>/dev/null || true
	ruff check --fix src/backend/ 2>/dev/null || true
	@if [ -d src/frontend ]; then cd src/frontend && npx prettier --write src/ 2>/dev/null || true; fi

migrate:
	cd src/backend && alembic revision --autogenerate -m "$(name)"

migrate-up:
	cd src/backend && alembic upgrade head

dispatch:
	@echo "Open Claude Code or Kimi in the project root and run:"
	@echo "  /dispatch wave-$(wave)"

ship:
	@echo "Open Claude Code or Kimi in the project root and run:"
	@echo "  /ship wave-$(wave)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
