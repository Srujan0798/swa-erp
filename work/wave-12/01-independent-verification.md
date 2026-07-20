# Task 01 — Independent verification (tests, typecheck, Docker, E2E)

## What to do
Every "N/N tests passing" claim in this repo's commit messages and handoff docs is
developer-self-reported, not independently confirmed. wave-15's own deploy attempt was
BLOCKED because Docker wasn't available (`work/reports/wave-15/`), so integration/E2E status is
genuinely unverified. Your job is to actually run everything and report ground truth — fix
what's broken, but do not paper over failures with skipped tests or loosened assertions.

## Files to create
- CREATE: `work/reports/wave-12/01-independent-verification.report.md` (the main deliverable)
- CREATE (only if gaps found): fix commits as needed in whatever files are actually broken

## Files you may modify (only to fix genuine failures, not to hide them)
- Any file under `src/backend/` or `src/frontend/src/` if a real bug is found
- `tests/` if a test itself is wrong (not if the test is correctly catching a real bug —
  fix the code in that case, not the test)

## Files you must NOT touch
- `.github/workflows/*.yml` — do not modify CI config to make it "pass"; report the discrepancy instead
- `tests/conftest.py` — flagged do-not-touch in FINAL_SPEC.md §1

## The core problem (inline)
Run, in order, and record actual pass/fail counts (not what a commit message claims):
1. `python3 -m pytest tests/ -q` — full backend suite. Compare against the self-reported
   "97/97" (wave-3), "109/109" (wave-4), "42/42" (wave-7), "26/26" (wave-8) claims. Flag any
   discrepancy.
2. `cd src/frontend && npm run typecheck` (or `tsc --noEmit`) — full frontend, zero errors expected.
3. `cd src/frontend && npm run lint`
4. `docker compose up -d` (or `make dev`) — confirm the full stack (Postgres, Redis, backend,
   frontend) actually boots. This is the step wave-15 never completed. If Docker genuinely isn't
   available in this environment, say so explicitly in the report — don't fake success.
5. If Docker boots successfully: run whatever Playwright E2E config exists
   (`playwright.config.ts`) — `npx playwright test`. Report pass/fail per spec file.
6. Hit a handful of real API endpoints against the running stack (health check, login, one CRUD
   round-trip per major domain) to confirm the app is actually usable end-to-end, not just
   unit-test-green.

## Acceptance criteria
- [ ] Report states actual (not claimed) pass/fail counts for every step above
- [ ] Any discrepancy between self-reported and actual results is called out explicitly
- [ ] Docker boot status is definitively resolved (works / doesn't work / environment
      limitation) — no more "blocked, unclear" left hanging
- [ ] Any bugs found are either fixed (with a note in the report) or filed as a clear punch-list
      item with file:line

## How to deliver
1. Run all six steps above in this exact order
2. Fix genuine bugs found along the way
3. Write the full report — this report IS the deliverable, be thorough and honest, especially
   about anything that does NOT pass
4. Stop

## Constraints
- Time budget: 120 min
- Do not modify CI workflow files to force green
- Do not delete or skip failing tests to "pass" — fix the underlying issue or report it as a gap
- Allowed tools: pytest, npm, docker, playwright, file edit, curl
