# AGENT-L7-B: Backup/restore make targets + restore dry-run

Repo: `/Users/srujansai/Desktop/swa-erp` (main). MAY EDIT: Makefile, scripts/backup_db.sh, scripts/restore_db.sh, scripts/backup_files.sh, scripts/restore_files.sh, docs/DEPLOYMENT_CHECKLIST.md. NO pytest.

## Summary of changes

1. **Makefile** — updated `restore-db` usage text, added `restore-files` target, added daily DB / weekly files cron cadence comment, added `restore-files` to .PHONY
2. **scripts/restore_db.sh** — rewritten with dry-run-by-default mode (--force needed for live restore, + interactive "yes")
3. **scripts/restore_files.sh** — NEW, same pattern as restore_db.sh (dry-run default, --force to execute)
4. **DEPLOYMENT_CHECKLIST.md** — added Section 5 with backup cadence, dry-run checklist items, retention policies, safety notes
5. **Dry-run executed** against dev DB (swa_erp @ localhost:5432) — both restore-db and restore-files printed commands cleanly, exit 0, no changes made

## Dry-run output (executed, not restored)

```
$ make restore-db file=./backups/db/swa_erp_backup_20260918_212326.sql.gz
==================================================
  DATABASE RESTORE
  MODE: DRY-RUN (no changes will be made)
==================================================
  backup file : ./backups/db/swa_erp_backup_20260918_212326.sql.gz
  target db   : swa_erp
  host        : localhost
  port        : 5432
  user        : swa
==================================================

==> DRY-RUN: the following commands would execute:

    # 1. Verify gzip integrity (already checked above)
    gzip -t ./backups/db/swa_erp_backup_20260918_212326.sql.gz

    # 2. Drop and recreate the public schema (destructive)
    psql postgresql://swa:***@localhost:5432/swa_erp -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'

    # 3. Restore from backup
    gunzip -c ./backups/db/swa_erp_backup_20260918_212326.sql.gz | psql postgresql://swa:***@localhost:5432/swa_erp --set ON_ERROR_STOP=on --single-transaction

==> DRY-RUN complete. No changes made.
==> To actually restore, run: ./scripts/restore_db.sh ./backups/db/swa_erp_backup_20260918_212326.sql.gz --force

$ make restore-files file=./backups/files/swa_erp_files_backup_20260918_212338.tar.gz
==================================================
  FILES RESTORE
  MODE: DRY-RUN (no changes will be made)
==================================================
  backup file : ./backups/files/swa_erp_files_backup_20260918_212338.tar.gz
  target dir  : ./uploads
==================================================

==> DRY-RUN: the following command would execute:

    tar -xzf ./backups/files/swa_erp_files_backup_20260918_212338.tar.gz -C .

==> DRY-RUN complete. No changes made.
==> To actually restore, run: ./scripts/restore_files.sh ./backups/files/swa_erp_files_backup_20260918_212338.tar.gz --force
```

## Verification

- `make backup-db` executed: produced 27619-byte .sql.gz against localhost:5432 swa_erp (live dev DB)
- `make backup-files` executed: produced 524367-byte .tar.gz of uploads/
- `make restore-db` (dry-run) executed: exit 0, no changes to DB
- `make restore-files` (dry-run) executed: exit 0, no changes to uploads/
- bash syntax check via execution (scripts ran cleanly with set -euo pipefail)
- No actual restore performed (dry-run only, per instructions)

## Notes

- Pre-existing `smoke` target is duplicated in Makefile (lines 87 and 146) — not touched (surgical scope).
- `scripts/backup_db.sh` and `scripts/backup_files.sh` were pre-existing and already correct — no changes needed there.
- Pre-existing `scripts/restore_db.sh` was rewritten to dry-run-by-default mode.

## NOT MEASURED

- Actual restore against a fresh DB (would require --force + interactive yes); NOT done — do not re-import/pollute before the meeting.