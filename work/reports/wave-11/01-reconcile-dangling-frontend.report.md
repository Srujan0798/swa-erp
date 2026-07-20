# Report — Wave 11 · 01 Finish, verify, and commit dangling frontend work

## Result
DONE

## What I did (investigation + finishing)

**Investigated each dangling file, then fixed/verified:**

- `src/frontend/src/pages/TasksPage.tsx` — removed unused imports (`taskKeys`, `Task`, `TaskComment`), removed unused `STATUS_OPTIONS` / `PRIORITY_OPTIONS` / `STATUS_TRANSITIONS` consts, and changed `<KanbanBoard loading=...>` → `isLoading={...}` plus added the required `onTaskClick` handler.
- `src/frontend/src/components/tasks/TaskDetail.tsx` — removed unused `_STATUS_OPTIONS` const.
- `src/frontend/src/components/boqs/BOQVersionList.tsx` — fixed `useDeleteBoq` call to pass the boq id string (was passing `{id, projectId}`), and switched `parsed_by_name` → `parsed_by` (the field the `BOQListRead` type + backend actually expose).
- `src/frontend/src/components/compliance/ComplianceChecklist.tsx` — removed unused `ComplianceStatus` import.
- `src/frontend/src/components/financials/PnlDashboard.tsx` — reviewed for GST. `PnlDashboard` is a P&L summary (revenue/cost/profit), not an invoice display, so the GST breakdown belongs on the invoice UI. Added a **GST (tax) line** to the invoice detail dialog in `InvoicesPage.tsx` (Subtotal / GST / Total) — the ERP already tracks `gst_number` on clients and `tax_amount` on invoices, so this surfaces the GST breakdown in the invoice UI.
- `src/frontend/src/components/quotes/QuoteDetail.tsx`, `src/frontend/src/pages/NewVendorPage.tsx` — reviewed; compile cleanly, no changes required beyond what typecheck/lint demanded.

**Wiring of the 5 orphaned pages** (untracked, never committed, not in routing/nav):
- `InvoicesPage`, `MaterialsPage`, `RFQsPage`, `ReportsPage`, `TimeTrackingPage` — added routes in `App.tsx` (`/invoices`, `/materials`, `/rfqs`, `/reports`, `/time-tracking`; `TimeTrackingPage` uses a default export) and nav items in `Sidebar.tsx` (Receipt / Package / Send / BarChart3 / Clock icons). All 5 are reachable from the sidebar.

**Duplicate types:** `src/frontend/src/types/index.ts` was an abandoned, full duplicate of `types/api.ts`. Confirmed **nothing imports it** (no `@/types/index` or bare `@/types` imports anywhere), so it was deleted — eliminating the duplicate source of truth.

**Verification:** `npm run typecheck` → 0 errors; `npm run lint` → clean; `npx vite build` → succeeds (1783 modules). Backend was not touched (out of scope).

## Acceptance checks
- [x] `npm run typecheck` clean (zero errors) across the whole frontend — **passed** (12 errors → 0).
- [x] `npm run lint` clean — **passed** (idempotent; `--max-warnings 0`).
- [x] Every one of the 5 new pages reachable via sidebar nav in a running app — **wired** (routes + nav added, production build succeeds). Not clicked through a live browser in this environment, but routing/nav are in place and the build validates all imports resolve.
- [x] No duplicate type definitions between `types/index.ts` and `types/api.ts` — **resolved** by deleting the unreferenced `types/index.ts`.
- [x] `git status --short src/frontend/` clean after commit — **passed** (committed as `4e0655d`).

## Decisions I made
- Located GST display on the invoice detail UI (`InvoicesPage`) rather than `PnlDashboard`, because `PnlDashboard` is a P&L aggregate with no per-invoice data; the invoice UI is where a GST line item belongs (client already carries `gst_number`, invoices carry `tax_amount`).
- Deleted `types/index.ts` outright (rather than merging specific types into `api.ts`) because it was entirely unreferenced — keeping two files would risk future drift.
- The Wave-10 sustainability frontend files (`SustainabilityPage`, `components/sustainability/`, `useSustainability.ts`, and the shared `App.tsx`/`Sidebar.tsx`/`api.ts`/`types/api.ts`/`ProjectDetailPage.tsx` edits) were committed together with the Wave-11 work so that `src/frontend/` ends fully clean; the Wave-10 backend + tests were committed separately (`a155000`).

## Commits
- `a155000` feat(wave-10): add sustainability metrics API and frontend
- `4e0655d` feat(wave-11): finish and commit dangling frontend work

## Tests run
- `npx tsc --noEmit` → 0 errors
- `npm run lint` → clean
- `npx vite build` → built successfully
- (Backend `pytest tests/wave-10/` also re-run → 5 passed, confirming no regression.)

## Issues / blockers
- **Left intentionally uncommitted (out of scope / not mine):** pre-existing unrelated working-tree changes — `src/backend/models/client.py`, `uploads/` deletions, `HANDOFF.md`, `plan/EXECUTION.md`. These were not part of the Wave 11 dangling list and were not touched; they remain uncommitted.
- No abandoned/broken files were found that required flagging; all 5 orphaned pages were complete and compilable once wired.

## Recommended next task
None. Wave 11 closes the dangling-frontend gap; `src/frontend/` is now typecheck-clean, lint-clean, fully routed, and committed.

## Time / tokens / model
~75 min / hy3-free
