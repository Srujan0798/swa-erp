# Report — Task 01 — Fix failing E2E BOQ/quote flow tests

## Result
PARTIAL — the targeted selector bug is fixed and verified (5/7 → 6/7, up from the report's
baseline, with zero regressions). A second, unrelated, pre-existing **backend** bug was
uncovered one step further into the flow; fixing it requires touching backend files, which this
task explicitly forbids ("Files you must NOT touch: Backend files"). Flagging it as a follow-up
rather than fixing it out-of-scope.

## What I did
- Investigated `src/frontend/src/pages/ProjectsPage.tsx` → it just renders
  `src/frontend/src/components/projects/ProjectList.tsx`, which is where the row action actually
  lives.
- Root cause: `ProjectList.tsx` renders the row's "View" action as
  `<Button variant="ghost" asChild><Link to={...}>View</Link></Button>`. With shadcn's `asChild`,
  the DOM element that's actually rendered is the `<Link>` (an `<a>` tag) — its accessible role is
  **`link`**, not `button`. The test used `getByRole("button", { name: /view|open|details/i })`,
  which never matches. This is a reasonable, accessible UI pattern (visible text "View", proper
  `<a href>`, keyboard-operable) — not a UI defect — so I fixed the test instead of the UI, per the
  task's stated preference.
- Modified `tests/e2e/test_boq_quote_flow.spec.ts`: changed both occurrences of
  `projectRow.getByRole("button", { name: /view|open|details/i })` to
  `projectRow.getByRole("link", { name: /view|open|details/i })`.
- While driving the flow further (BOQ tab → upload → Quotes tab → quote row), found a second,
  genuine accessibility gap in `src/frontend/src/components/quotes/QuoteList.tsx`: the quote row's
  "view" action is an icon-only `<Button variant="ghost" size="icon">` wrapping only a Lucide
  `<Eye>` svg, with **no accessible name at all** (no text, no `aria-label`). This is exactly the
  case the task brief called out as the "add a proper aria-label" exception — a real
  screen-reader-unfriendly control, not a guessed selector. Added `aria-label="View quote"` to
  that button. This does not change any visible UI/behavior for sighted users (icon and click
  handler unchanged), it only supplies an accessible name so `getByRole("button", { name:
  /view|details/i })` (used in the "quote approval workflow" test) and real assistive tech both
  resolve it.
- (An unrelated hunk in the same spec file — the BOQ-upload payload shape (`{items:[...]}` →
  bare `[...]`) — was already present/changed in the working tree before I started per the
  system's note that it was an intentional external edit; I left it as-is and it is required for
  the upload step to succeed against the real API.)

## Acceptance checks
- [x] `npx playwright test tests/e2e/ --project=chromium` (with `--workers=1`, see note below) —
      **6/7 pass**, up from the 5/7 baseline in the wave-12 report — passed (evidence: full run
      below)
- [x] No regression in the 2 currently-passing spec files — `test_login_flow.spec.ts` (4/4) and
      `test_dashboard.spec.ts` (1/1) still pass — passed
- [x] The only change to visible UI/behavior was adding `aria-label="View quote"` to an
      already-existing icon button in `QuoteList.tsx` — no visual or behavioral change for real
      users — passed
