# Conventions

## Code
- **Python:** ruff + black + mypy strict (see `pyproject.toml`); 3.11+; PEP 604 unions ok
- **TypeScript:** strict mode; no `any`; explicit return types on exports; eslint + prettier
- **DB:** SQLAlchemy 2 declarative; Alembic migrations for every schema change
- **Tests:** pytest for backend, Playwright for E2E, Vitest for frontend units

## Data
- **Raw uploads:** `data/raw/` (immutable; never modified)
- **Samples:** `data/samples/` (small fixtures for dev/demo)
- **Synthetic:** `data/synthetic/` (generated for testing)
- **Seed data:** `data/seed/` (initial dev data; not for prod)
- **BOQ uploads (runtime):** stored under MinIO bucket `boq-uploads/` (prod) or `data/runtime/boq/` (dev)

## Documents (runtime)
- **Drawings:** `documents/<project_id>/drawings/v<N>/`
- **Specs:** `documents/<project_id>/specs/`
- **Signed:** `documents/<project_id>/signed/`

## Models (if ML — not in current scope)
- N/A for SWA ERP (no ML modules)

## Naming
- **Folders:** kebab-case (`wave-1/`, `client-portal/`)
- **Python files:** snake_case (`project_service.py`)
- **TS components:** PascalCase (`ProjectCard.tsx`)
- **TS non-components:** camelCase (`useProjects.ts`, `apiClient.ts`)
- **Markdown:** kebab-case for docs (`scope-guard.md`), SCREAMING_CASE for top-level (`README`, `CLAUDE`, `HANDOFF`)
- **Test files:** `test_*.py` (Python), `*.spec.ts` (Playwright/Vitest)
- **Migrations:** `0NNN_descriptive_name.py` (4-digit zero-padded, sequential)

## Money
- ALL money fields: `Decimal(18, 2)` in DB; `Decimal` in Python; string in JSON ("99999999.99")
- Currency: INR default; multi-currency-ready via `currency` column where applicable
- GST: stored separately (`amount`, `gst_amount`, `total_amount`); HSN/SAC code per line

## Dates and times
- DB: `TIMESTAMPTZ`, always UTC
- Python: `datetime` with `tzinfo=timezone.utc`; never naive
- Display layer (frontend): Asia/Kolkata via `date-fns-tz`
- API JSON: ISO 8601 with `Z` suffix (`"2026-05-20T10:30:00Z"`)

## Identifiers
- Primary keys: UUID v4 (server-generated)
- External-facing slugs: kebab-case (e.g., `project_slug = "swa-mumbai-hotel-2026-01"`)
- Reference numbers: sequential per type (e.g., `quote_no = "Q-2026-00123"`)

## API
- Routes: kebab-case in URLs (`/api/audit-log`, not `/api/auditLog`)
- JSON keys: camelCase in TS frontend; snake_case in Python backend (Pydantic models bridge with `alias_generator`)
- Errors: `{detail, code, request_id}` always
- Pagination: `?page=1&page_size=20` query params; response includes `{items, total, page, page_size}`

## Git
- Branches: `wave-N/<short-name>` or `bugfix/<issue-id>`
- Commits: Conventional Commits (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`)
- Commit scope: wave or module (`feat(wave-2): add project list`)
- PR title: imperative present (`Add project list page`)
- No force push to `main`
