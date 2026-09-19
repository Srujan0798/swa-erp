# Wave-34 Task 02 — Close the frontend page-coverage gap (55% → ≥60%)

**Depends on wave-34 task 01 having landed** (it has — check `work/reports/wave-34/01-frontend-test-suite.report.md`).
That wave got all 19 hooks to 100% and most components tested, but left `src/pages/*.tsx`
almost entirely untested (1.6% statements), which is the only reason overall coverage (54.88%)
misses the 60% target.

## Current real baseline (verified 2026-08-19)

```
cd src/frontend && npx vitest run --coverage
Statements   : 54.88% ( 1557/2837 )
Branches     : 36.78% ( 767/2085 )
Functions    : 55.35% ( 672/1214 )
Lines        : 55.23% ( 1439/2605 )
```

`src/pages/` is at 1.6% statements — every page component listed at 0% except 3 trivial re-export
stubs already at 100/0. This is the single highest-leverage place to add tests: the components
these pages render are already well-tested (per wave-34 task 01), so page tests mostly need to
verify the page renders, wires up the right hooks/routes, and handles loading/error states —
integration-level tests, not re-testing component internals.

## Files to test (priority order — biggest 0%-coverage files first)
- `src/pages/RFQsPage.tsx` (667 lines, 0%)
- `src/pages/TasksPage.tsx` (390 lines, 0%)
- `src/pages/InvoicesPage.tsx` (343 lines, 0%)
- `src/pages/ProjectDetailPage.tsx` (327 lines, 0%)
- `src/pages/InquiriesPage.tsx` (265 lines, 0%)
- `src/pages/TokensPage.tsx` (184 lines, 0%)
- `src/pages/MaterialsPage.tsx` (174 lines, 0%)
- `src/pages/ReportsPage.tsx` (198 lines, 0%)
- `src/pages/UsersPage.tsx` (193 lines, 0%)
- `src/pages/TimeTrackingPage.tsx` (242 lines, 0%)
- Remaining pages at 0% (client/vendor/agreement/compliance/dashboard/sustainability detail
  pages) as budget allows

Also worth closing while in this area (not pages, but same-shaped low-coverage gaps):
- `src/components/tasks/KanbanBoard.tsx` (0%), `src/components/tasks/TaskDetail.tsx` (0%)
- `src/components/vendors/VendorDetail.tsx`, `VendorForm.tsx`, `ContactForm.tsx` (all 0%)
- `src/components/quotes/QuoteBuilder.tsx`, `QuoteDetail.tsx` (0%)

## How to test a page efficiently
Follow the pattern in `src/frontend/src/components/*/__tests__/` from wave-34 task 01. For each
page: render with the query client + router wrapper already used elsewhere, mock the API layer
the page's hooks call, assert loading state → data state → key content renders, and one error
state. Don't chase 100% per page — a page going from 0%→60% is worth more than one going from
60%→100% while others stay at 0%. Spread effort across files rather than perfecting one.

## Also fix (found during verification, not yet fixed)
`npx tsc --noEmit` has ~30 errors, all in `__tests__/*.tsx` files from wave-34 task 01 — mock
fixture objects missing required interface fields (e.g. a `Task` mock missing `sort_order`,
an `Invoice` mock missing `gst_percent`). Runtime tests pass regardless (vitest doesn't
type-check), but a strict `tsc` gate would fail. Fix these — add the missing fields to each
fixture — while you're in these files anyway. List: run `npx tsc --noEmit` yourself for the
current exact list, don't trust this description as exhaustive.

## Acceptance criteria
- [ ] `npx vitest run --coverage` → **≥60% statements** (the configured threshold in
      `vitest.config.ts` — 60/50/60/60 — should pass without lowering it)
- [ ] `npx tsc --noEmit` clean (fix the pre-existing fixture-type errors too)
- [ ] `npx eslint . --ext ts,tsx --max-warnings 0` clean
- [ ] `npx vite build` succeeds
- [ ] All new tests actually assert real behavior (rendered content, not just "doesn't crash")

## Deliver
Report → `work/reports/wave-34/02-frontend-page-coverage.report.md` with real before/after
coverage numbers. Commit before writing the report — and commit incrementally as you finish each
page, not all at once.

## Constraints
- Time budget: 150 min
- Do not lower the coverage thresholds in `vitest.config.ts` to make the gate pass
- Allowed: file edit, git, npm, vitest
