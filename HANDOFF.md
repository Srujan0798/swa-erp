# Handoff Protocol

> **Role:** Session / orchestrator-switching protocol. Part of the front-door set — start at
> [README.md](README.md).

## Current state (2026-08-28 — engineering close sealed)

**Engine version:** v1.0.1. Professional-grade track (waves 32–39) **all shipped**. Post-seal
hardening (waves 40–47) landed the truth-infrastructure guardrails, operational docs,
architecture/schema docs, and the final gate-and-tracker seal.

### Verified (this session, real command output — not carried forward from memory)
- Backend: **572 passed / 1 skipped / 0 failed** · 85% coverage · ruff/black/mypy clean
- Frontend: **523 passed / 0 failed** · tsc/eslint/vite-build clean
- Migrations: single Alembic head `0033`
- The last 5 standing failures (401-vs-403 auth assertions) are fixed for real — `deps.py`
  now explicitly returns 403 when no `Authorization` header is present
  (`HTTPBearer(auto_error=False)` + a guard in `get_current_user`), matching what
  FastAPI's default already implied and what wave-46 had separately fixed on the test side.
- Seal report: [`work/reports/FINAL-CLOSE.report.md`](work/reports/FINAL-CLOSE.report.md)
- Wave-47 full report: [`work/reports/wave-47/01-final-seal.report.md`](work/reports/wave-47/01-final-seal.report.md)

### Recovery-month context (still relevant, not superseded)
Earlier feedback from SWA was that the product felt "unusable / dummy." A focused recovery
addressed real Excel-chain UX (not more test waves): Document References as a first-class page,
Excel-first sidebar, full-chain dashboard, `make swa-live-local`, real field-name parity for
Time Logging / Tokens / Service Agreements / Document References. See
[`deliverables/VIRAJ_TRIAL_SCRIPT.md`](deliverables/VIRAJ_TRIAL_SCRIPT.md) and
`work/reports/recovery/LOOP.md` for that history.

### Truth hierarchy
MEETINGS + ADRs → code/tests → README → this file. If two docs disagree, the one closer to
code/tests wins; fix the drift rather than trusting the more convenient one.

## Secrets / environment
- **Docker available:** `docker compose up -d postgres redis minio` brings up the full stack.
  Test DB `swa_erp_test` (create manually if needed:
  `psql -h localhost -U swa -d postgres -c "CREATE DATABASE swa_erp_test OWNER swa;"`).
- **Local Postgres only** (no Docker): tests still target
  `postgresql://swa:***@localhost:5432/swa_erp_test`; expect the 2 Redis-dependent `/readyz`
  checks to fail/skip in that mode — that's environmental, not a defect.
- `SECRET_KEY="test-secret-key"` for tests; production value is external (Viraj / no IT dept).
  See [`docs/INSTALL_NO_IT.md`](docs/INSTALL_NO_IT.md).

## What is external (do NOT block engineering work on these)
1. **Server access / deploy** — Viraj holds the 8 server facts; no IT department client-side.
   [`docs/IT_BRIEF.md`](docs/IT_BRIEF.md) has the full brief. Do not re-blast SEND_IT / SEND_VIRAJ.
2. **Excel data migration** — owner pending Viraj's freeze date. Importer (`make migrate-data`)
   is ready, dry-run by default.
3. **Client-box load test** — the Locust runs in [`docs/PERFORMANCE.md`](docs/PERFORMANCE.md)
   were on a dev machine, not the client's server.

## Where to start a new session
1. This file → deploy/import help only unless a bug is reported
2. `README.md` for the evaluator view
3. `MASTER-FLOW.md` for the one ops path
4. To re-verify from scratch: `python3 -m pytest tests/ -q --tb=no` with Postgres (+ Redis for
   full green) running; `cd src/frontend && npx vitest run` for the frontend suite.

## Open decisions (external)
- Server/deploy 8 facts — Viraj
- Excel freeze date + migration owner — Viraj

## Queued, not yet dispatched
A live product audit (waves 48–49) found real gaps beyond the close-out scope — see
`work/wave-48/` (rate limiting, audit-log coverage, error boundary, accessibility, pagination,
idempotency, CSP/token rotation, service-layer logging) and `work/wave-49/01-transaction-atomicity.md`
(**critical** — the core Inquiry→Client→Project flow can leave orphaned rows on a partial
failure; not yet fixed). Also `work/wave-40/02-metrics-script-fix.md` for two real bugs found
mid-audit. None of these are dispatched — they're ready whenever assigned.
