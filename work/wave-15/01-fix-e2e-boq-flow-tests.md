# Task 01 — Fix failing E2E BOQ/quote flow tests

## What to do
`tests/e2e/test_boq_quote_flow.spec.ts` has 2 failing tests (confirmed by independent
verification, `work/reports/wave-12/01-independent-verification.report.md`: "5/7 pass... 0/2 pass
[BOQ flow] because the projects list table row doesn't have a button matching
`/view|open|details/` selector"). This is a test/UI mismatch, not a backend bug — the backend API
for projects/BOQs is confirmed working (verified via live curl smoke test in the same report).
Fix the test selectors to match the real UI, or fix the UI if it's genuinely missing an
accessible affordance — investigate first, don't guess.

## Files to investigate
- `tests/e2e/test_boq_quote_flow.spec.ts` — the failing test file
- `src/frontend/src/pages/ProjectsPage.tsx` — likely where the row-click/view mechanism actually
  lives (report suspects "a link wrapping the whole row, or a MoreHorizontal icon button" instead
  of a `/view|open|details/`-labeled button)

## Files you may modify
- `tests/e2e/test_boq_quote_flow.spec.ts` — update selectors to match real UI, IF the UI's
  current interaction pattern is reasonable (e.g. a row click, or an icon button with an
  aria-label) — prefer fixing the test to match good UI over changing working UI to match a
  guessed test
- `src/frontend/src/pages/ProjectsPage.tsx` — ONLY if you determine there's a genuine
  accessibility gap (e.g. a row-click with no keyboard/screen-reader affordance at all) — in that
  case add a proper `aria-label="View project"` button rather than reworking navigation

## Files you must NOT touch
- Backend files — the report confirms the backend is fine, this is UI/test only
- Other E2E spec files (`test_login_flow.spec.ts`, `test_dashboard.spec.ts`) — those already pass, don't touch them

## The core problem (inline)
Run `npx playwright test tests/e2e/test_boq_quote_flow.spec.ts --project=chromium --debug` (or
use `--ui` mode) to see exactly what selector is failing and what's actually rendered on
`ProjectsPage.tsx` at that point. Compare against what the test expects
(`/view|open|details/i` text match, per the wave-12 report). Determine the real interaction
pattern, then either:
- Update the test's selector to match it (most likely fix — e.g. target the row's actual link/
  icon-button by a stable selector like `data-testid` or `aria-label` instead of guessed text)
- If there's truly no accessible way to reach project detail from the list (unlikely, but
  check), add one

## Acceptance criteria
- [ ] `npx playwright test tests/e2e/ --project=chromium` — all 7 tests pass (up from 5/7)
- [ ] No regression in the 2 currently-passing spec files
- [ ] If a `data-testid` or `aria-label` was added to make the row reliably selectable, it
  doesn't change the visible UI/behavior for real users

## How to deliver
1. Investigate with Playwright debug/UI mode against a running dev stack (`make dev` or the
   docker-compose stack from wave-12/wave-14)
2. Fix the test (preferred) or the UI (only if genuinely warranted)
3. Run the full E2E suite to confirm 7/7
4. Write report to `work/reports/wave-15/01-fix-e2e-boq-flow-tests.report.md`
5. Stop

## Constraints
- Time budget: 45 min
- Prefer fixing the test over changing working UI — only touch the UI if there's a real gap
- Allowed tools: file edit, playwright, browser, npm
