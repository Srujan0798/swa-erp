# Handoff Protocol

> **Role:** Session / orchestrator-switching protocol. Part of the front-door set — start at
> [README.md](README.md).

## Current state (2026-09-22 — files sent to company group; awaiting 8 IT answers)

**Engine version:** v1.0.1. Professional-grade track (waves 32–39) **all shipped**. Post-seal
hardening (waves 40–51) landed truth-infrastructure guardrails, audit logging, CSP/token rotation,
service-layer logging, pagination, deterministic tests, atomicity fix, IDOR fix, and final re-seal.

### Verified (this session, real command output — not carried forward from memory)
- Backend static gates: **ruff clean, black clean, mypy clean** (2026-09-22) · tsc/eslint/vite-build clean
- Backend suite: **654 passed** (2026-09-22); prior wave-47 Docker seal: 572 passed / 1 skipped / 0 failed · 85% coverage
- Frontend: **600 passed / 0 failed** (2026-09-22) · coverage at 2026-09-19 reseal: **60.46% functions** (63.2% statements, 55.09% branches, 64.29% lines) · tsc/eslint/vite-build clean
- Migrations: single Alembic head `0042`
- Prod deploy: `docker-compose.prod.yml` + `.env.production` validated (secrets pre-filled, gitignored); files sent to company group 2026-09-22 — awaiting 8 IT answers (Docker/WSL2/ports/HTTPS/backups/URL/DB-location/deploy)
- Seal report: [`work/reports/FINAL-CLOSE.report.md`](work/reports/FINAL-CLOSE.report.md)
- Wave-51 re-seal: commit `4396581` (pushed to `origin/main`)

### Recovery-month context (still relevant, not superseded)
Earlier feedback from SWA was that the product felt "unusable / dummy." A focused recovery
addressed real Excel-chain UX (not more test waves): Document References as a first-class page,
Excel-first sidebar, full-chain dashboard, `make swa-live-local`, real field-name parity for
Time Logging / Tokens / Service Agreements / Document References. See
[`deliverables/MEETING_AND_GO_LIVE_GUIDE.md`](deliverables/MEETING_AND_GO_LIVE_GUIDE.md) and
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
3. [`deliverables/MEETING_AND_GO_LIVE_GUIDE.md`](deliverables/MEETING_AND_GO_LIVE_GUIDE.md) for the one ops path
4. To re-verify from scratch: `python3 -m pytest tests/ -q --tb=no` with Postgres (+ Redis for
   full green) running; `cd src/frontend && npx vitest run` for the frontend suite.

## Open decisions (external)
- Server/deploy 8 facts — Viraj
- Excel freeze date + migration owner — Viraj

## Dispatch status: ALL COMPLETE
The full dispatch plan (waves 40–51) has been executed and committed to `origin/main`.
- Wave-40: Truth infrastructure (metrics script, EXECUTION.md)
- Wave-48: Production hardening (logging, CSP, pagination, audit, idempotency, frontend loading/bundling)
- Wave-49: Transaction atomicity for Inquiry→Client→Project
- Wave-50: Security risks (job IDOR, /metrics auth flag) + deterministic test suite
- Wave-51: Final re-seal + submission refresh (commit `4396581`)
