# Task 01 — Backup, restore, and operational scripts

## What to do
Meeting 2 explicitly asked for "daily DB dump, weekly file backup" as the intended backup
strategy, and it was never built — confirmed by grep, `scripts/` has zero backup-related files.
Build the scripts now; they work identically whether run against the current dev Docker stack or
the eventual production server, since a `pg_dump`/file-copy doesn't care about the surrounding
infra details still pending from IT.

## Files to create
- CREATE: `scripts/backup_db.sh` — `pg_dump` wrapper, timestamped output, configurable retention
- CREATE: `scripts/backup_files.sh` — backs up `uploads/` (or MinIO bucket if already wired for
  file storage — check `src/backend/core/config.py` / wherever file storage is configured to see
  if MinIO is actually in use yet or if it's still local-fs `uploads/`; back up whichever is
  actually active)
- CREATE: `scripts/restore_db.sh` — restores from a `backup_db.sh` output file, with a
  confirmation prompt before it overwrites anything (this is a destructive operation, never run
  silently)
- CREATE: `docs/runbook_backup_restore.md` — short, concrete runbook: how to run backups
  manually, how to schedule them, how to restore, how to verify a restore succeeded
- CREATE: `tests/wave-19/test_backup_scripts.py` — test the scripts' logic where testable (e.g.
  retention-count pruning, filename timestamp format) against a temp directory; full
  `pg_dump`/`psql` execution can be tested against the local test DB if available, skip
  gracefully if `pg_dump` isn't on PATH in the test environment

## Files to modify
- MODIFY: `Makefile` — add `make backup-db`, `make backup-files`, `make restore-db file=<path>`
  targets wrapping the scripts above
- MODIFY: `docker-compose.yml` — OPTIONAL: add a scheduled backup sidecar container only if it's
  a clean, low-risk addition; if it would meaningfully complicate the compose file, skip it and
  just document the cron-based approach in the runbook instead (this is a judgment call — explain
  which you chose and why in the report)

## Files you must NOT touch
- Any Alembic migration file
- `src/backend/` application code — this task is pure ops tooling

## The core problem (inline)

### `backup_db.sh`
```bash
#!/usr/bin/env bash
# Usage: ./scripts/backup_db.sh [output_dir] [retention_days]
# Dumps DATABASE_URL (or a sensible default matching scripts/seed_demo.py's pattern) to a
# timestamped .sql.gz file, then deletes backups older than retention_days (default 30).
```
Read `DATABASE_URL` from environment with the same default-fallback pattern already used in
`scripts/seed_demo.py` (`os.environ.get(...)` — actually this is bash, so mirror the intent:
read `$DATABASE_URL` env var, fall back to the same default connection string used elsewhere in
this repo for consistency). Output naming: `swa_erp_backup_YYYYMMDD_HHMMSS.sql.gz`. Compress
with gzip. Exit non-zero on any pg_dump failure — don't silently produce an empty/corrupt backup
file and report success.

### `backup_files.sh`
Same pattern, tar+gzip the uploads directory (or MinIO bucket, whichever is live) into a
timestamped archive, same retention pruning.

### `restore_db.sh`
```bash
# Usage: ./scripts/restore_db.sh <backup_file.sql.gz>
# Prompts: "This will REPLACE all data in <db name>. Type 'yes' to continue:"
# Then gunzip | psql
```
Must show which database it's about to overwrite before prompting — the same dual-Postgres
confusion documented in wave-14's report (host vs. docker Postgres both on 5432) makes this
especially important to get right; print the resolved `DATABASE_URL` host/port/dbname clearly
before the confirmation prompt.

### Retention policy
Default: keep daily DB backups for 30 days, weekly file backups for 90 days — these are
reasonable defaults, not confirmed requirements; state this explicitly in the runbook as "default,
adjust if the client specifies otherwise."

## Acceptance criteria
- [ ] `./scripts/backup_db.sh` (against the local dev/test DB) produces a valid, restorable
  `.sql.gz` file
- [ ] `./scripts/restore_db.sh <that file>` — with confirmation answered "yes" — successfully
  restores into a scratch database (don't test-restore over the real dev DB; create a throwaway
  DB for this verification and drop it after)
- [ ] Retention pruning actually deletes files older than the configured window (test with
  artificially-aged filenames in a temp dir)
- [ ] `python3 -m pytest tests/ -q` — no regression (run with a clean environment, see the
  process-contention note in `docs/PROJECT_HISTORY.md`)
- [ ] `docs/runbook_backup_restore.md` is concrete enough that someone unfamiliar with the
  project could run a backup and a restore from it alone

## How to deliver
1. Implement all scripts + runbook + Makefile targets
2. Verify a real backup → restore round-trip against a scratch database
3. Write report to `work/reports/wave-19/01-backup-and-ops-scripts.report.md`
4. Stop

## Constraints
- Time budget: 90 min
- Never make `restore_db.sh` destructive without an explicit confirmation step
- No new dependencies beyond what's already available (`pg_dump`, `psql`, `tar`, `gzip` — all
  standard, no new Python/Node packages needed for this task)
- Allowed tools: file edit, bash, psql, pg_dump, pytest
