# Conventions

## Code
- **Python:** ruff + black + mypy strict (see `pyproject.toml`); 3.11+; PEP 604 unions ok
- **TypeScript:** strict mode; no `any`; explicit return types on exports; eslint + prettier
- **DB:** SQLAlchemy 2 declarative; Alembic migrations for every schema change
- **Tests:** pytest for backend, Playwright for E2E, Vitest for frontend units

## Backend module conventions
- **Service convention** (`src/backend/services/<entity>_service.py`): one function per
  operation; each takes `db: Session` + `actor_id: uuid.UUID`; returns an ORM model or raises
  a typed exception. Services hold the business logic — API routers must not.
- **Repository convention** (`src/backend/db/repositories/<entity>_repo.py`): expose
  `list_*`, `get_by_id`, `create`, `update`, `soft_delete`. Soft-delete is via a `deleted_at`
  column — never a hard delete of business data.
- **Reference-ID service** (`src/backend/services/reference_id_service.py`):
  `generate_reference_id(db: Session, entity_type: str) -> str` returns
  `SWA-{year}-{TYPE}-{seq:03d}`, atomically and race-safe via `INSERT … ON CONFLICT` on
  `reference_counters`. Entity codes in use: `SA`, `INQ`, `CLT`, `TKN`, plus per-document-type
  counter keys from `document_reference_service.py`. The code is authoritative over any doc
  (see ADR-0002's corrected signature).
- **Alembic**: revisions are 4-digit zero-padded (`0001`…`0025`), one migration per concern;
  always create with `alembic revision --rev-id=NNNN_descriptive_name`.

## Data (runtime storage — as actually implemented)

**Corrected 2026-07-21, updated 2026-08-10 (wave-31)** — this section previously described a
`data/` directory structure and MinIO integration that were never built; a full-project audit
confirmed no `data/` directory exists at all. What's actually real:
- **All uploads (BOQs, documents, everything)**: written through the `StorageBackend`
  abstraction (`src/backend/core/storage.py`, `get_storage()`). Default backend is `local` —
  flat `uploads/<id>/` directory at repo root, see `src/backend/services/boq_service.py`
  (`UPLOAD_DIR = Path("uploads/boqs")`) and `src/backend/services/document_service.py`
  (`f"uploads/{project_id}"`). Opt-in `minio` backend (`STORAGE_BACKEND=minio`) writes to the
  compose `minio` service. `uploads/` is gitignored (see root `.gitignore`).
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
- GST: **implemented at invoice level as of wave-18** (`2073c36`, migration `0025_add_invoice_gst`).
  `Invoice` carries `gst_percent` + `gst_amount` (`Numeric(18,2)`), computed in
  `src/backend/services/invoice_service.py` (`gst_amount = subtotal × gst_percent / 100`) and
  returned in `InvoiceRead`. The older generic `tax_rate`/`tax_amount` columns remain and mirror
  the GST values. Scope of what is NOT GST-specific yet: no HSN/SAC code per line, and no GSTIN
  captured on the invoice itself (Client/Vendor models do store their own `gst_number`).
  **Corrected 2026-08-07** — this line previously claimed GST was not implemented; wave-18 shipped it.

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
- Errors: body is `{"detail": "..."}` (standard FastAPI `HTTPException`); every response carries a
  `X-Request-ID` header (added by `src/backend/core/middleware.py` `RequestIdMiddleware`). There is
  **no `code` field in the body and no `request_id` field in the body** — do not rely on them.
  **Corrected 2026-08-07** — this line previously claimed `{detail, code, request_id}`; no custom
  exception handler exists and `request_id` is header-only.
- Pagination: `?page=1&page_size=20` query params; response includes `{items, total, page, page_size}`

## Git
- Branches: `wave-N/<short-name>` or `bugfix/<issue-id>`
- Commits: Conventional Commits (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`)
- Commit scope: wave or module (`feat(wave-2): add project list`)
- PR title: imperative present (`Add project list page`)
- No force push to `main`
