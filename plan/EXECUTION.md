# Execution Plan — SWA ERP

## Wave dependency graph

```
wave-1 (Foundation)
  │
  ├──→ wave-2 (Clients + Projects)
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
| 1 | Foundation | **READY TO DISPATCH** | 0/5 | spec written; task files in work/wave-1/ |
| 2 | Clients + Projects | pending | — | depends on wave-1 |
| 3 | Quotation/BOQ workflow | pending | — | depends on wave-2 |
| 4 | Task management | pending | — | depends on wave-2 |
| 5 | Vendors + Inventory | pending | — | depends on wave-2 |
| 6 | Documents + Compliance | pending | — | depends on wave-2 (independent of 3,4,5) |
| 7 | Time + Financials | pending | — | depends on wave-2 (independent of 3,4,5,6) |
| 8 | Reports + Deliverables | pending | — | depends on all above |

## Wave details

### Wave 1 — Foundation
**Goal:** Bootable backend + frontend with auth, RBAC, users, app shell. No business features yet.
**Tasks (5):**
1. Backend skeleton — FastAPI app, config, db session, Alembic
2. Auth + RBAC — JWT, bcrypt, roles, login/refresh/reset endpoints
3. Users API — CRUD users, role assignment
4. Frontend shell — Vite + React + Tailwind + shadcn/ui, router, auth flow
5. CI + Docker — workflows, Dockerfile, docker-compose for dev

**Acceptance:**
- `make dev` brings up backend + frontend + postgres + redis
- Login flow works end-to-end
- `pytest tests/` passes
- CI green on first push

### Wave 2 — Clients + Projects (core)
**Goal:** Manage clients and projects. CRM-lite + project lifecycle.
**Tasks (~6):** clients API, projects API, lifecycle transitions, dashboard page, client/project list/detail pages, search & pagination.

### Wave 3 — Quotation / BOQ Workflow
**Goal:** Upload BOQ files (JSON/Excel), version them, generate and send quotes.
**Tasks (~5):** BOQ parser (JSON + Excel), BOQ versioning, quote generation, PDF export, send-to-client.

### Wave 4 — Task Management
**Goal:** Per-project tasks with assignees, dependencies, statuses.
**Tasks (~4):** tasks API, dependency graph, assignment notifications, task UI (kanban + list).

### Wave 5 — Vendors + Inventory
**Goal:** Vendor database, materials catalog, vendor-RFQ workflow.
**Tasks (~5):** vendors API, materials catalog, vendor-RFQ generation, comparison view, vendor portal stub.

### Wave 6 — Documents + Compliance
**Goal:** Document storage + compliance checklists (NBC/ECBC/IGBC/IS).
**Tasks (~5):** document upload/versioning, checklist data model (versioned per standard), checklist UI, audit trail per checklist item, document linking to projects.

### Wave 7 — Time + Financials
**Goal:** Timesheets, invoicing, project P&L.
**Tasks (~5):** timesheets API, invoice generation, GST-aware totals, payment tracking, project P&L view.

### Wave 8 — Reports + Deliverables
**Goal:** Dashboards (utilization, project health, revenue forecast) + final deliverables.
**Tasks (~5):** dashboard widgets, exports (Excel/PDF), final technical report, slide deck, demo video script.

## Current activity

**Active wave:** wave-1
**Next action:** dispatch `work/wave-1/01-*.md` through `05-*.md` to OpenCode CLI workers in parallel windows.

## Changelog (waves shipped)

_None yet — wave-1 in progress._
