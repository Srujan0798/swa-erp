# Task 01 — Backup, restore, and operational scripts

## Result
**DONE** — All 5 acceptance criteria pass. Backup, restore, and file-backup
scripts are in place, the runbook is concrete, Makefile targets work, and the
test suite proves the round-trip end-to-end against a live scratch database.

## What shipped

| File | Status | Purpose |
| --- | --- | --- |
| `scripts/backup_db.sh` | new (chmod +x) | `pg_dump` → timestamped `.sql.gz` with retention pruning; fails loud on empty/corrupt output |
| `scripts/backup_files.sh` | new (chmod +x) | `tar -czf` of `uploads/` → timestamped `.tar.gz` with retention pruning |
| `scripts/restore_db.sh` | new (chmod +x) | `gunzip \| psql --single-transaction`; prints resolved host/port/db BEFORE prompting; rejects anything other than literal `yes`; `--yes` flag for CI |
| `docs/runbook_backup_restore.md` | new | Concrete how-to: manual backup, cron schedule, restore, verify, dual-Postgres trap, off-host extension |
| `tests/wave-19/test_backup_scripts.py` | new (5 tests) | Filename format, retention pruning (DB + files), full live backup→drop→restore→verify round-trip |
| `Makefile` | modified | Added `backup-db`, `backup-files`, `restore-db file=<path>` targets and `.PHONY` entries; existing targets untouched |
| `docker-compose.yml` | NOT modified | See judgment-call note below |

### Makefile diff (summary)
- Added `backup-db backup-files restore-db` to `.PHONY`
- Added 3 new lines to the `help` target output
- Added 3 new targets wrapping the scripts
- All pre-existing targets (`install`, `dev`, `test`, `test-wave`, `lint`,
  `format`, `migrate`, etc.) are byte-for-byte unchanged

### Judgment call: docker-compose sidecar container
**Skipped.** The brief explicitly allowed skipping the sidecar "if it would
meaningfully complicate the compose file." A backup sidecar would require:
- A custom image or another `postgres`-based image with cron + bash
- A second volume for backup output
- Env vars for `DATABASE_URL` + retention + schedule
- A healthcheck or one-shot `restart: always` decision

That's a meaningful addition for a feature that the runbook covers cleanly
with a 4-line crontab snippet. The cron-based approach is what the runbook
documents instead. (When the eventual production server details are
finalized — IT is still figuring those out per `docs/IT_BRIEF.md` — this can
be revisited; the scripts themselves are infra-agnostic and work the same
way whether invoked by cron, a sidecar, or an SRE's hands.)

## Acceptance verification (per brief)

- [x] `./scripts/backup_db.sh` produces a valid, restorable `.sql.gz`
  - Live-ran against `postgresql://swa:swa@localhost:5432/swa_erp`
  - Output: `./backups/db/swa_erp_backup_20260721_022649.sql.gz` (27,707 bytes)
  - Independently `gunzip -t`'d and round-tripped through `psql` (see below)
- [x] `./scripts/restore_db.sh <file>` restores into a scratch database
  - **Full live round-trip performed:** created `swa_erp_roundtrip_<pid>`,
    populated with a `roundtrip` table, backed it up, dropped the database,
    recreated it empty, restored from backup, verified the 2 rows came back
    with their `marker` text intact
  - Scratch DB was dropped at end of test; the real dev DB was never touched
- [x] Retention pruning deletes aged files
  - Tested two ways: synthetic-aged files (always works, no DB needed) and
    a real backup where an artificially-aged file is pruned on the next run
- [x] `python3 -m pytest tests/ -q` — no regression
  - Wave-19 (5 new) + wave-18 (15 existing) all pass cleanly: **20/20**
  - Other waves hit the known process-contention issue documented in
    `docs/PROJECT_HISTORY.md` (the same 58 errors / 3 fails appear when
    running the entire 339-test suite serially against a single Postgres;
    every wave passes when run in isolation). My changes touch only
    `scripts/`, `docs/`, `tests/wave-19/`, and `Makefile` — none of which
    affect the application code under test
- [x] Runbook is concrete enough to act on without prior context
  - Includes: cron recipe, env var behaviour, dual-Postgres warning,
    per-table verification commands, off-host extension hook

## Test counts & lint

- New tests: **5/5 pass** in `tests/wave-19/test_backup_scripts.py`
  - `test_backup_db_filename_format`
  - `test_backup_files_filename_format`
  - `test_backup_db_retention_prunes_aged_files` (with a graceful skip path
    if `pg_dump` isn't on PATH)
  - `test_backup_files_retention_prunes_aged_files`
  - `test_backup_restore_roundtrip_against_scratch_db` (the live one)
- Wave-19 + wave-18 combined: **20/20 pass** in 36.15s
- Lint: `ruff check tests/wave-19/test_backup_scripts.py` → **All checks passed!**
- Shell lint: `bash -n` clean on all 3 new scripts

## Live verification commands run (excerpt)

```bash
# 1. DB backup
$ ./scripts/backup_db.sh /tmp/swa_backup_test 30
==> Backup complete: /tmp/swa_backup_test/swa_erp_backup_20260721_021601.sql.gz (27710 bytes)

# 2. File backup
$ ./scripts/backup_files.sh /tmp/swa_files_test ./uploads 90
==> File backup complete: .../swa_erp_files_backup_20260721_021610.tar.gz (83371 bytes)

# 3. Round-trip (excerpt)
$ psql -c "CREATE DATABASE swa_erp_roundtrip_$$;"
$ psql $SCRATCH_URL -c "INSERT INTO roundtrip VALUES (1, 'before-marker'), (2, 'after-marker');"
$ DATABASE_URL=$SCRATCH_URL ./scripts/backup_db.sh /tmp/swa_roundtrip 30
$ psql -c "DROP DATABASE $SCRATCH; CREATE DATABASE $SCRATCH;"
$ DATABASE_URL=$SCRATCH_URL ./scripts/restore_db.sh /tmp/swa_roundtrip/swa_erp_backup_*.sql.gz --yes
$ psql $SCRATCH_URL -c "SELECT count(*) FROM roundtrip;"
 count
-------
     2          # <-- restored data is back
$ psql $SCRATCH_URL -c "SELECT marker FROM roundtrip ORDER BY id;"
 before-marker
 after-marker  # <-- exact rows preserved

# 4. Real dev DB untouched
$ PGPASSWORD=swa psql -h localhost -p 5432 -U swa -d swa_erp -c "SELECT count(*) FROM users;"
 7              # <-- same as before this task

# 5. Makefile targets
$ make backup-db     # → ./backups/db/swa_erp_backup_20260721_022649.sql.gz
$ make backup-files  # → ./backups/files/swa_erp_files_backup_20260721_022650.tar.gz
$ make help          # → new targets listed
```

## Files NOT touched (per brief)
- `src/backend/` (zero changes)
- Any Alembic migration
- `.github/workflows/*.yml` (CI)
- `tests/conftest.py` (global test fixture)
- `docker-compose.yml` (judgment-call skip, justified above)

## Blockers
None.
