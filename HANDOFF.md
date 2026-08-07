# Handoff Protocol

## Why this file exists
Switching orchestrators (Claude ↔ Kimi) or starting a fresh session shouldn't require re-explaining the project. This file lets the new session catch up in < 5 minutes.

## Current state (2026-07-21 — this section previously went stale for a full day; if you're
reading this in a future session, check `plan/EXECUTION.md`'s status table and `git log` before
trusting anything below, don't repeat that mistake)

- **Status:** Waves 1-16 ✅ SHIPPED and independently verified (7/7 E2E,
  Docker boots clean from cold). The real client-requested core chain (Inquiry→Agreement→Token→
  DocumentReference, waves 9-10) is built and traced correctly against
  `resources/MEETINGS_MASTER.md` — see the 2026-07-21 four-agent audit findings referenced below.
  **Backend test suite: 393/393 passing** (`python3 -m pytest tests/ -q`, verified 2026-08-07).
  **Corrected 2026-08-07** — this line previously said "324/324"; that count predates waves 17-27.
- **Waves 17-21** (notifications mount, security hardening, backup scripts, prod config
  templates, handover docs): task briefs exist in `work/wave-N/`, check `work/reports/wave-N/`
  for which have actually landed — don't assume, verify.
- **A full-project traceability audit ran 2026-07-21** (4 parallel agents: core-chain backend,
  legacy CRM waves 1-8, frontend↔backend wiring, full docs sweep) and found real, unfixed issues
  as of this writing — **check `plan/EXECUTION.md`'s wave table for waves 22+ (security fixes,
  correctness bugs, dead-code/UI-wiring cleanup) to see current status**, don't assume they're
  done just because this file mentions them. Headline findings: unauthenticated materials
  endpoints, zero RBAC on financial modules (`project_pnl`, `exports`), a fabricated
  70%/30%-ratio financial PDF report, RBAC gated PM-only across the whole core chain when the
  client's own access matrix requires PM+Designer (and Auditor+Designer for Reforge/DPR) — full
  detail was in the audit agents' output, not preserved in a single file; re-run a similar audit
  if this context is lost and no wave-22+ reports exist yet.
- **External blockers, unaffected by any of the above:** Viraj's 3 open decisions
  (`docs/decisions/0002-core-id-chain-gap.md`) and IT's 8 infra answers (`docs/IT_BRIEF.md`,
  already sent) — nothing code can resolve there.
- **KleenHand cleanup:** COMPLETED — 142 sessions merged, then that merge itself was found to be
  low-value noise and distilled into `docs/PROJECT_HISTORY.md` on 2026-07-20; originals archived
  at `docs/historical/`.
- **Open decisions:** see `docs/decisions/` (most recent first)

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
17. Mount notifications router — check `work/reports/wave-17/` for status
18-21. Security hardening, backup scripts, prod config templates, handover docs — check
   `work/reports/wave-N/` for which have landed; see `plan/EXECUTION.md`'s status table
22+. Fixes from the 2026-07-21 full-project audit (security gaps, correctness bugs, dead-code/
   UI-wiring) — check `plan/EXECUTION.md` for current numbering and status
13. Excel → ERP data migration importer — ready to dispatch, depends on wave-9+10 (`work/wave-13/`)

## Key project context
- **Tech stack:** Python 3.11, FastAPI, SQLAlchemy 2, Pydantic v2, PostgreSQL, Redis, React 18, Vite, TS, Tailwind, shadcn/ui, TanStack Query. (Celery is an installed dependency only — no worker exists; storage is a local `uploads/` dir, MinIO/S3 not wired — see `HIERARCHY.md`)
- **Auth:** JWT + RBAC (roles: admin, pm, designer, auditor, viewer)
- **Money:** Decimal(18,2), INR default, multi-currency ready
- **Compliance standards:** NBC, ECBC, IGBC, IS fire codes (explicit references required)
- **Project lifecycle:** Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed
- **BOQ ingestion:** JSON or Excel; never call rfq2boq directly (independent product)
- **Time tracking:** 15-min increments; billable vs non-billable flag
