# Task 01 — Finish, verify, and commit dangling frontend work

## What to do
The working tree has real in-progress frontend work that was never committed. Investigate each
file, finish/fix it if incomplete, verify it builds and works, then commit. Do NOT assume these
are safe to commit as-is — some may be half-finished (FINAL_SPEC.md §3 flagged "TypeScript
errors to fix" as still outstanding at the time these were left uncommitted).

## Files to investigate and finish

**Modified (already tracked, uncommitted changes):**
- `src/frontend/src/components/financials/PnlDashboard.tsx`
- `src/frontend/src/components/quotes/QuoteDetail.tsx`
- `src/frontend/src/components/tasks/KanbanBoard.tsx`
- `src/frontend/src/components/tasks/TaskDetail.tsx`
- `src/frontend/src/lib/api.ts`
- `src/frontend/src/pages/NewVendorPage.tsx`
- `src/frontend/src/pages/TasksPage.tsx`
- `src/frontend/src/types/api.ts`

**Untracked (never committed at all):**
- `src/frontend/src/components/ui/separator.tsx`
- `src/frontend/src/hooks/useToast.ts`
- `src/frontend/src/pages/InvoicesPage.tsx`
- `src/frontend/src/pages/MaterialsPage.tsx`
- `src/frontend/src/pages/RFQsPage.tsx`
- `src/frontend/src/pages/ReportsPage.tsx`
- `src/frontend/src/pages/TimeTrackingPage.tsx`
- `src/frontend/src/types/index.ts`

(Run `git status --short src/frontend/` first — this list may be stale by the time you start;
trust the live output over this list.)

## Files you must NOT touch
- `src/backend/` (backend is not part of this task)
- Anything under `work/wave-9/`, `work/wave-10/` scope (new chain modules — separate waves)

## The core problem (inline)
This is investigation + finishing work, not net-new features:
1. For each untracked page (InvoicesPage, MaterialsPage, RFQsPage, ReportsPage,
   TimeTrackingPage): confirm it's wired into `App.tsx` routing and `Sidebar.tsx` nav. If not,
   wire it up (this matches FINAL_SPEC.md §3's flagged gap — "missing routes for tasks, quotes,
   BOQs, invoices, time, reports").
2. Run `tsc --noEmit` (or `npm run typecheck`) and fix every error surfaced in these files —
   FINAL_SPEC.md explicitly notes "Badge import, unused vars, type mismatches" as known issues.
3. Check `types/index.ts` vs `types/api.ts` for duplicate/conflicting type definitions — if
   `index.ts` is a superset or was an abandoned rename, consolidate into `api.ts` and delete the
   duplicate rather than keeping both (don't leave two competing sources of truth).
4. Verify `PnlDashboard.tsx` GST invoicing: check whether the invoice PDF/UI includes a GST
   breakdown (ADR-0002 item #8 — Client already has `gst_number`). If missing, add a GST line
   item to the invoice display.
5. Start `make dev`, click through Invoices, Materials, RFQs, Reports, Time Tracking, Tasks
   (Kanban + Detail), Quotes detail, Vendors new-vendor form — confirm no console errors, no
   broken renders.

## Acceptance criteria
- [ ] `npm run typecheck` clean (zero errors) across the whole frontend, not just these files
- [ ] `npm run lint` clean
- [ ] Every one of the 5 new pages reachable via sidebar nav in a running app
- [ ] No duplicate type definitions between `types/index.ts` and `types/api.ts`
- [ ] `git status --short src/frontend/` is clean after commit (nothing left dangling)

## How to deliver
1. Investigate, finish, fix typecheck/lint errors
2. Manually verify in browser (`make dev`)
3. `git add` the finished files and commit with a clear message describing what was completed
   (do not commit if typecheck/lint still fails)
4. Write report to `work/reports/wave-11/01-reconcile-dangling-frontend.report.md` — list what
   was already fine, what you fixed, and what (if anything) you deliberately left out and why
5. Stop

## Constraints
- Time budget: 90 min
- If a file turns out to be genuinely abandoned/broken beyond reasonable repair, say so in the
  report instead of forcing a bad commit — flag it, don't hide it
- Allowed tools: file edit, npm, browser, git (add/commit only, no push, no force)