- [ ] Full 7/7 — **not reached**. The 2nd `test_boq_quote_flow.spec.ts` test ("quote approval
      workflow") now passes (it degrades gracefully when no quote exists yet). The 1st test
      ("admin can upload BOQ and generate quote") still fails, but **not** on the selector issue
      this task targets — it fails one step later, on `POST /api/quotes` itself, which 500s. See
      "Issues / blockers".

### Full run (sequential, `--workers=1`)
```
Running 7 tests using 1 worker
✓ test_boq_quote_flow.spec.ts:39 quote approval workflow
✓ test_dashboard.spec.ts:3 dashboard shows stats for admin
✓ test_login_flow.spec.ts:3 admin can log in and reach dashboard
✓ test_login_flow.spec.ts:12 invalid credentials show error
✓ test_login_flow.spec.ts:20 non-admin gets blocked from /users
✓ test_login_flow.spec.ts:31 logout returns to login
✗ test_boq_quote_flow.spec.ts:12 admin can upload BOQ and generate quote
  (fails at: expect(page.getByText("Draft")).toBeVisible() — quote creation 500s server-side)
1 failed, 6 passed (36.7s)
```

Note on `--workers=1`: the default `fullyParallel` config (4 workers) against this sandbox's
freshly-(re)started Docker stack produced additional, non-deterministic failures in
`test_login_flow` and `test_dashboard` (login redirect timing out under worker contention) that
disappeared entirely when run sequentially. This reads as sandbox resource contention on a cold
backend, not a real regression — those two spec files are explicitly out of scope and their
underlying app code was never touched. Recommend the orchestrator re-verify with `--workers=1` or
against a warmed-up stack if the default parallel run looks flaky.

## Decisions I made
- Fixed the test's role selector (`button` → `link`) rather than changing `ProjectList.tsx`,
  because `Button asChild` wrapping a `Link` with visible "View" text is a standard, accessible
  shadcn pattern — changing it would be UI churn to satisfy a guessed test selector, which the
  task explicitly said to avoid.
- Added `aria-label="View quote"` to the icon-only quote-row button in `QuoteList.tsx` even though
  it wasn't in the task's original "files you may modify" list (which named `ProjectsPage.tsx`
  specifically, based on the brief's guess about where the bug lived). The actual row-action code
  lives in `ProjectList.tsx`/`QuoteList.tsx`, not `ProjectsPage.tsx` itself; I judged this within
  the spirit and letter of "the UI, ONLY if you determine there's a genuine accessibility gap ...
  add a proper aria-label" since this button had zero accessible name, and it's on the exact path
  this task is verifying. Did not touch anything else in that file or component.
- Did **not** fix the `Quote.code` AttributeError in `src/backend/services/quote_service.py` even
  though it now blocks 7/7, because it is squarely a backend file and the task says "Files you
  must NOT touch: Backend files ... this is UI/test only." Filed as a blocker/follow-up instead.

## Tests run
- `npx playwright test tests/e2e/ --project=chromium` (default, 4 workers) → flaky (2–5 failures,
  varying — see note above)
- `npx playwright test tests/e2e/ --project=chromium --workers=1` → stable, **6 passed, 1 failed**
  (run twice, same result both times)
- Manual repro via `curl` + `docker logs swa-erp-backend-1` to confirm the remaining failure's
  root cause server-side (see below)

## Issues / blockers
**New, pre-existing backend bug found (not the bug this task targets, and out of scope to fix
here):**

`src/backend/services/quote_service.py:58` reads `quote.code` when serializing a newly created
quote, but the `Quote` model (`src/backend/models/quote.py`) has no `code` column/attribute
(fields present: `id`, `project_id`, `boq_id`, `version_number`, `status`, `subtotal`,
`markup_percent`, `markup_amount`, `tax_percent`, `tax_amount`, `total_amount`, `terms`,
`validity_days`, `valid_until`, `created_by`, `approved_by`, `approved_at`, `sent_at`,
`client_response`, `client_response_at`, ...). Every `POST /api/projects/{id}/quotes` call
therefore raises `AttributeError: 'Quote' object has no attribute 'code'` and the endpoint 500s.
This is why the UI shows "Failed to create quote." and the test's final
`expect(page.getByText("Draft")).toBeVisible()` never resolves. Confirmed via
`docker logs swa-erp-backend-1` traceback and by inspecting the model directly — this is 100%
reproducible, not test-data flakiness.

This fully explains the wave-12 report's earlier claim that "the backend is confirmed working via
curl smoke test" not catching it: that smoke test never exercised `POST /api/quotes`
end-to-end (its endpoint list stops at `GET .../quotes` type read paths — see
`work/reports/wave-12/01-independent-verification.report.md`, "Live API smoke" table, items 1–21;
none of them create a quote).

**Environment setup performed for this task** (may be useful context for whoever picks up the
backend fix or re-runs this later):
- Stack was already partially up under `docker-compose` in this sandbox when I started, but the
  Postgres database had 0 users. Reseeded via
  `docker exec -e DATABASE_URL="postgresql://swa:swa@postgres:5432/swa_erp" swa-erp-backend-1
  python scripts/seed_demo.py` (host's local Postgres on 5432 conflicts with the container's
  published port, so seeding from the host targets the wrong DB — the wave-12 report flagged the
  same issue).
- Rebuilt+redeployed the frontend image (`docker-compose build frontend && docker-compose up -d
  frontend`) after editing `QuoteList.tsx`, since the frontend is a static Vite build baked into
  the nginx image, not a live-reloading dev server.
- The Docker stack was unstable during this session (containers disappeared entirely between two
  of my runs, requiring `docker-compose up -d` + reseed again) — appears to be sandbox-level, not
  related to my changes.

## Recommended next task
File a follow-up backend task: fix `src/backend/services/quote_service.py:58` — either add a
`code` column to the `Quote` model (with an Alembic migration, per repo convention — e.g. a
human-readable quote reference like `SWA-{year}-QT-{n}`, matching the reference-ID pattern already
used for `inquiries`/`service_agreements`/`tokens`/`document_references` per the wave-12 report),
or remove the `"code": quote.code` line from the serialized response if no such field is actually
needed by the frontend/`QuoteBuilder.tsx` (worth checking `src/frontend/src/types/api.ts`'s
`Quote` type — if it doesn't declare `code`, deleting the line is the smaller fix). Once that's
fixed, re-run `npx playwright test tests/e2e/ --project=chromium --workers=1` to confirm 7/7.

## Time / tokens / model
~40 min / Claude Sonnet 5
