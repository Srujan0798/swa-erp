# Execution Plan — SWA ERP

## Wave dependency graph

```
wave-1 (Foundation) ✅ SHIPPED
  │
  ├──→ wave-2 (Clients + Projects) ← READY TO DISPATCH
  │      │
  │      ├──→ wave-3 (Quotation/BOQ workflow)
  │      ├──→ wave-4 (Task management)
  │      └──→ wave-5 (Vendors + Inventory)         ──┐
  │                                                  │
  │      ┌──→ wave-6 (Documents + Compliance)  ──────┤
  │      │                                           │
  │      └──→ wave-7 (Time tracking + Financials) ───┤
  │                                                  │
  │                                          ┌───────▼────────┐
  │                                          │  wave-8         │
  └──────────────────────────────────────────│  Reports +      │
                                             │  Dashboards +   │
                                             │  Deliverables   │
                                             └─────────────────┘
```

## Status

| Wave | Name | Status | Tasks | Notes |
|---|---|---|---|---|
| 1 | Foundation | **SHIPPED** ✅ | 5/5 | `df1b779` on main |
| 2 | Clients + Projects | **SHIPPED** ✅ | 5/5 | `d1e3017` on main; 52 tests pass |
| 3 | Quotation / BOQ workflow | **SHIPPED** ✅ | 5/5 | `f49eac1` on main; 97 tests pass |
| 4 | Task management | **SHIPPED** ✅ | — | bulk commit `ed71fac`, self-reported 109/109 |
| 5 | Vendors + Inventory | **SHIPPED** ✅ | — | bulk commit `ed71fac`, no per-task reports filed |
| 6 | Documents + Compliance | **SHIPPED** ✅ | — | bulk commit `ed71fac`, no per-task reports filed |
| 7 | Time + Financials | **SHIPPED** ✅ | — | bulk commit `ed71fac`, self-reported 42/42 |
| 8 | Reports + Deliverables | **SHIPPED** ✅ | — | `58864df`, self-reported 26/26 |
| 9 | Core ID chain (Inquiry/Agreement/Token/DocRef) | **SHIPPED** ✅ | 5/5 | closed the real client-requested MVP gap, see `docs/decisions/0002-core-id-chain-gap.md`. `c3367fa` |
| 10 | Sustainability metrics | **SHIPPED** ✅ | 1/1 | `a155000` |
| 11 | Reconcile dangling frontend work | **SHIPPED** ✅ | 1/1 | `4e0655d` |
| 12 | Independent verification (tests, Docker, E2E) | **SHIPPED** ✅ | 1/1 | `9852ec0`; 324/324 tests, found + fixed real migration/model drift, Docker never actually worked before this |
| 13 | Excel → ERP data migration importer | **SHIPPED** ✅ | 1/1 | `466d8ae` |
| 14 | Docker Compose auto-migration + seed fix | **SHIPPED** ✅ | 1/1 | `ab0a786` |
| 15 | E2E test fixes | **SHIPPED** ✅ | 1/1 | `4be7536`; 7/7 E2E, also fixed a real `quote.code` 500 in production code |
| 16 | Model/migration drift sweep | **SHIPPED** ✅ | 1/1 | `d5b2790`; found 2 more missing tables (notifications, timesheet_audit_log) |
| 17 | Mount notifications router | ready to dispatch | 0/1 | `work/wave-17/`; small wiring gap flagged by wave-16 |
| 18 | Security hardening (secrets, rate limiting, GST on invoices) | ready to dispatch | 0/1 | `work/wave-18/`; does not depend on Viraj/IT answers |
| 19 | Backup + restore + ops scripts | ready to dispatch | 0/1 | `work/wave-19/`; closes a Meeting-2-requested gap that was never built |
| 20 | Production config templates | ready to dispatch | 0/1 | `work/wave-20/`; placeholders marked for each pending IT answer, ready for instant swap |
| 21 | Handover documentation package | ready to dispatch | 0/1 | `work/wave-21/`; admin guide, user guide, the architecture summary Viraj asked for in Meeting 2 and never got |
| 22 | Critical RBAC and auth gaps | **SHIPPED** ✅ | 1/1 | `work/reports/wave-22/01-critical-rbac-and-auth-gaps.report.md`; materials endpoints authenticated, financial modules (project_pnl/exports/invoice-status) role-gated, core-chain RBAC matrix matches client access matrix (PM+Designer for DBR/KDR, Auditor+Designer for Reforge), compliance-review and task/RFQ transitions gated |
| 23 | Correctness bugs | **SHIPPED** ✅ | 1/1 | `work/reports/wave-23/01-correctness-bugs.report.md`; financial PDF now uses real ProjectCost data, money as Decimal, real soft-delete on Task, Project.version optimistic locking (0027) |
| 24 | Dead code + missing UI wiring | **SHIPPED** ✅ | 1/1 | `work/reports/wave-24/01-dead-code-and-ui-wiring.report.md`; dead debug endpoint + dead page removed, New User button wired, delete-user/client UI, Tokens + DocumentReference reachable via navigation, notifications un-stubbed (0026) |
| 25 | (docs truth pass) — DONE inline, no task file | ✅ SHIPPED | — | fixed directly by the orchestrator 2026-07-21: `docs/api.md`, `docs/conventions.md`, `docs/deployment.md`, `docs/runbook.md`, `HIERARCHY.md`, `orchestrator/rules/security.md`, `docs/SCOPE_GUARD.md`, `orchestrator/memory/MEMORY.md` |
| 26 | Root handoff extraction + doc cleanup | **SHIPPED** ✅ | 4/4 | `work/reports/wave-26/*`; extracted 3 root handoffs, swept 142 archived handoffs, triaged 122 MB of session exports (no secrets), produced current-docs overlap map |
| 27 | Security findings + lint | **SHIPPED** ✅ | 1/1 | `work/reports/wave-27/01-security-findings-and-lint.report.md`; backup scripts hardened against credential leakage, pre-commit hooks pinned to SHAs, ruff swept, backup-safety test suite added |
| 28 | Doc consolidation | **SHIPPED** ✅ | 1/1 | `work/reports/wave-28/01-execute-doc-consolidation.report.md`; `HANDOFF_FINAL.md`/`wave9handoff`/`wave10handoff`/`OS_SETUP.md` archived via `git mv`, KIMI.md → CLAUDE.md symlink, ADR-0003 de-duplicated, conventions/history enriched |
| 29 | Stale claim fixes | **SHIPPED** ✅ | 1/1 | `work/reports/wave-29/01-stale-claim-fixes.report.md`; 9 docs corrected to match real repo state (backups, GST, Celery/MinIO target-state, test counts, version/tag reconciliation) |
| 30 | Final release + submission package | **SHIPPED** ✅ | 1/1 | this file; full verification sweep + live end-to-end business-flow validation, version cut at 1.0.0, `deliverables/SUBMISSION.md` produced. See `work/reports/wave-30/01-final-release-and-submission.report.md` |

