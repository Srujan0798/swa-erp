# Wave 12 — Gotchas

> **Source:** Harvested from `work/reports/wave-12/01-independent-verification.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### Migration/model drift is real
Independent verification found + fixed real migration/model drift. Docker never actually worked before this wave. Don't assume "it compiled" = "it works" — verify against a fresh DB.

### Full suite has known contention
Running the entire 339-test suite serially against a single Postgres hits a known process-contention issue documented in `docs/PROJECT_HISTORY.md` (58 errors / 3 fails). Every wave passes when run in isolation.

### Auth rate-limiter kills test suite
The `3e0f137` fix commit describes 177 errors caused by the rate limiter before being fixed. Like the DB-fixture gotcha, this produces unrelated-looking mass failures, not an obvious single error in the failing module.
