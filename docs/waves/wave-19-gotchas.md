# Wave 19 — Gotchas

> **Source:** Harvested from `work/reports/wave-19/01-backup-and-ops-scripts.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### Dual-Postgres trap
The runbook documents a dual-Postgres warning — when restoring, make sure you're targeting the right database. The restore script prints resolved host/port/db BEFORE prompting and rejects anything other than literal `yes`.

### Restore script is strict
`restore_db.sh` rejects anything other than literal `yes` (or `--yes` flag for CI). Designed to prevent accidental overwrites.

### Sidecar container skipped intentionally
The brief explicitly allowed skipping the Docker sidecar "if it would meaningfully complicate the compose file." The cron-based approach in the runbook is the documented alternative. When production server details are finalized (IT still figuring out per `docs/IT_BRIEF.md`), this can be revisited.

### Process contention with full suite
Wave-19 + wave-18 combined: 20/20 pass. But other waves hit the known process-contention issue when running the entire 339-test suite serially. Run waves in isolation.
