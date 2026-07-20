# Conventions

## Code
- **Python:** ruff + black + mypy strict (see `pyproject.toml`); 3.11+; PEP 604 unions ok
- **TypeScript:** strict mode; no `any`; explicit return types on exports; eslint + prettier
- **DB:** SQLAlchemy 2 declarative; Alembic migrations for every schema change
- **Tests:** pytest for backend, Playwright for E2E, Vitest for frontend units

## Data (runtime storage — as actually implemented)

**Corrected 2026-07-21** — this section previously described a `data/` directory structure and
MinIO integration that were never built; a full-project audit confirmed no `data/` directory
exists at all and there is zero MinIO code anywhere in `src/backend` (grep confirms). What's
actually real:
- **All uploads (BOQs, documents, everything)**: flat `uploads/<id>/` directory at repo root —
  see `src/backend/services/boq_service.py` (`UPLOAD_DIR = Path("uploads/boqs")`) and
  `src/backend/services/document_service.py` (`f"uploads/{project_id}"`). This is local
  filesystem only in the current implementation; MinIO/S3 was a planned future migration, never
  built. `uploads/` is gitignored (see root `.gitignore`).
- No `data/raw/`, `data/samples/`, `data/synthetic/`, `data/seed/`, or `documents/<project_id>/`
  structure exists — remove any references to these paths if found elsewhere, they describe an
  unbuilt plan, not the real system.

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
- GST: **not yet implemented as of 2026-07-21** — `Invoice`/`InvoiceItem` currently only have a
  generic `tax_rate`/`tax_amount` pair (defaults to 18%, numerically GST-shaped but not
  GST-specific), no `gst_amount` field, no HSN/SAC code per line, no GSTIN captured on the
  invoice itself. Client and Vendor models do store a `gst_number` (their own registration
  number) but Invoice never references it. This line previously described the target design as
  already built — it wasn't; see `work/wave-18/01-security-hardening.md` item 4 for the actual
  fix in progress.

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
