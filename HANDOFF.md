# Handoff Protocol

## Why this file exists
Switching orchestrators (Claude ↔ Kimi) or starting a fresh session shouldn't require re-explaining the project. This file lets the new session catch up in < 5 minutes.

## Current state (2026-08-07 — FINAL RELEASE CUT: v1.0.0)

- **Status:** Waves 1-30 ✅ SHIPPED and independently verified. **`v1.0.0`** is the first real
  release (tagged locally `v1.0.0`, unpushed — orchestrator pushes it). Version files
  (`pyproject.toml`, `src/frontend/package.json`, `package-lock.json`) all say **1.0.0**.
- **Release verification (wave-30, all run live against the stack):** backend suite
  **393 passed / 0 failed**; `ruff check src/backend/` clean; `tsc --noEmit` 0 errors;
  eslint clean (`--max-warnings 0`); `vite build` succeeds; Docker cold boot (`down -v` +
  `up --build`) brings all 5 services up healthy; `/healthz` → 200; Playwright **7/7**; the
  full client business chain was walked live via the API (Inquiry → convert new + existing
  client → Service Agreement → Token → DBR/KDR shared counter → time log → sustainability
  metric → invoice with GST → report export), all with real reference IDs. Full evidence in
  `work/reports/wave-30/01-final-release-and-submission.report.md` and
  `deliverables/SUBMISSION.md`.
- **Backend test suite: 393/393 passing** (`python3 -m pytest tests/ -q`, verified 2026-08-07).
- **Client submission package:** `deliverables/SUBMISSION.md` — what was built, verification
  evidence, explicit drop list, known limitations, the 2 open external blockers, deploy
  pointer, Excel import pointer, docs map, and support/next steps.
- **The 2 open external blockers remain** (nothing code can resolve): Viraj's 3 decisions
  (`docs/decisions/0002-core-id-chain-gap.md`) and IT's 8 answers (`docs/IT_BRIEF.md`).
- **Known limitations (documented honestly in SUBMISSION.md):** Celery is an installed
  dependency only — jobs run synchronously; storage is local disk (`uploads/`), MinIO/S3 not
  wired; JWT is HS256 (not RS256); the Alembic graph has multiple heads resolved via
  `upgrade heads` (no merge migrations).
- **Where to start:** `deliverables/SUBMISSION.md` → `docs/DEPLOYMENT_CHECKLIST.md` →
  `docs/IT_BRIEF.md` (fill PENDING IT ANSWER placeholders before prod deploy).

## Where to start a new session
1. Read this file
2. Read `CLAUDE.md` (kernel)
3. Read `plan/EXECUTION.md` (wave status)
4. Read most recent ADR in `docs/decisions/`
5. Run `/status` to see live state

## When you've just merged a wave
Update this file:
- Bump "Active wave" to wave-N+1
- Summarize what shipped
- Note open issues / carry-overs to next wave

## When switching Claude ↔ Kimi
- No file changes needed
- Both read root CLAUDE.md (Kimi treats KIMI.md as alias — identical content)
- Same workflow, same commands
- Auto-memory in `orchestrator/memory/MEMORY.md` is shared

## When onboarding a worker (rare — workers should be stateless)
Workers DON'T read this file. Their task brief in `work/<wave>/` is self-contained.
Workers receive:
1. `work/WORKER_PROMPT.md` (universal prefix)
2. One task file from `work/wave-N/`
That's it. No project memory needed.

## Open decisions (live)
- _None yet — see ADRs in docs/decisions/ as they accumulate_

## Wave roadmap recap
1. Foundation (auth, users, roles, base data model, shell) — ✅ SHIPPED `df1b779`
2. Clients + Projects core (CRM-lite, project CRUD) — ✅ SHIPPED `d1e3017`
3. Quotation/BOQ workflow (upload BOQ, quote versions, approvals) — ✅ SHIPPED `f49eac1`
4. Task management (per-project tasks, assignments, deps) — ✅ SHIPPED (`ed71fac` bulk commit)
5. Vendor + Inventory (vendor DB, materials catalog, RFQ-to-vendor) — ✅ SHIPPED (`ed71fac`)
6. Documents + compliance tracking (NBC/ECBC/IGBC/IS checklist) — ✅ SHIPPED (`ed71fac`)
7. Time tracking + financials (timesheets, invoicing, project P&L) — ✅ SHIPPED (`ed71fac`)
8. Reports + dashboards + deliverables (paper/report/slides/demo) — ✅ SHIPPED `58864df`
9. Core ID chain — Inquiry, Service Agreement, Token, Document Reference — ✅ SHIPPED, closed
   the real client-requested MVP gap (`c3367fa`)
10. Sustainability metrics — ✅ SHIPPED (`a155000`)
11. Reconcile dangling uncommitted frontend work — ✅ SHIPPED (`4e0655d`)
12. Independent verification (real test run, Docker, E2E) — ✅ SHIPPED (`9852ec0`)
13. Excel → ERP data migration importer — ✅ SHIPPED (`466d8ae`)
14. Docker Compose auto-migration + seed fix — ✅ SHIPPED (`ab0a786`)
15. E2E test fixes — ✅ SHIPPED (`4be7536`)
16. Model/migration drift sweep — ✅ SHIPPED (`d5b2790`)
17-21. Notifications mount, security hardening, backup scripts, prod config templates,
   handover docs — ✅ SHIPPED (see `work/reports/wave-N/` and the status table in
   `plan/EXECUTION.md`)
22-30. Audit fixes (RBAC, correctness, dead-code/UI), security/lint, doc consolidation, and the
   **v1.0.0 release** — ✅ SHIPPED; see `plan/EXECUTION.md` status table and
   `deliverables/SUBMISSION.md`

## Key project context
- **Tech stack:** Python 3.11, FastAPI, SQLAlchemy 2, Pydantic v2, PostgreSQL, Redis, React 18, Vite, TS, Tailwind, shadcn/ui, TanStack Query. Celery is implemented (`src/backend/workers/`, compose `worker` service, Redis broker/backend) and powers async export endpoints (`?async=true` → `GET /api/jobs/{id}`). Storage goes through `StorageBackend` (`src/backend/core/storage.py`) — `local` `uploads/` default, opt-in `minio` backend. See `HIERARCHY.md`.
- **Auth:** JWT + RBAC (roles: admin, pm, designer, auditor, viewer)
- **Money:** Decimal(18,2), INR default, multi-currency ready
- **Compliance standards:** NBC, ECBC, IGBC, IS fire codes (explicit references required)
- **Project lifecycle:** Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed
- **BOQ ingestion:** JSON or Excel; never call rfq2boq directly (independent product)
- **Time tracking:** 15-min increments; billable vs non-billable flag
