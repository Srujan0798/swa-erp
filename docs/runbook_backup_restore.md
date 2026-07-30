# Runbook — Backup & Restore

Operational guide for the swa-erp backup and restore scripts.

## What gets backed up

| What | Script | Default destination | Default retention |
| --- | --- | --- | --- |
| PostgreSQL database (full SQL dump) | `scripts/backup_db.sh` | `./backups/db/` | 30 days |
| `uploads/` directory (file storage) | `scripts/backup_files.sh` | `./backups/files/` | 90 days |

**Retention is configurable.** The 30/90 day defaults are reasonable starting points
but not confirmed client requirements — adjust if the client specifies otherwise
by passing the retention as the second/third argument to the script (or by editing
the `Makefile` targets).

**File storage is currently local-fs** (`./uploads/` at the repo root). If/when
MinIO or S3 is wired in for file storage, extend `scripts/backup_files.sh` to use
`mc mirror` or `aws s3 sync` for that path.

## Quick start

```bash
# Back up the database to ./backups/db/ (default retention 30 days)
make backup-db

# Back up the uploads/ directory to ./backups/files/ (default retention 90 days)
make backup-files

# Restore a database backup (DESTRUCTIVE — will prompt for confirmation)
make restore-db file=./backups/db/swa_erp_backup_20260121_021400.sql.gz
```

The `Makefile` targets simply wrap the scripts in `scripts/`, so you can call
the scripts directly too:

```bash
./scripts/backup_db.sh                                    # use all defaults
./scripts/backup_db.sh /var/backups/swa 14                # custom dir, 14-day retention
./scripts/backup_files.sh /var/backups/swa/files /srv/uploads 60
./scripts/restore_db.sh ./backups/db/swa_erp_backup_20260121_021400.sql.gz
```

## Environment variables

Both backup/restore scripts read `DATABASE_URL`. If unset, they fall back to
`postgresql://swa:swa@localhost:5432/swa_erp` (same default used by
`src/backend/core/config.py` and `scripts/seed_demo.py`).

The scripts intentionally print the resolved `DATABASE_URL` (host/port/db) on
every run, so you can never accidentally back up or restore the wrong database
silently. There are two Postgres instances on this host (host PG on 5432, and
the docker one inside the colima VM also exposed on 5432) — see the
**Dual-Postgres trap** section below.

## How to run a backup manually

```bash
# 1. (Optional) confirm which database you're pointing at
echo "$DATABASE_URL"

# 2. Run the backup
./scripts/backup_db.sh

# 3. Verify the file exists and is non-empty
ls -lh ./backups/db/
zcat ./backups/db/swa_erp_backup_*.sql.gz | head -20
```

Successful output looks like:

```
==> Backing up database
    DATABASE_URL = postgresql://swa:swa@localhost:5432/swa_erp
    output       = ./backups/db/swa_erp_backup_20260121_021400.sql.gz
    retention    = 30 days
==> Backup complete: ./backups/db/swa_erp_backup_20260121_021400.sql.gz (84211 bytes)
==> Done.
```

## How to schedule backups (cron)

On the production host, add the following to root's crontab (`sudo crontab -e`):

```cron
# Daily DB backup at 02:14 (after any ETL windows)
14 2 * * *  /opt/swa-erp/scripts/backup_db.sh  /var/backups/swa/db   30  >> /var/log/swa_backup_db.log  2>&1

# Weekly file backup on Sunday at 03:00
0 3 * * 0   /opt/swa-erp/scripts/backup_files.sh /var/backups/swa/files /opt/swa-erp/uploads 90  >> /var/log/swa_backup_files.log  2>&1
```

Make sure:
- The cron user can read `uploads/`
- The cron user can write to the backup destination
- `pg_dump` and `psql` are on PATH for the cron user (the scripts use
  `/usr/bin/env bash` so this is usually fine on Ubuntu/Debian hosts)

Retention pruning is part of the same script, so each backup run also deletes
files older than the configured window. No separate prune job is needed.

## How to restore

**This replaces ALL data in the target database. There is no undo.**

```bash
# 1. Pick the backup file you want to restore
ls -lh ./backups/db/

# 2. Confirm which database the script is about to overwrite
#    The script prints host/port/db BEFORE asking for confirmation.
./scripts/restore_db.sh ./backups/db/swa_erp_backup_20260121_021400.sql.gz

# 3. The script will say:
#       This will REPLACE all data in 'swa_erp' on localhost:5432.
#       Type 'yes' to continue:
#    Type 'yes` (literally) to proceed. Anything else aborts.

# 4. After restore, the script prints verification hints:
#       psql postgresql://...:5432/swa_erp -c '\dt'
#       psql postgresql://...:5432/swa_erp -c 'SELECT count(*) FROM <table>'
```

For non-interactive restores (e.g. a CI smoke test against a scratch DB), pass
`--yes`:

```bash
./scripts/restore_db.sh ./backups/db/swa_erp_backup_*.sql.gz --yes
```

## How to verify a restore succeeded

```bash
# 1. Table list looks right
psql "$DATABASE_URL" -c '\dt'

# 2. Row counts on the key tables match what you expect
psql "$DATABASE_URL" -c "SELECT count(*) FROM users"
psql "$DATABASE_URL" -c "SELECT count(*) FROM clients"
psql "$DATABASE_URL" -c "SELECT count(*) FROM projects"

# 3. A specific sanity-check row is present
psql "$DATABASE_URL" -c "SELECT id, name, role FROM users WHERE email = 'admin@swa.co.in'"
```

The pytest test `tests/wave-19/test_backup_scripts.py` automates a full
backup → restore → verify cycle against a scratch database (skipped gracefully
if `pg_dump`/`psql` aren't on PATH).

## Dual-Postgres trap

The host and the docker stack both expose Postgres on port 5432, with the same
`postgresql://swa:swa@.../swa_erp` URL. From inside the docker network, the
hostname is `postgres`; from the host, it's `localhost`. The `DATABASE_URL`
you export (or the one that was last sourced from `.env`) determines which
one the scripts talk to.

Before any restore, always sanity-check:

```bash
# Which Postgres am I talking to?
PGPASSWORD=swa psql "$DATABASE_URL" -c "SELECT current_database(), inet_server_addr(), inet_server_port();"
```

The `restore_db.sh` script always prints host/port/dbname before prompting,
and `psql` is invoked with `--single-transaction` + `--set ON_ERROR_STOP=on`
so a failure aborts the restore rather than leaving the database half-loaded.

## Off-host backup (eventual)

The current scripts write to local disk. For off-host resilience, add a second
step that ships files to S3/B2/object storage:

```bash
# After the daily backup, push anything newer than 1 day to S3
aws s3 sync /var/backups/swa/db/   s3://swa-erp-backups/db/   --exclude "*" --include "*-1day"
```

That's intentionally out of scope for these scripts — credentials and bucket
policy are an IT/SRE decision, not a script decision.

## File layout

```
scripts/
  backup_db.sh         # pg_dump → .sql.gz with retention
  backup_files.sh      # tar -czf of uploads/ with retention
  restore_db.sh        # gunzip | psql, with confirmation
docs/
  runbook_backup_restore.md   # this file
tests/wave-19/
  test_backup_scripts.py      # retention + filename format + full backup/restore round-trip
```
