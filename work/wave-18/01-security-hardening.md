# Task 01 — Production security hardening

## What to do
Close real, confirmed gaps found in a security sweep — this is not speculative, each item below
was verified against the actual code, not guessed.

## Files to modify
- MODIFY: `src/backend/core/config.py` — fail-fast validation on startup
- MODIFY: `src/backend/main.py` — add rate limiting middleware, tighten CORS for non-dev
- CREATE: `src/backend/core/rate_limit.py` (or wherever fits the existing `core/` module style)
- MODIFY: `src/backend/models/invoice.py`, `src/backend/schemas/invoice.py`,
  `src/backend/services/invoice_service.py` — add GST breakdown
- MODIFY: relevant invoice PDF/frontend rendering component to show the GST line
- CREATE: `tests/wave-18/test_security_hardening.py`, `tests/wave-18/test_invoice_gst.py`

## Files you must NOT touch
- Any file outside the ones listed above — this is a hardening pass, not a refactor
- `src/backend/models/client.py`, `src/backend/models/vendor.py` — their `gst_number` fields
  already exist and are correct, this task only adds GST to the *invoice*, not the parties

## The core problem (inline)

### 1. `SECRET_KEY` has no production fail-safe
`src/backend/core/config.py` line 10: `SECRET_KEY: str = "change-me"`. If `APP_ENV` is not
`"dev"` and `SECRET_KEY` is still the literal default `"change-me"`, the app must refuse to
start — raise at import/startup time, not silently run with a guessable JWT signing key. Add
this check in `Settings` (a `model_validator` or equivalent Pydantic v2 mechanism) or in
`main.py`'s startup path — whichever matches how `Settings` is already validated elsewhere in
this file.

### 2. No rate limiting anywhere
Zero rate limiting exists on any endpoint, including `/api/auth/login`. Add rate limiting scoped
initially to just the auth endpoints (login, refresh, any password-reset endpoint if one
exists) — a reasonable default is 5 attempts per minute per IP, returned as 429 with a
`Retry-After` header. Use a lightweight library appropriate for FastAPI (check what's already
in `requirements.txt` before adding a new dependency; `slowapi` is a common choice if nothing
suitable exists — flag it if you add a new dependency per the constraint below).

### 3. CORS is hardcoded to `localhost:3000` via `.env.example`, no prod guidance
`CORS_ORIGINS` in `.env.example` is `["http://localhost:3000"]`. This task doesn't need to know
the real prod hostname (that's still pending IT's answer) — just make sure `main.py`/`config.py`
reads `CORS_ORIGINS` from the environment correctly (verify it already does; if it's hardcoded
anywhere instead of reading `settings.CORS_ORIGINS`, fix that) so swapping the value later is a
one-line env change, not a code change.

### 4. Invoices don't break out GST at all
`src/backend/models/invoice.py` has no GST-related field. Client and Vendor both store a
`gst_number` (their registration number), but the invoice itself never calculates or displays a
GST amount — despite Meeting 2 flagging "GST invoicing required in wave-7" and the wave never
actually verifying this. Add:
- `gst_percent: Decimal` (default `Decimal("18")`, matching the tax_percent convention already
  used on `Quote` — check `models/quote.py`'s `tax_percent`/`tax_amount` fields and mirror that
  exact pattern for consistency)
- `gst_amount: Decimal` (computed: `subtotal * gst_percent / 100`, same rounding convention as
  Quote)
- Update `total_amount` calculation to include `gst_amount`
- Show the GST line on whatever renders the invoice (PDF export via WeasyPrint, and/or the
  frontend invoice detail view — check `InvoicesPage.tsx` / any invoice PDF template file for
  where subtotal/total currently render, add GST between them)
- Needs a new Alembic migration (`00NN_add_invoice_gst.py`) adding the two columns, nullable
  with sensible defaults so existing rows don't break

### Edge cases
- Existing invoices (created before this migration) should get a sensible default GST (e.g.
  computed from existing `subtotal`/`total_amount` if those already implicitly included tax, or
  just `gst_percent=18, gst_amount=0` if genuinely unknown — check with a `data migration` step
  in the same Alembic file if `total_amount` minus `subtotal` cleanly implies an existing rate;
  otherwise default to 0 and flag it in the report rather than guessing at historical data)
- Rate limiting must not block legitimate CI/test traffic — check `tests/conftest.py`'s async
  test client bypasses or use a generous enough limit that the test suite doesn't trip it

## Acceptance criteria
- [ ] Starting the app with `APP_ENV != "dev"` and `SECRET_KEY = "change-me"` fails fast with a
  clear error message, doesn't silently boot
- [ ] 6 rapid login attempts from the same client within a minute → the 6th returns 429
- [ ] `python3 -m pytest tests/ -q` — 324+ pass (existing suite unaffected, new tests added and
  passing) — **run with no other pytest process active and a freshly reset test DB**, this
  suite is known to produce false failures under process/DB contention, see
  `docs/PROJECT_HISTORY.md`
- [ ] `ruff check` on all touched files — clean
- [ ] A new invoice created via API includes correct `gst_amount` (18% of subtotal by default)
  and `total_amount` reflects it
- [ ] `npm run typecheck` — clean if any frontend file was touched for GST display

## How to deliver
1. Implement all 4 items
2. Run every acceptance check above
3. Write report to `work/reports/wave-18/01-security-hardening.report.md`
4. Stop

## Constraints
- Time budget: 120 min
- Flag any new dependency (e.g. a rate-limiting library) explicitly in the report rather than
  adding it silently
- Don't touch CORS_ORIGINS' actual value — only fix how it's read/enforced, the real prod value
  is still pending IT's answer
- Allowed tools: file edit, pytest, ruff, npm, curl
