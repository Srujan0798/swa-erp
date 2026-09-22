# Work Archive — waves 1-31 (SHIPPED)

Index of the first 31 waves — the shipped history. Waves 32+ (shipped, in-flight, and queued)
are tracked in [`work/ACTIVE.md`](ACTIVE.md). **Do not dispatch work into these folders** — they
are historical record. Live work lives in `work/wave-32+`.

Reports and briefs for waves 1-31 were archived during repository reorganization (wave-39).
This table preserves the historical index; the per-wave folders no longer exist in the filesystem.

| # | Purpose (one line) | Status | Brief | Report |
|---|---|---|---|---|
| 1 | Foundation — bootable backend + frontend, auth/RBAC, users, app shell | SHIPPED | (archived) | (archived) |
| 2 | Clients + Projects — CRM-lite, project lifecycle, dashboard | SHIPPED | (archived) | (archived) |
| 3 | Quotation/BOQ workflow — BOQ upload, versioning, quotes, PDF | SHIPPED | (archived) | (archived) |
| 4 | Task management — tasks, dependencies, assignments, kanban | SHIPPED | (archived) | (archived) |
| 5 | Vendors + Inventory — vendors, materials catalog, RFQ | SHIPPED | (archived) | — (no per-task reports) |
| 6 | Documents + Compliance — document storage, compliance checklists (NBC/ECBC/IGBC/IS) | SHIPPED | (archived) | — (no per-task reports) |
| 7 | Time + Financials — timesheets, invoicing, project P&L | SHIPPED | (archived) | (archived) |
| 8 | Reports + Deliverables — dashboards, reports, exports | SHIPPED | (archived) | — (no per-task reports) |
| 9 | Core ID chain — Inquiry → Service Agreement → Token → Document Reference | SHIPPED | (archived) | (archived) |
| 10 | Sustainability metrics | SHIPPED | (archived) | (archived) |
| 11 | Reconcile dangling frontend work from prior sessions | SHIPPED | (archived) | (archived) |
| 12 | Independent verification — tests/Docker/E2E, found + fixed real migration/model drift | SHIPPED | (archived) | (archived) |
| 13 | Excel → ERP one-time data migration importer | SHIPPED | (archived) | (archived) |
| 14 | Docker Compose auto-migration + seed fix | SHIPPED | (archived) | (archived) |
| 15 | E2E test fixes (also fixed a real `quote.code` 500) | SHIPPED | (archived) | (archived) |
| 16 | Model/migration drift sweep (2 missing tables found) | SHIPPED | (archived) | (archived) |
| 17 | Mount notifications router | SHIPPED | (archived) | (archived) |
| 18 | Security hardening — secrets, rate limiting, GST on invoices | SHIPPED | (archived) | (archived) |
| 19 | Backup/restore/ops scripts | SHIPPED | (archived) | (archived) |
| 20 | Production config templates | SHIPPED | (archived) | (archived) |
| 21 | Handover documentation package | SHIPPED | (archived) | (archived) |
| 22 | Critical RBAC and auth gaps | SHIPPED | (archived) | (archived) |
| 23 | Correctness bugs — Decimal money, optimistic locking, soft delete | SHIPPED | (archived) | (archived) |
| 24 | Dead code + missing UI wiring | SHIPPED | (archived) | (archived) |
| 25 | Docs truth pass (done inline by orchestrator, no task file) | SHIPPED | — | — |
| 26 | Root handoff extraction + doc cleanup (142 handoffs swept) | SHIPPED | (archived) | (archived) |
| 27 | Security findings + lint sweep | SHIPPED | (archived) | (archived) |
| 28 | Doc consolidation (archived root handoffs, KIMI→CLAUDE symlink) | SHIPPED | (archived) | (archived) |
| 29 | Stale claim fixes (9 docs corrected to real repo state) | SHIPPED | (archived) | (archived) |
| 30 | Final release + submission package — cut **v1.0.0** | SHIPPED | (archived) | (archived) |
| 31 | Deferred features — MinIO storage + Celery worker — cut **v1.0.1** | SHIPPED | (archived) | (archived) |

## How this archive was built

Generated wave-39 from `plan/EXECUTION.md` status table + per-wave brief/report folders.
Every wave 1-31 is SHIPPED and appears here; every wave appears in exactly one of
`work/ARCHIVE.md` (1-31) or `work/ACTIVE.md` (32-39).

**Note:** The per-wave folders (`work/wave-N/` and `work/reports/wave-N/` for N=1..31)
were removed during the wave-39 repository reorganization to reduce clutter. The
historical record is preserved in this table and in git history.

## Seal-session archive moves (2026-09-22)
- work/reports/dispatch-24h/* → attic/dispatch-24h/ (49 NOISE files)
- work/FINAL-CLOSE/* → attic/final-close/ (ANTI-FAB also at docs/historical/)
- plan/ARCHITECTURE.md → merged into docs/ARCHITECTURE.md §8 → docs/historical/ARCHITECTURE-plan.md
- VALIDATION_REPORT.md, work/STATE.md, ASSIGN-* → docs/historical/
