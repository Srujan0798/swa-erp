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
| 17 | Mount notifications router | **SHIPPED** ✅ | 1/1 | `work/reports/wave-17/01-mount-notifications-router.report.md`; notifications router mounted + verified (324 passed) |
| 18 | Security hardening (secrets, rate limiting, GST on invoices) | **SHIPPED** ✅ | 1/1 | `work/reports/wave-18/01-security-hardening.report.md`; prod refuses insecure SECRET_KEY, 429 on rapid login, 339 passed |
| 19 | Backup + restore + ops scripts | **SHIPPED** ✅ | 1/1 | `work/reports/wave-19/01-backup-and-ops-scripts.report.md`; closes the Meeting-2-requested gap — scripts + `docs/runbook_backup_restore.md` + 5 tests |
| 20 | Production config templates | **SHIPPED** ✅ | 1/1 | `work/reports/wave-20/01-production-config-templates.report.md`; `docker-compose.prod.yml` + `.env.production.example` with `PENDING IT ANSWER (Q#)` markers + `docs/DEPLOYMENT_CHECKLIST.md` |
| 21 | Handover documentation package | **SHIPPED** ✅ | 1/1 | `work/reports/wave-21/01-handover-documentation.report.md`; admin guide, user guide, training one-pager, architecture overview for Viraj |
| 22 | Critical RBAC and auth gaps | **SHIPPED** ✅ | 1/1 | `work/reports/wave-22/01-critical-rbac-and-auth-gaps.report.md`; materials endpoints authenticated, financial modules (project_pnl/exports/invoice-status) role-gated, core-chain RBAC matrix matches client access matrix (PM+Designer for DBR/KDR, Auditor+Designer for Reforge), compliance-review and task/RFQ transitions gated |
| 23 | Correctness bugs | **SHIPPED** ✅ | 1/1 | `work/reports/wave-23/01-correctness-bugs.report.md`; financial PDF now uses real ProjectCost data, money as Decimal, real soft-delete on Task, Project.version optimistic locking (0027) |
| 24 | Dead code + missing UI wiring | **SHIPPED** ✅ | 1/1 | `work/reports/wave-24/01-dead-code-and-ui-wiring.report.md`; dead debug endpoint + dead page removed, New User button wired, delete-user/client UI, Tokens + DocumentReference reachable via navigation, notifications un-stubbed (0026) |
| 25 | (docs truth pass) — DONE inline, no task file | ✅ SHIPPED | — | fixed directly by the orchestrator 2026-07-21: `docs/api.md`, `docs/conventions.md`, `docs/deployment.md`, `docs/runbook.md`, `HIERARCHY.md`, `orchestrator/rules/security.md`, `docs/SCOPE_GUARD.md`, `orchestrator/memory/MEMORY.md` |
| 26 | Root handoff extraction + doc cleanup | **SHIPPED** ✅ | 4/4 | `work/reports/wave-26/*`; extracted 3 root handoffs, swept 142 archived handoffs, triaged 122 MB of session exports (no secrets), produced current-docs overlap map |
| 27 | Security findings + lint | **SHIPPED** ✅ | 1/1 | `work/reports/wave-27/01-security-findings-and-lint.report.md`; backup scripts hardened against credential leakage, pre-commit hooks pinned to SHAs, ruff swept, backup-safety test suite added |
| 28 | Doc consolidation | **SHIPPED** ✅ | 1/1 | `work/reports/wave-28/01-execute-doc-consolidation.report.md`; `HANDOFF_FINAL.md`/`wave9handoff`/`wave10handoff`/`OS_SETUP.md` archived via `git mv`, KIMI.md → CLAUDE.md symlink, ADR-0003 de-duplicated, conventions/history enriched |
| 29 | Stale claim fixes | **SHIPPED** ✅ | 1/1 | `work/reports/wave-29/01-stale-claim-fixes.report.md`; 9 docs corrected to match real repo state (backups, GST, Celery/MinIO target-state, test counts, version/tag reconciliation) |
| 30 | Final release + submission package | **SHIPPED** ✅ | 1/1 | this file; full verification sweep + live end-to-end business-flow validation, version cut at 1.0.0, `deliverables/SUBMISSION.md` produced. See `work/reports/wave-30/01-final-release-and-submission.report.md` |
| 31 | Deferred features: MinIO storage + Celery worker | **SHIPPED** ✅ | 2/2 | `work/reports/wave-31/01-wire-minio-storage.report.md`, `work/reports/wave-31/02-wire-celery-worker.report.md`; object storage abstraction (`src/backend/core/storage.py`, `local` default | `minio` opt-in) + Celery app (`src/backend/workers/`) with async export endpoints. Version cut 1.0.1. See `CHANGELOG.md` |
| 32 | Real CI quality gates | **SHIPPED** ✅ | 1/1 | See `work/ACTIVE.md` + `work/reports/wave-32/` |
| 33 | Backend coverage ≥85% | **SHIPPED** ✅ | 3/3 | `work/reports/wave-33/` — 86% overall; 5 target services ≥70% |
| 34 | Frontend Vitest suite ≥60% | **SHIPPED** ✅ | 2/2 | `work/reports/wave-34/` |
| 35 | Load validation 10–150 users | **SHIPPED** ✅ | 1/1 | `docs/PERFORMANCE.md` |
| 36 | Observability | **SHIPPED** ✅ | 2/2 | code + `02-post-merge-fixes.report.md` (01 never written) |
| 37 | Independent adversarial review | **SHIPPED** ✅ | 1/1 | `work/reports/wave-37/01-independent-review.report.md` |
| 38 | Professional submission package | **SHIPPED** ✅ | 1/1 | `work/reports/wave-38/01-submission-package.report.md` |
| 39 | Repo organization | **SHIPPED** ✅ | 1/1 | `work/reports/wave-39/` |
| 40-47 | Final seal passes (gates, 0-failed suite, DoD A–E) | **SHIPPED** ✅ | 5/5 | `96852fe` on worktree `w47`; report `work/reports/wave-47/01-final-seal.report.md` |

**Waves 1–39, 43–47 are SHIPPED.** Engineering closed 2026-08-28.
Product release remains **v1.0.1**. Deploy remains external (Viraj / no IT dept).

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

**Active wave:** none — waves 32–39, 43–47 SHIPPED. Engineering sealed by wave-47 (2026-08-28).
Full-stack pytest: 572 passed / 1 skipped / 0 failed. Coverage: 85%. Vitest: 523 passed / 0 failed.
Product release remains **v1.0.1**. Deploy remains external (Viraj / no IT dept).
