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

| Wave | Name | Status | Tasks | Commit | Notes |
|------|------|--------|-------|--------|-------|
| 1 | Foundation | **SHIPPED** ✅ | 5/5 | `df1b779` | on main |
| 2 | Clients + Projects | **SHIPPED** ✅ | 5/5 | `d1e3017` | on main; 52 tests pass |
| 3 | Quotation / BOQ workflow | **SHIPPED** ✅ | 5/5 | `f49eac1` | on main; 97 tests pass |
| 4 | Task management | **SHIPPED** ✅ | — | `ed71fac` | bulk commit; self-reported 109/109 |
| 5 | Vendors + Inventory | **SHIPPED** ✅ | — | `ed71fac` | bulk commit; no per-task reports filed |
| 6 | Documents + Compliance | **SHIPPED** ✅ | — | `ed71fac` | bulk commit; no per-task reports filed |
| 7 | Time + Financials | **SHIPPED** ✅ | — | `ed71fac` | bulk commit; self-reported 42/42 |
| 8 | Reports + Deliverables | **SHIPPED** ✅ | — | `58864df` | self-reported 26/26 |
| 9 | Core ID chain (Inquiry/Agreement/Token/DocRef) | **SHIPPED** ✅ | 5/5 | `c3367fa` | closed the real client-requested MVP gap, see `docs/decisions/0002-core-id-chain-gap.md` |
| 10 | Sustainability metrics | **SHIPPED** ✅ | 1/1 | `a155000` | |
| 11 | Reconcile dangling frontend work | **SHIPPED** ✅ | 1/1 | `4e0655d` | |
| 12 | Independent verification (tests, Docker, E2E) | **SHIPPED** ✅ | 1/1 | `9852ec0` | 324/324 tests, found + fixed real migration/model drift, Docker never actually worked before this |
| 13 | Excel → ERP data migration importer | **SHIPPED** ✅ | 1/1 | `466d8ae` | |
| 14 | Docker Compose auto-migration + seed fix | **SHIPPED** ✅ | 1/1 | `ab0a786` | |
| 15 | E2E test fixes | **SHIPPED** ✅ | 1/1 | `4be7536` | 7/7 E2E, also fixed a real `quote.code` 500 in production code |
| 16 | Model/migration drift sweep | **SHIPPED** ✅ | 1/1 | `d5b2790` | found 2 more missing tables (notifications, timesheet_audit_log) |
| 17 | Mount notifications router | **SHIPPED** ✅ | 1/1 | `432d65d` | notifications router mounted + verified (324 passed) |
| 18 | Security hardening (secrets, rate limiting, GST on invoices) | **SHIPPED** ✅ | 1/1 | `2073c36` | prod refuses insecure SECRET_KEY, 429 on rapid login, 339 passed |
| 19 | Backup + restore + ops scripts | **SHIPPED** ✅ | 1/1 | `—` | no single commit; code in `ed71fac` mega-commit |
| 20 | Production config templates | **SHIPPED** ✅ | 1/1 | `—` | no single commit; code in `ed71fac` mega-commit |
| 21 | Handover documentation package | **SHIPPED** ✅ | 1/1 | `—` | no single commit; code in `ed71fac` mega-commit |
| 22 | Critical RBAC and auth gaps | **SHIPPED** ✅ | 1/1 | `bb6f3ec` | materials endpoints authenticated, financial modules role-gated, core-chain RBAC matrix matches client access matrix |
| 23 | Correctness bugs | **SHIPPED** ✅ | 1/1 | `23dfe05` | financial PDF now uses real ProjectCost data, money as Decimal, real soft-delete on Task, Project.version optimistic locking (0027) |
| 24 | Dead code + missing UI wiring | **SHIPPED** ✅ | 1/1 | `3cc5a90` | dead debug endpoint + dead page removed, New User button wired, delete-user/client UI, Tokens + DocumentReference reachable via navigation |
| 25 | (docs truth pass) — DONE inline, no task file | ✅ SHIPPED | — | `—` | fixed directly by the orchestrator 2026-07-21 |
| 26 | Root handoff extraction + doc cleanup | **SHIPPED** ✅ | 4/4 | `03348e3` | extracted 3 root handoffs, swept 142 archived handoffs, triaged 122 MB of session exports (no secrets) |
| 27 | Security findings + lint | **SHIPPED** ✅ | 1/1 | `aa60e73` | backup scripts hardened against credential leakage, pre-commit hooks pinned to SHAs, ruff swept, backup-safety test suite added |
| 28 | Doc consolidation | **SHIPPED** ✅ | 1/1 | `339313e` | `HANDOFF_FINAL.md`/`wave9handoff`/`wave10handoff`/`OS_SETUP.md` archived via `git mv`, KIMI.md → CLAUDE.md symlink, ADR-0003 de-duplicated |
| 29 | Stale claim fixes | **SHIPPED** ✅ | 1/1 | `39a6c12` | 9 docs corrected to match real repo state (backups, GST, Celery/MinIO target-state, test counts, version/tag reconciliation) |
| 30 | Final release + submission package | **SHIPPED** ✅ | 1/1 | `db243e0` | full verification sweep + live end-to-end business-flow validation, version cut at 1.0.0, `deliverables/SUBMISSION.md` produced |
| 31 | Deferred features: MinIO storage + Celery worker | **SHIPPED** ✅ | 2/2 | `d152a20` | object storage abstraction (`src/backend/core/storage.py`, `local` default | `minio` opt-in) + Celery app (`src/backend/workers/`) with async export endpoints. Version cut 1.0.1 |
| 32 | Real CI quality gates | **SHIPPED** ✅ | 1/1 | `486dce7` | See `work/ACTIVE.md` + `work/reports/wave-32/` |
| 33 | Backend coverage ≥85% | **SHIPPED** ✅ | 3/3 | `9cb2b22` | 86% overall; 5 target services ≥70% |
| 34 | Frontend Vitest suite ≥60% | **SHIPPED** ✅ | 2/2 | `6e8f7be` | |
| 35 | Load validation 10–150 users | **SHIPPED** ✅ | 1/1 | `586806d` | `docs/PERFORMANCE.md` |
| 36 | Observability | **SHIPPED** ✅ | 2/2 | `d1bfb63` | code + `02-post-merge-fixes.report.md` (01 never written) |
| 37 | Independent adversarial review | **SHIPPED** ✅ | 1/1 | `82bf291` | |
| 38 | Professional submission package | **SHIPPED** ✅ | 1/1 | `—` | no single commit; code in `96852fe` wave-47 seal |
| 39 | Repo organization | **SHIPPED** ✅ | 1/1 | `889215a` | |
| 40-47 | Final seal passes (gates, 0-failed suite, DoD A–E) | **SHIPPED** ✅ | 5/5 | `96852fe` | on worktree `w47`; report `work/reports/wave-47/01-final-seal.report.md` |
| 48 | Production hardening (logging, CSP, pagination, audit, idempotency, frontend loading/bundling) | **SHIPPED** ✅ | 1/1 | `af04262` | `work/reports/wave-48/01-production-hardening.report.md` |
| 49 | Transaction atomicity for Inquiry→Client→Project | **SHIPPED** ✅ | 1/1 | `f26b420` | `work/reports/wave-49/01-transaction-atomicity.report.md` |
| 50 | Security risks (job IDOR, /metrics auth) + deterministic test suite | **SHIPPED** ✅ | 2/2 | `8652036` | `work/reports/wave-50/02-deterministic-test-suite.report.md` |
| 51 | Final re-seal + submission refresh | **SHIPPED** ✅ | 1/1 | `4396581` | `work/reports/wave-51/01-final-reseal-and-submission.report.md` |

**Waves 1–39, 43–51 are SHIPPED.** Engineering closed 2026-09-19.
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

**Active wave:** none — waves 32–39, 43–51 SHIPPED (48 production-hardening, 49 atomicity, 50 security, 51 re-seal round 6 at `b20c5f5` — reseal report `work/reports/wave-51/01-final-reseal-and-submission.report.md`). Engineering sealed by wave-47 (2026-08-28).
Full-stack pytest: 572 passed / 1 skipped / 0 failed (wave-47 Docker seal; NOT re-measured 2026-09-17 — no Docker. Same-date partitioned runs at `b20c5f5`: 571 passed / 30 failed / 9 skipped, Redis down, pytest 9 vs pinned 8.3.3). Coverage: 85% (wave-47). Vitest: 580 passed / 0 failed; coverage 65.16/55.47/62.31/66.21 (2026-09-17, at `b20c5f5`). Static: ruff/mypy clean; black/tsc/eslint FAIL (see reseal report).
Product release remains **v1.0.1**. Deploy remains external (Viraj / no IT dept).
