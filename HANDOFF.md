# Handoff Protocol

## Why this file exists
Switching orchestrators (Claude ↔ Kimi) or starting a fresh session shouldn't require re-explaining the project. This file lets the new session catch up in < 5 minutes.

## Current state
- **Active wave:** wave-3 (Quotation / BOQ Workflow)
- **Status:** Wave 1 ✅ SHIPPED, Wave 2 ✅ SHIPPED, Wave 3 spec + tasks ready to dispatch
- **Last completed:** Wave 2 at commit `d1e3017` (52 tests pass)
- **Next action:** Dispatch wave-3 tasks (5 task files in `work/wave-3/`)
- **KleenHand cleanup:** COMPLETED — 142 sessions merged into ULTIMATE_HANDOFF.md, stale sessions cleaned
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
3. Quotation/BOQ workflow (upload BOQ, quote versions, approvals) — 🚀 **READY TO DISPATCH**
4. Task management (per-project tasks, assignments, deps) — pending
5. Vendor + Inventory (vendor DB, materials catalog, RFQ-to-vendor) — pending
6. Documents + compliance tracking (NBC/ECBC/IGBC/IS checklist) — pending
7. Time tracking + financials (timesheets, invoicing, project P&L) — pending
8. Reports + dashboards + deliverables (paper/report/slides/demo) — pending

## Key project context
- **Tech stack:** Python 3.11, FastAPI, SQLAlchemy 2, Pydantic v2, PostgreSQL, Celery, Redis / React 18, Vite, TS, Tailwind, shadcn/ui, TanStack Query
- **Auth:** JWT + RBAC (roles: admin, pm, designer, auditor, viewer)
- **Money:** Decimal(18,2), INR default, multi-currency ready
- **Compliance standards:** NBC, ECBC, IGBC, IS fire codes (explicit references required)
- **Project lifecycle:** Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed
- **BOQ ingestion:** JSON or Excel; never call rfq2boq directly (independent product)
- **Time tracking:** 15-min increments; billable vs non-billable flag
