# Wave 26 — Gotchas

> **Source:** Harvested from `work/reports/wave-26/*` — real gotchas only, nothing invented.

## Known pitfalls

### 122MB of session exports in git history
`docs/historical/session_exports/` (142 files, 122MB) — already committed, so deleting from working tree does NOT shrink repo. Contains 777K chars of reasoning not referenced by any canonical doc. Decisions/gotchas in §2 and §5 were extracted into `docs/PROJECT_HISTORY.md` first.

### Code gotchas NOT documented
`invoice.py` date/Date bug, BOQ RBAC bug, `.join("boq")` bug, `conftest.py` overwrite, `datetime not JSON serializable` — these are NOT in `docs/PROJECT_HISTORY.md` (UNVERIFIED). Worth adding.

### Auth rate-limiter kills test suite
The `3e0f137` fix commit describes 177 errors caused by the rate limiter before being fixed. Like the DB-fixture gotcha, this produces unrelated-looking mass failures, not an obvious single error. Same class as Postgres-native-ENUM + pytest-fixture-scoping gotcha.

### Postgres-native-ENUM + fixture scoping gotcha
Drop without `checkfirst`, pooled-stale OIDs → unrelated multi-module failures. Already in `docs/PROJECT_HISTORY.md:37-64`.

### KIMI.md ↔ CLAUDE.md byte-identical alias is a maintenance trap
One edit silently diverges. A symlink preserves the "interchangeable orchestrator" behavior with zero drift risk. (Resolved: CLAUDE.md + KIMI.md are now symlinks; AGENTS.md added in wave-45.)

### wave9handoff.md §8 has unique architectural patterns
Service/repo conventions, reference-ID service signature, zero-padded alembic rev-ids — NOT in PROJECT_HISTORY or conventions.md and would take an engineer hours to rediscover. Extracted into wave-28 item 1.

### Version still 0.2.0
`pyproject.toml:7` and `package.json:4` still `0.2.0` though waves 4-31 shipped. Release-versioning discipline is missing.
