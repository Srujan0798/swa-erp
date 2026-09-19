# Wave-48 Task 05 — Missing loading states on 3 data-heavy pages + bundle code-splitting

Two independent, real findings from a live audit (many other pages checked and correctly ruled OUT as non-issues — thin wrappers delegating to components that already handle loading properly; see `work/reports/wave-48/05-*.report.md` for the ruled-out list once written).

## Verified findings

| # | Finding | Evidence |
|---|---|---|
| 9 | **3 substantial pages fetch data directly with zero loading-state UI.** `DashboardPage.tsx` (256 lines, **8 separate `useQuery` calls**), `ProjectDetailPage.tsx` (156 lines, 2 calls), `DocumentsPage.tsx` (101 lines, 2 calls) — none reference `isLoading`, `isPending`, `Skeleton`, `Spinner`, or use a `Suspense` boundary. `DashboardPage` is the first thing a user sees after login. | `grep -c "useQuery\|useMutation"` vs `grep -c "isLoading\|Skeleton\|Spinner"` on each file — 8/0, 2/0, 2/0 |
| 10 | **Frontend ships as a single 725KB JS bundle with zero code-splitting.** No route-based lazy loading — every page's code loads on first paint regardless of which page the user is on. | `ls -la src/frontend/dist/assets/*.js` → one 725567-byte file |

**Contrast, for calibration:** most other pages (`ClientsPage`, `ProjectsPage`, `VendorsPage`, `VendorDetailPage` — all thin wrappers) delegate to components (`ClientList.tsx` etc.) that correctly handle `isLoading`/`isError` via `useQuery`. This wave's scope is specifically the pages that do NOT follow that pattern.

## Files you own
- `src/frontend/src/pages/DashboardPage.tsx`
- `src/frontend/src/pages/ProjectDetailPage.tsx`
- `src/frontend/src/pages/DocumentsPage.tsx`
- `src/frontend/src/App.tsx` (route-level code-splitting only — do not restructure routing logic)
- `src/frontend/vite.config.ts` (if manual chunk config is needed)

## The work

### 1. Loading states for the 3 pages
Follow the pattern already established correctly elsewhere in this codebase (check `ClientList.tsx` for the reference pattern). For `DashboardPage`'s 8 queries specifically: don't block the whole page on all 8 resolving — show each dashboard card/section with its own loading skeleton so fast queries render immediately and slow ones don't hold up the rest. Add a visible error state for each query too (not just loading), matching whatever error-display convention the rest of the app uses.

### 2. Route-based code splitting
Convert the page-level route components in `App.tsx` to `React.lazy()` + a `Suspense` boundary with a loading fallback (which pairs naturally with wave-48 task 01's error boundary work, if that's landed — check first, don't duplicate). Verify the resulting build actually produces multiple chunk files, not just a slightly smaller single bundle.

## Acceptance criteria
- [ ] Each of the 3 pages shows a real loading indicator while its query is pending — verify by throttling network in a manual check or by asserting on loading UI in a test, paste evidence
- [ ] `npx vite build` output shows multiple JS chunks, not one — paste the file listing before/after with sizes
- [ ] Total initial-load JS for a typical page is meaningfully smaller than 725KB — paste the real number
- [ ] Full frontend suite still green

## Deliver
`work/reports/wave-48/05-frontend-loading-states-and-bundle-splitting.report.md`. Also record, in the same report, the pages that were checked and ruled out as already correct (ClientsPage, ProjectsPage, VendorsPage, VendorDetailPage) so this doesn't get re-audited later. Commit before writing it.

## Constraints
- Time budget: 90 min · commit per item (loading states, then code-splitting, separately)
- Do not add loading UI to pages that already handle it correctly via a child component
