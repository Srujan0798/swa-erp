# Wave-34 Task 01 — Build a real frontend test suite (2 test files → ≥60% coverage)

**Depends on wave-32.** Can run in parallel with 33 and 35 (different files, no collision).

## The problem (measured)

- **128 frontend source files** (`.ts`/`.tsx` under `src/frontend/src`)
- **2 test files total**: `hooks/__tests__/useTasks.test.ts`, `hooks/__tests__/useInquiries.test.ts`

The React application — the entire surface the client's staff actually touch — is effectively
untested. Vitest + React Testing Library are already configured (the 2 files prove the harness
works); nobody built on it.

For an industry submission this is the most visible engineering gap in the repo: a reviewer
sees a large frontend with no tests and reasonably concludes the UI was never verified.

## Target
- **≥60% statement coverage** on `src/frontend/src`
- **100% of custom hooks** (`src/frontend/src/hooks/`) — they hold the data-fetching and
  cache logic, highest bug-density per line
- Critical user-facing components tested: the core-chain screens (Inquiries, Agreements, Tokens,
  Document References), plus auth/role-gating behaviour

## Files to modify
- `src/frontend/src/**/__tests__/` — new test files colocated with what they test
- `src/frontend/package.json` — add `test:coverage` script if absent
- `src/frontend/vitest.config.*` — coverage thresholds
- Component/hook source **only** where a test reveals a genuine bug

## Files you must NOT touch
- Backend anything
- The 2 existing test files (follow their established patterns instead)
- Playwright E2E specs (`tests/e2e/`) — different layer, not this wave

## How to do this properly

**Load the `frontend-design` skill** for component-quality context, and follow the patterns
already established in `useTasks.test.ts` / `useInquiries.test.ts` rather than inventing a new
convention.

Priority order (highest value first):
1. **All hooks** (`hooks/*.ts`) — mock the API layer, assert query keys, loading/error/success
   states, and cache invalidation on mutations. This is where TanStack Query bugs hide.
2. **Role-gating behaviour** — this project had a real, confirmed class of bug where the UI
   showed actions the backend would 403 (found in the 2026-07-21 audit). Test that
   viewer/designer/PM/admin each see the correct controls. **This is the highest-value frontend
   testing in the repo** — it maps to a defect class that actually occurred.
3. **Core-chain forms**: validation, submit, error rendering (Inquiry convert flow especially —
   it has the existing-client-vs-new-client branch and an ambiguous-match path).
4. **List/table components**: empty state, loading state, pagination, filters.

**Test user-visible behaviour, not implementation.** Query by role/label/text as RTL intends —
don't assert on internal state or CSS classes; those tests break on refactor and prove nothing.

## Acceptance criteria
- [ ] `npm run test:coverage` (in `src/frontend`) → **≥60% statements**, threshold enforced in
      config so it can't regress
- [ ] **Every** file in `hooks/` has a test file
- [ ] Role-gating tests exist and genuinely fail if a role check is removed — **prove this**:
      temporarily break one gate, show the test catches it, revert, paste the evidence
- [ ] `npx tsc --noEmit` and `npx eslint . --ext ts,tsx --max-warnings 0` clean
- [ ] `npx vite build` succeeds
- [ ] Frontend test run added to CI (wave-32 made CI real — this must gate too)

## Deliver
Report → `work/reports/wave-34/01-frontend-test-suite.report.md`. Include before/after coverage,
the list of hooks covered, the role-gating mutation-test evidence, and any bugs found. Commit
before writing.

## Constraints
- Time budget: 180 min
- Prefer fewer meaningful tests over many shallow ones
- If 60% isn't reachable in budget, get the hooks + role-gating done completely and report the
  real number honestly rather than padding with trivial render tests
- Allowed: file edit, git, npm, vitest
