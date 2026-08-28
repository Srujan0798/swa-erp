# Blast radius containment tiers

This file maps r0–r5 containment tiers to concrete SWA-ERP actions.
Agents MUST stay inside the tier granted by the orchestrator for the current task.

## r0 — read-only analysis

Automatic, low risk. No mutations.

Examples in this repo:
- `git status`, `git log`, `git diff`
- Reading `src/backend/**`, `src/frontend/**`, `docs/**`
- Searching with `rg` / grep against non-test code
- Running `pytest` in `--collect-only` mode

## r1 — docs/reports only

Automatic. Produces human-readable artifacts; no code paths change.

Examples:
- Writing or updating `work/reports/wave-*/**`
- Updating `docs/**`, `README.md`, `PLAN.md`
- Updating `orchestrator/core/*.md`

## r2 — tests only

Automatic or lightly supervised. Adds/modifies tests without changing app code.

Examples:
- Adding files under `tests/` (e.g. wave-33 coverage tests)
- Updating `tests/conftest.py` only to add fixtures
- Running `pytest` against the current code surface

## r3 — application code behind a green suite

Requires green test baseline before and after. Code changes allowed behind passing suite.

Examples:
- Adding a backend service helper in `src/backend/services/`
- Adding a frontend page/component in `src/frontend/src/pages/`
- Updating an existing feature with tests that still pass

Gate: `pytest` must be green for affected packages before merge.

## r4 — migrations / auth / money paths

Human-confirmed. Touches invariants the project explicitly protects.

Concrete anchors for THIS repo:
- Decimal money convention: `Decimal(18,2)`, INR default, multi-currency ready
- RBAC role checks (`HTTPBearer`, role assertions)
- Alembic heads / schema migrations
- Storage backend paths (`local` uploads vs `minio`)

Examples:
- Any `alembic/versions/*.py` change
- Changing `src/backend/core/storage.py` behaviour
- Changing JWT/RBAC auth flows or role seeds
- Any repo/service path that writes `amount`, `currency`, or tax fields

## r5 — real data / production deploy

Always human-confirmed. No automatic execution.

Examples:
- `docker compose` against production targets
- Seeding, migrating, or deleting live database records
- Deploy workflows touching prod infra
- Handling vendor/inventory/financial transaction corrections in live systems
