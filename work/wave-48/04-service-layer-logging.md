# Wave-48 Task 04 — Zero business-logic logging across all 30 services

## Verified finding
`grep -rln "logger\.\|log\.error\|log\.warning\|structlog" src/backend/services/*.py` → **0 of 30 services**. Middleware (`src/backend/core/middleware.py`) logs HTTP-level request/response with a bound `request_id` via `structlog`, but nothing inside a service function logs anything.

**Why this matters here specifically:** the client has no IT department. When a request fails, the only trace is `request_end status_code=500 request_id=<uuid>` — no indication of WHICH business rule tripped, which row of an Excel import failed, or why a quote calculation hit an edge case. Whoever ends up debugging (remotely, likely you) has a UUID and nothing else.

`import_service.py` alone has 5+ `except` blocks (lines 98, 111, 123, 515, 554) that catch and handle errors without logging what was caught.

## Files you own
- `src/backend/services/import_service.py` (highest error-surface: parses real client Excel data)
- `src/backend/services/invoice_service.py`, `src/backend/services/quote_service.py` (money-sensitive)
- `src/backend/services/inquiry_service.py` (the core conversion flow, also touched by wave-49)

## The work

Reuse the existing `structlog` logger already configured in `core/middleware.py` — do not introduce a second logging system. Get the request-scoped logger the same way middleware does (`structlog.get_logger()`), so log lines automatically inherit the bound `request_id` via contextvars.

Add logging at:
1. **Every `except` block that currently handles an error silently** — log what was caught, with enough context to reproduce (which row/ID/input, not just the exception type).
2. **Key business decisions in the core flows** — e.g. in `inquiry_service.py`'s `convert_inquiry`, log which branch was taken (new client vs. reused existing client) and the resulting IDs.
3. **Import row-level failures** — `import_service.py` should log which row number and what validation failed, not just increment an error counter.

Do NOT log sensitive data unredacted (PII, tokens, secrets) — check what the existing Sentry `scrub_pii` pattern in `core/errors.py` considers sensitive and follow the same list.

## Acceptance criteria
- [ ] Deliberately trigger a failure in each of the 4 owned files (e.g. malformed Excel row, invalid quote transition) and show the resulting log line contains enough to diagnose it without a debugger attached — paste real log output
- [ ] No sensitive fields (passwords, tokens, full PAN/GSTIN) appear unredacted in any new log line
- [ ] Full backend suite still green

## Deliver
`work/reports/wave-48/04-service-layer-logging.report.md`. Commit before writing it.

## Constraints
- Time budget: 90 min · commit per file
- Scope is these 4 files only — document the remaining 26 services as backlog, don't attempt all of them
