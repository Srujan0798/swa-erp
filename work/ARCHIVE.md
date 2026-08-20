# Work Archive — waves 1-31 (SHIPPED)

Index of the first 31 waves — the shipped history. Waves 32+ (shipped, in-flight, and queued)
are tracked in [`work/ACTIVE.md`](ACTIVE.md). **Do not dispatch work into these folders** — they
are historical record. Live work lives in `work/wave-32+`.

Reports live under `work/reports/wave-N/`; briefs under `work/wave-N/`. Some early waves
(4-8, 10, 25) were merged without per-task reports — that gap is why wave-12 and wave-32 exist.

| # | Purpose (one line) | Status | Brief | Report |
|---|---|---|---|---|
| 1 | Foundation — bootable backend + frontend, auth/RBAC, users, app shell | SHIPPED | [`work/wave-1/`](wave-1/) | [`work/reports/wave-1/`](reports/wave-1/) |
| 2 | Clients + Projects — CRM-lite, project lifecycle, dashboard | SHIPPED | [`work/wave-2/`](wave-2/) | [`work/reports/wave-2/`](reports/wave-2/) |
| 3 | Quotation/BOQ workflow — BOQ upload, versioning, quotes, PDF | SHIPPED | [`work/wave-3/`](wave-3/) | [`work/reports/wave-3/`](reports/wave-3/) |
| 4 | Task management — tasks, dependencies, assignments, kanban | SHIPPED | [`work/wave-4/`](wave-4/) | [`work/reports/wave-4/`](reports/wave-4/) |
| 5 | Vendors + Inventory — vendors, materials catalog, RFQ | SHIPPED | [`work/wave-5/`](wave-5/) | — (no per-task reports) |
| 6 | Documents + Compliance — document storage, compliance checklists (NBC/ECBC/IGBC/IS) | SHIPPED | [`work/wave-6/`](wave-6/) | — (no per-task reports) |
| 7 | Time + Financials — timesheets, invoicing, project P&L | SHIPPED | [`work/wave-7/`](wave-7/) | [`work/reports/wave-7/`](reports/wave-7/) |
| 8 | Reports + Deliverables — dashboards, reports, exports | SHIPPED | [`work/wave-8/`](wave-8/) | — (no per-task reports) |
| 9 | Core ID chain — Inquiry → Service Agreement → Token → Document Reference | SHIPPED | [`work/wave-9/`](wave-9/) | [`work/reports/wave-9/`](reports/wave-9/) |
| 10 | Sustainability metrics | SHIPPED | [`work/wave-10/`](wave-10/) | [`work/reports/wave-10/`](reports/wave-10/) |
| 11 | Reconcile dangling frontend work from prior sessions | SHIPPED | [`work/wave-11/`](wave-11/) | [`work/reports/wave-11/`](reports/wave-11/) |
| 12 | Independent verification — tests/Docker/E2E, found + fixed real migration/model drift | SHIPPED | [`work/wave-12/`](wave-12/) | [`work/reports/wave-12/`](reports/wave-12/) |
| 13 | Excel → ERP one-time data migration importer | SHIPPED | [`work/wave-13/`](wave-13/) | [`work/reports/wave-13/`](reports/wave-13/) |
| 14 | Docker Compose auto-migration + seed fix | SHIPPED | [`work/wave-14/`](wave-14/) | [`work/reports/wave-14/`](reports/wave-14/) |
| 15 | E2E test fixes (also fixed a real `quote.code` 500) | SHIPPED | [`work/wave-15/`](wave-15/) | [`work/reports/wave-15/`](reports/wave-15/) |
| 16 | Model/migration drift sweep (2 missing tables found) | SHIPPED | [`work/wave-16/`](wave-16/) | [`work/reports/wave-16/`](reports/wave-16/) |
| 17 | Mount notifications router | SHIPPED | [`work/wave-17/`](wave-17/) | [`work/reports/wave-17/`](reports/wave-17/) |
| 18 | Security hardening — secrets, rate limiting, GST on invoices | SHIPPED | [`work/wave-18/`](wave-18/) | [`work/reports/wave-18/`](reports/wave-18/) |
| 19 | Backup/restore/ops scripts | SHIPPED | [`work/wave-19/`](wave-19/) | [`work/reports/wave-19/`](reports/wave-19/) |
| 20 | Production config templates | SHIPPED | [`work/wave-20/`](wave-20/) | [`work/reports/wave-20/`](reports/wave-20/) |
| 21 | Handover documentation package | SHIPPED | [`work/wave-21/`](wave-21/) | [`work/reports/wave-21/`](reports/wave-21/) |
| 22 | Critical RBAC and auth gaps | SHIPPED | [`work/wave-22/`](wave-22/) | [`work/reports/wave-22/`](reports/wave-22/) |
| 23 | Correctness bugs — Decimal money, optimistic locking, soft delete | SHIPPED | [`work/wave-23/`](wave-23/) | [`work/reports/wave-23/`](reports/wave-23/) |
| 24 | Dead code + missing UI wiring | SHIPPED | [`work/wave-24/`](wave-24/) | [`work/reports/wave-24/`](reports/wave-24/) |
| 25 | Docs truth pass (done inline by orchestrator, no task file) | SHIPPED | — | — |
| 26 | Root handoff extraction + doc cleanup (142 handoffs swept) | SHIPPED | [`work/wave-26/`](wave-26/) | [`work/reports/wave-26/`](reports/wave-26/) |
| 27 | Security findings + lint sweep | SHIPPED | [`work/wave-27/`](wave-27/) | [`work/reports/wave-27/`](reports/wave-27/) |
| 28 | Doc consolidation (archived root handoffs, KIMI→CLAUDE symlink) | SHIPPED | [`work/wave-28/`](wave-28/) | [`work/reports/wave-28/`](reports/wave-28/) |
| 29 | Stale claim fixes (9 docs corrected to real repo state) | SHIPPED | [`work/wave-29/`](wave-29/) | [`work/reports/wave-29/`](reports/wave-29/) |
| 30 | Final release + submission package — cut **v1.0.0** | SHIPPED | [`work/wave-30/`](wave-30/) | [`work/reports/wave-30/`](reports/wave-30/) |
| 31 | Deferred features — MinIO storage + Celery worker — cut **v1.0.1** | SHIPPED | [`work/wave-31/`](wave-31/) | [`work/reports/wave-31/`](reports/wave-31/) |

## How this archive was built

Generated wave-39 from `plan/EXECUTION.md` status table + per-wave brief/report folders.
Every wave 1-31 is SHIPPED and appears here; every wave appears in exactly one of
`work/ARCHIVE.md` (1-31) or `work/ACTIVE.md` (32-39).