# Wave 29 — Gotchas

> **Source:** Harvested from `work/reports/wave-29/01-stale-claim-fixes.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### 9 docs corrected to match real repo state
Docs corrected: backups, GST, Celery/MinIO target-state, test counts, version/tag reconciliation. When reading old docs, verify against current repo state — status claims drift.

### Test counts in docs are stale
Doc claims like "339 tests" or "344 tests" can be stale. The real count changes with each wave. Verify by running `pytest` yourself.

### Version/tag reconciliation
Tags like `wave-3-complete` exist but `pyproject.toml` and `package.json` still say `0.2.0`. Tags and version numbers can diverge — don't rely on tags for version info.

### GST status
GST was shipped on invoices in wave-18. Docs that say "GST pending" are stale.

### Celery/MinIO target-state
Celery app and MinIO storage are wired (wave-31). Docs describing them as "planned" or "deferred" are stale.
