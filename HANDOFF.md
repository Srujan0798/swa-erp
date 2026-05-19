# Handoff Protocol

## Why this file exists
Switching orchestrators (Claude ↔ Kimi) or starting a fresh session shouldn't require re-explaining the project. This file lets the new session catch up in < 5 minutes.

## Current state
- **Active wave:** wave-1 (Foundation)
- **Status:** spec written; tasks ready to dispatch
- **Last dispatched tasks:** see `work/wave-1/`
- **Last completed reports:** see `work/reports/wave-1/`
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
1. Foundation (auth, users, roles, base data model, shell)
2. Clients + Projects core (CRM-lite, project CRUD)
3. Quotation/BOQ workflow (upload BOQ, quote versions, approvals)
4. Task management (per-project tasks, assignments, deps)
5. Vendor + Inventory (vendor DB, materials catalog, RFQ-to-vendor)
6. Documents + compliance tracking (NBC/ECBC/IGBC/IS checklist)
7. Time tracking + financials (timesheets, invoicing, project P&L)
8. Reports + dashboards + deliverables (paper/report/slides/demo)
