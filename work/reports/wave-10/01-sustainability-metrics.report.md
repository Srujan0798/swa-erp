# Report — Wave 10 · 01 Sustainability Metrics API + Frontend

## Result
DONE

## What I did
- Created `src/backend/models/sustainability_metric.py` — `SustainabilityMetric` model with all fields from the real sheet (reference_id, recorded_date, compliant_with_green_standards as nullable bool, energy_saved_kwh, co2_avoided_tco2e, lifecycle_cost_savings_inr, insulation_efficiency_ratio, payback_period_months, notes). All metric fields nullable; project_id + recorded_date only meaningful anchors. Used `Numeric(5,2)` for the ratio and `Numeric(6,2)` for months (corrected from the earlier bad draft that used years).
- Created `src/backend/schemas/sustainability_metric.py` — Create/Update/Read schemas (Decimal fields per spec).
- Created `src/backend/db/repositories/sustainability_metric_repo.py` — CRUD + project-scoped list.
- Created `src/backend/services/sustainability_metric_service.py` — service layer returning dicts (matches repo/service convention used by compliance).
- Created `src/backend/api/sustainability_metrics.py` — project-scoped router `/api/projects/{project_id}/sustainability/metrics` (list/get/create/update/delete). Reads require any authenticated user; writes require PM+ (mirrors the invoices pattern).
- Created `src/backend/alembic/versions/0018_add_sustainability_metrics.py` — migration creating the table + project FK index. (Tests use `Base.metadata.create_all`, not the migration, so the table is still exercised.)
- Modified `src/backend/models/__init__.py`, `src/backend/api/__init__.py`, `src/backend/main.py` — registered the model + router.
- Created `tests/wave-10/test_sustainability_metrics.py` — 5 tests (create, project-scoped list, update, delete, PM-role enforcement). All pass.
- Created `src/frontend/src/components/sustainability/SustainabilityForm.tsx` and `SustainabilityList.tsx`.
- Created `src/frontend/src/hooks/useSustainability.ts`.
- Created `src/frontend/src/pages/SustainabilityPage.tsx` (standalone `/sustainability` page with project selector, plus a reusable `SustainabilityManager` used as a **Project-detail tab**).
- Modified `src/frontend/src/App.tsx` (route `/sustainability`), `Sidebar.tsx` (nav item), `ProjectDetailPage.tsx` (Sustainability tab), `lib/api.ts` + `types/api.ts` (API client + types).

## This-session verification (re-run)
- `python3 -m pytest tests/wave-10/ -q` → **5 passed**
- `python3 -m pytest tests/wave-7/ tests/wave-8/ tests/wave-9/ -q` → **146 passed** (regression suite)
- `python3 -m ruff check` on all touched/created files → **clean**
- `npm run typecheck` → **clean**

## Lint fixes applied this session
- `tests/wave-10/test_sustainability_metrics.py` — removed unused `import pytest`.
- `src/backend/api/__init__.py` — fixed `RUF022` (sorted `__all__`; the `sustainability_metrics_router` entry was appended out of order in the prior session).

## Acceptance checks
- [x] `python3 -m pytest tests/wave-10/ -q` passes — **5 passed**.
- [x] `ruff check src/backend/models/sustainability_metric.py` — **clean**.
- [x] `npm run typecheck` — **clean** (0 errors across the whole frontend).
- [x] `python3 -m pytest tests/wave-7/ tests/wave-8/ tests/wave-9/ -q` — **146 passed**, no regressions introduced.
- [ ] Create a metric via UI against a running backend — **not manually clicked in a browser** (no browser in this environment). Covered by: the API endpoint is exercised by the passing pytest suite (`authed_pm_client` POST returns 201), and the form/list/tab components are built, typecheck-clean, and wired into routing + nav. Recommended manual smoke test: `make dev`, log in as PM/admin, open a project → Sustainability tab → Add Metric.

## Decisions I made
- Corrected the earlier bad draft: field is a Yes/No `compliant_with_green_standards` bool (not `green_standard: str`), and payback is in **months** (not years).
- Used `Decimal` for all money/ratio fields in model + schema exactly as the sheet dictates.
- Mounted the feature both as a standalone `/sustainability` page (per the file/route list) **and** as a Project-detail tab (per the prose instruction), sharing a `SustainabilityManager` component — matching the existing BOQ/Quotes tab pattern in `ProjectDetailPage.tsx`.
- Writes require PM+ (consistent with the invoices API); reads are open to any authenticated user.

## Tests run
- `python3 -m pytest tests/wave-10/ -q` → 5 passed
- `python3 -m pytest tests/wave-7/ tests/wave-8/ tests/wave-9/ -q` → 146 passed (regression)
- `ruff check` on all wave-10 files → clean
- `npx tsc --noEmit` (frontend) → 0 errors
- `npm run lint` (frontend) → clean
- `npx vite build` → built successfully (previous session)

## Issues / blockers
- None. (Note: `pytest-asyncio` was not installed in the venv; installed it to run the async test suite. That is an environment dependency, not a code issue.)

## Recommended next task
None required; Wave 10 is independently complete. Wave 11 in this same session finishes the shared `typecheck`/`lint` gate.

## Time / tokens / model
~60 min / hy3-free
