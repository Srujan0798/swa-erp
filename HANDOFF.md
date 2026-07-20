# Handoff Protocol

## Why this file exists
Switching orchestrators (Claude ↔ Kimi) or starting a fresh session shouldn't require re-explaining the project. This file lets the new session catch up in < 5 minutes.

## Current state
- **Active wave:** wave-9 through wave-13 (see below) — dispatched 2026-07-20
- **Status:** Waves 1-8 ✅ SHIPPED (committed in bulk at `ed71fac`, see `plan/EXECUTION.md`).
  **BUT**: waves 1-8 built a generic Client/Project/BOQ/Task/Vendor/Time/Invoice CRM, NOT the
  specific Inquiry→Agreement→Token→DocumentReference chain the client actually asked for in
  Meeting 1/2. That chain does not exist in code — see `docs/decisions/0002-core-id-chain-gap.md`.
- **Last completed:** wave-8 (reports/KPIs/exports), commit `58864df`
- **Next action:** dispatch wave-9 tasks in strict order `work/wave-9/00 → 01 → 02 → 03 → 04`
  (00 is the shared ID generator every other task depends on) — the core ID-chain gap, this is
  the highest-priority remaining work. Waves 10-13 can run in parallel/after (see roadmap below).
- **Uncommitted at handoff time:** 8 modified + 8 untracked frontend files — dangling
  wave-5/7/8 frontend work never committed. Covered by wave-11 task.
- **Never independently verified:** all "N/N tests passing" claims are self-reported in commit
  messages; Docker/E2E was never confirmed working (wave-15 blocked, no docker daemon). Covered
  by wave-12 task.
- **KleenHand cleanup:** COMPLETED — 142 sessions merged into ULTIMATE_HANDOFF.md, stale sessions cleaned
- **Open decisions:** see `docs/decisions/` (most recent first) — `0002-core-id-chain-gap.md` has
  10 open questions for Viraj, defaults are in use so dev work isn't blocked

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
9. **Core ID chain — Inquiry, Service Agreement, Token, Document Reference** — 🚀 READY TO
   DISPATCH, highest priority, closes the real client-requested MVP gap (`work/wave-9/`)
10. Sustainability metrics — ready to dispatch, depends on nothing new (`work/wave-10/`)
11. Reconcile dangling uncommitted frontend work — ready to dispatch (`work/wave-11/`)
12. Independent verification (real test run, Docker, E2E) — ready to dispatch (`work/wave-12/`)
13. Excel → ERP data migration importer — ready to dispatch, depends on wave-9+10 (`work/wave-13/`)

## Key project context
- **Tech stack:** Python 3.11, FastAPI, SQLAlchemy 2, Pydantic v2, PostgreSQL, Celery, Redis / React 18, Vite, TS, Tailwind, shadcn/ui, TanStack Query
- **Auth:** JWT + RBAC (roles: admin, pm, designer, auditor, viewer)
- **Money:** Decimal(18,2), INR default, multi-currency ready
- **Compliance standards:** NBC, ECBC, IGBC, IS fire codes (explicit references required)
- **Project lifecycle:** Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed
- **BOQ ingestion:** JSON or Excel; never call rfq2boq directly (independent product)
- **Time tracking:** 15-min increments; billable vs non-billable flag
