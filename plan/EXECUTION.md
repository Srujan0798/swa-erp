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
| 3 | Quotation / BOQ workflow | **READY TO DISPATCH** | 0/5 | spec + task files ready |
| 3 | Quotation/BOQ workflow | pending | — | depends on wave-2 |
| 4 | Task management | pending | — | depends on wave-2 |
| 5 | Vendors + Inventory | pending | — | depends on wave-2 |
| 6 | Documents + Compliance | pending | — | depends on wave-2 (independent of 3,4,5) |
| 7 | Time + Financials | pending | — | depends on wave-2 (independent of 3,4,5,6) |
| 8 | Reports + Deliverables | pending | — | depends on all above |

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

**Active wave:** wave-3
**Next action:** dispatch `work/wave-3/01-*.md` through `05-*.md` to worker agents in parallel windows.

## Changelog (waves shipped)

- **wave-1** — `df1b779` — Backend skeleton, Auth + RBAC, Users API, Frontend shell, CI + Docker
- **wave-2** — `d1e3017` — Clients + Contacts, Projects, Lifecycle transitions, Dashboard, Stats

## Changelog (waves shipped)

- **wave-1** — `df1b779` — Backend skeleton, Auth + RBAC, Users API, Frontend shell, CI + Docker
