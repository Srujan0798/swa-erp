.PHONY: help install dev dev-services test test-wave test-unit test-integration test-e2e lint format migrate migrate-up dispatch ship clean backup-db backup-files restore-db seed-demo seed-dev smoke

help:
	@echo "swa-erp commands:"
	@echo "  make install           — install backend + frontend deps"
	@echo "  make dev               — docker-compose up (full stack; UI :3100 API :8100)"
	@echo "  make dev-services      — only postgres + redis (run backend/frontend separately)"
	@echo "  make bootstrap-real    — FULL real Excel load + link chain (USE THIS)"
	@echo "  make import-real       — DRY-RUN real Excel from resources/"
	@echo "  make import-real-commit — WIPE + COMMIT real Excel only"
	@echo "  make seed-demo         — synthetic demo only (prefer import-real)"
	@echo "  make seed-dev          — minimal dev users only"
	@echo "  make smoke             — live API smoke; backend must be up on :8100"
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
	@echo "  make backup-db         — pg_dump → ./backups/db/ (30-day retention)"
	@echo "  make backup-files      — tar ./uploads/ → ./backups/files/ (90-day retention)"
	@echo "  make restore-db file=<path> — DESTRUCTIVE restore, prompts for confirmation"
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
	python3 -m ruff check src/backend/
	@if [ -d src/frontend ]; then cd src/frontend && npm run lint; fi

# Real quality gates, identical to CI (ci.yml backend-lint + backend-test).
# Wave-32: every step fails the build — no `|| true` anywhere.
verify:
	python3 -m ruff check src/backend/
	python3 -m black --check src/backend/
	python3 -m mypy src/backend/ --explicit-package-bases
	python3 -m pytest tests/ -q --cov=src/backend --cov-report=term-missing --cov-report=xml --cov-fail-under=82
	@if [ -d src/frontend ]; then cd src/frontend && npm run lint; fi

format:
	black src/backend/
	ruff check --fix src/backend/
	@if [ -d src/frontend ]; then cd src/frontend && npx prettier --write src/; fi

migrate:
	cd src/backend && alembic revision --autogenerate -m "$(name)"

migrate-up:
	alembic -c src/backend/alembic.ini upgrade heads

dispatch:
	@echo "Open Claude Code or Kimi in the project root and run:"
	@echo "  /dispatch wave-$(wave)"

import-data:
	@if [ -z "$(file)" ] || [ -z "$(type)" ]; then \
		echo "Usage: make import-data file=<path.xlsx> type=<clients|inquiries|agreements|tokens|document_references|projects|time_logs|sustainability> [commit=1]"; \
		exit 1; \
	fi
	@if [ "$(commit)" = "1" ]; then \
		python3 scripts/import_excel.py $(type) $(file) --commit; \
	else \
		python3 scripts/import_excel.py $(type) $(file) --dry-run; \
	fi

seed-demo:
	@echo "DEV ONLY synthetic seed. Live data: make bootstrap-real"
	@test "$$CONFIRM_SYNTHETIC_SEED" = "1" || (echo "Set CONFIRM_SYNTHETIC_SEED=1 to force synthetic seed"; exit 1)
	APP_ENV=dev python3 scripts/seed_demo.py

seed-dev:
	APP_ENV=dev python3 scripts/seed_dev.py

# Real SWA Excel sheets from resources/ (dry-run by default)
import-real:
	APP_ENV=dev python3 scripts/import_real_sheets.py

import-real-commit:
	APP_ENV=dev python3 scripts/import_real_sheets.py --commit --wipe

# Full internship bootstrap: wipe + real Excel + link chain + all role users
bootstrap-real:
	APP_ENV=dev python3 scripts/bootstrap_real.py

smoke:
	python3 scripts/smoke_chain.py

ship:
	@echo "Open Claude Code or Kimi in the project root and run:"
	@echo "  /ship wave-$(wave)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true

backup-db:
	./scripts/backup_db.sh

backup-files:
	./scripts/backup_files.sh

restore-db:
	@if [ -z "$(file)" ]; then \
		echo "Usage: make restore-db file=<path-to-backup.sql.gz>"; \
		exit 1; \
	fi
	./scripts/restore_db.sh "$(file)"
