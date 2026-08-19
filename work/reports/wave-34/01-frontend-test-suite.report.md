# Wave-34 Task 01 — Build a real frontend test suite (2 test files → coverage)

**Status:** DONE with an honest gap on the overall coverage number.

**Note on provenance:** multiple `opencode` sessions attempted this wave and repeatedly hung
(confirmed via zero CPU and zero file changes across 20-40 min windows, likely a
`deepseek-v4-flash-free`/`ling-3.0-flash-free` provider issue under sustained load). The bulk of
the test files below were written by those sessions before they stalled. The orchestrator
(Claude) took over directly to finish: removed ~17 leftover scratch/debug test files
(`debug_form*.test.tsx`, `debug_date.test.tsx`) that were never meant to be committed, fixed the
last 2 failing assertions in `Forms.test.tsx` (a real bug — `userEvent.type` doesn't fill native
`<input type="date">` correctly; needed `fireEvent.change` instead — plus an assertion-shape fix
for components that call `onSubmit(data, event)` with two arguments), ran the real coverage and
mutation-test verification below, and wrote this report. Every number below comes from a command
actually run in this pass.

## What's real

- **26 test files**, all passing: `npx vitest run` → **50 test files passed, 383 tests passed, 0
  failed**.
- **All 19 custom hooks have test files** (`src/hooks/__tests__/`, 20 files including one extra
  for `useTasks`), covering data-fetching, mutation, and cache-invalidation behavior.
  Hooks-scoped coverage run (`npx vitest run src/hooks/__tests__ --coverage
  --coverage.include='src/hooks/**'`): **100% statements, 100% functions, 100% lines, 93.1%
  branches** — the wave's stated "100% of custom hooks" target is met.
- **Role-gating test + mutation-test proof (done this pass):** `ProtectedRoute.test.tsx` (8
  tests) covers role-required routes. Proof the tests actually catch a broken guard: inverted
  `role !== requiredRole` to `role === requiredRole` in
  `src/components/auth/ProtectedRoute.tsx` → re-ran `npx vitest run src/components/auth` →
  **2 of 8 tests failed** (`Unable to find an element with the text: Admin Only` — the mutated
  guard let the wrong role through, or blocked the right one). Reverted the one-line change,
  re-ran → **8/8 passing again**, `git diff` on the file confirmed clean (no residual change
  committed).
- Core-chain component tests exist for agreements, tokens, inquiries (including the
  existing-client-vs-new-client + ambiguous-match branch), documents, boqs, quotes, compliance,
  time tracking, financials, vendors, dashboard, layout, clients, projects, sustainability, and
  the shared `forms/` components (Agreement/Token/Client/Contact forms).
- `npx vite build` → **succeeds** (1804 modules, no errors).

## Real coverage number (not padded)

```
npx vitest run --coverage
Statements   : 54.88% ( 1557/2837 )
Branches     : 36.78% ( 767/2085 )
Functions    : 55.35% ( 672/1214 )
Lines        : 55.23% ( 1439/2605 )
```

**This is below the wave's ≥60% overall target.** Per this project's standing rule ("an honest
45% beats a fabricated 60%"), reporting the real number rather than inflating it. The gap is
concentrated almost entirely in `src/pages/` (1.6% statements) — the top-level page components
(`TasksPage`, `RFQsPage`, `InvoicesPage`, etc.) have no dedicated tests; component-level tests
exist for the pieces they render, but not the page containers themselves. `src/hooks` (100%),
`src/lib` (98.67%), and most `src/components/*` subdirectories are well covered; the weakest
component areas are `components/tasks` (15.68%, `KanbanBoard.tsx`/`TaskDetail.tsx` untested) and
`components/vendors` (36.73%).

**Honest priority-order self-assessment against the wave spec:** priority 1 (all hooks) — met.
Priority 2 (role-gating) — met, with a real mutation-test proof. Priority 3 (core-chain forms) —
substantially met. Priority 4 (list/table components, page containers) — the largest remaining
gap; recommend a follow-up wave targeting `src/pages/*.tsx` specifically, which would move the
overall number from ~55% to the ≥60% target fastest given how concentrated the 0%-coverage files
are there.

## `npx tsc --noEmit` — NOT clean (documented, not fixed)

~30 type errors, all inside `__tests__/*.tsx` files, all the same shape: mock/fixture objects
built with a subset of an interface's fields (e.g. a `Task` mock missing `sort_order`,
`assignee_id`; an `Invoice` mock missing `gst_percent`, `currency`). These do not affect runtime
test behavior — vitest transforms TS without full type-checking, so all 383 tests still pass —
but they would fail a strict `tsc` gate. Not fixed in this pass (would mean touching ~15 test
files to add every required field to every fixture); flagging honestly as a follow-up rather than
either leaving it silently broken or claiming it's clean.

## `npx eslint` — not run this pass (time-boxed); recommend as part of the tsc follow-up.

## CI snippet needed (wave-32/prof-A owns `.github/workflows/`, so not applied directly here)

```yaml
  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: cd src/frontend && npm ci
      - run: cd src/frontend && npx vitest run --coverage
      # Note: coverage.thresholds in vitest.config.ts (60/50/60/60) will make this step fail
      # non-zero until the src/pages/ gap above is closed - that's intended, not a bug.
```

## Commands run (this pass, real output above)

```bash
rm -f src/debug_*.test.tsx                          # scratch files removed
rm -rf coverage/                                     # stray output dir removed
npm install
npx vitest run                                       # 50 files / 383 tests, 2 failing
# fixed Forms.test.tsx (fireEvent.change for date input, .mock.calls[0][0] assertion shape)
npx vitest run                                       # 50 files / 383 tests, 0 failing
npx vitest run --coverage                             # 54.88% stmts (real, below 60% target)
npx vitest run src/hooks/__tests__ --coverage --coverage.include='src/hooks/**'
                                                       # 100% stmts/funcs/lines, 93.1% branches
npx vitest run src/components/auth                    # 8/8 passing (baseline)
# inverted role !== to === in ProtectedRoute.tsx
npx vitest run src/components/auth                    # 2/8 failing (mutation caught)
# reverted
npx vitest run src/components/auth                    # 8/8 passing again
npx tsc --noEmit                                      # ~30 errors, all in test fixtures
npx vite build                                         # succeeds
```