**Waves 22-30 are all SHIPPED** (see status table above; per-wave reports in `work/reports/wave-N/`).
All of the audit-driven fixes (22-24), the security/lint pass (27), and the docs-consolidation
passes (26, 28, 29) landed and were verified. **Wave-30 cut the first real release — `1.0.0`**
(2026-08-07), replacing the stale `0.2.0` version files, and produced the client submission
package at `deliverables/SUBMISSION.md`.

The only remaining external blockers are Viraj's 3 open decisions
(`docs/decisions/0002-core-id-chain-gap.md`) and IT's 8 answers (`docs/IT_BRIEF.md`) — nothing
in code can resolve those.

**Note on waves 4-8:** these were committed in one mega-commit (`ed71fac`) rather than the
per-task worker/report process this file describes — `work/reports/` is empty for waves 5, 6,
and 8 despite the code existing. Treat "SHIPPED" above as "code exists and compiles", not as
"acceptance criteria were checked task-by-task." Wave-12 exists specifically to close that gap.

## Wave details

### Wave 1 — Foundation ✅
**Goal:** Bootable backend + frontend with auth, RBAC, users, app shell.
**Shipped:** `df1b779` on `main`

### Wave 2 — Clients + Projects (core)
**Goal:** Manage clients and projects. CRM-lite + project lifecycle.
**Tasks (5):**
1. Clients API — Client + Contact models, CRUD, search, pagination
2. Projects API — Project model, CRUD, search, status filter, team assignment
3. Lifecycle + Stats Service — state machine, transitions, audit, /projects/stats
4. Dashboard Frontend — stats cards, recent projects/clients, quick actions
5. Clients + Projects UI — list/detail pages, forms, search, status filters, lifecycle buttons

**Acceptance:**
- `pytest tests/wave-2/` passes 100%
- PM can create client → create project → assign team → transition status end-to-end
- Dashboard shows real project stats
- CI green on push

### Wave 3 — Quotation / BOQ Workflow
**Goal:** Upload BOQ files (JSON/Excel), version them, generate and send quotes.

### Wave 4 — Task Management
**Goal:** Per-project tasks with assignees, dependencies, statuses.

### Wave 5 — Vendors + Inventory
**Goal:** Vendor database, materials catalog, vendor-RFQ workflow.

### Wave 6 — Documents + Compliance
**Goal:** Document storage + compliance checklists (NBC/ECBC/IGBC/IS).

### Wave 7 — Time + Financials
**Goal:** Timesheets, invoicing, project P&L.

### Wave 8 — Reports + Deliverables
**Goal:** Dashboards (utilization, project health, revenue forecast) + final deliverables.

## Current activity

**This section was stale** (leftover from wave-3, never updated across 13 subsequent waves —
directly contradicted the accurate status table above; see `docs/PROJECT_HISTORY.md` and a
2026-07-21 full-project audit for why this matters). The status table above this section is the
current, correct source of truth. See `CHANGELOG.md` for the full shipped-changes history
instead of duplicating it here.

**Active wave:** none — waves 1-30 shipped (see status table above). Wave-30 cut the
`1.0.0` client-submission release and produced `deliverables/SUBMISSION.md`.
**Next action:** hand over per `deliverables/SUBMISSION.md` (deploy checklist, Excel import,
support/next steps).
