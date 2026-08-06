#!/usr/bin/env bash
# Usage: ./scripts/restore_db.sh <backup_file.sql.gz> [--yes]
# DESTRUCTIVE: this REPLACES all data in the target database.
# Always prompts for confirmation unless --yes is passed.
set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <backup_file.sql.gz> [--yes]" >&2
    exit 2
fi

BACKUP_FILE="$1"
AUTO_YES="false"
if [[ "${2:-}" == "--yes" ]]; then
    AUTO_YES="true"
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
    echo "ERROR: backup file not found: $BACKUP_FILE" >&2
    exit 1
fi

# Same default-fallback as backup_db.sh / seed_demo.py / config.py
DEFAULT_DB_URL="postgresql://swa:swa@localhost:5432/swa_erp"
DATABASE_URL="${DATABASE_URL:-$DEFAULT_DB_URL}"

# Parse host / port / db / user from URL for the prompt.
# Format: postgresql://user:password@host:port/dbname?params
DB_USER="$(printf '%s' "$DATABASE_URL" | sed -E 's#^postgresql://##; s#@.*$##' | cut -d: -f1)"
DB_HOST_PORT="$(printf '%s' "$DATABASE_URL" | sed -E 's#^postgresql://[^@]+@##; s#/.*$##')"
DB_HOST="${DB_HOST_PORT%:*}"
DB_PORT="${DB_HOST_PORT##*:}"
DB_NAME="$(printf '%s' "$DATABASE_URL" | sed -E 's#^postgresql://[^/]+/##; s#\?.*$##')"
[[ -z "$DB_PORT" || "$DB_PORT" == "$DB_HOST" ]] && DB_PORT="5432"

echo "=================================================="
echo "  DATABASE RESTORE (DESTRUCTIVE)"
echo "=================================================="
echo "  backup file : $BACKUP_FILE"
echo "  target db   : $DB_NAME"
echo "  host        : $DB_HOST"
echo "  port        : $DB_PORT"
echo "  user        : $DB_USER"
echo "=================================================="
echo "  This will REPLACE all data in '$DB_NAME' on"
echo "  $DB_HOST:$DB_PORT."
echo "=================================================="

if [[ "$AUTO_YES" != "true" ]]; then
    # Read from /dev/tty when available so the prompt works in pipes too
    if [[ -t 0 ]]; then
        read -r -p "Type 'yes' to continue: " CONFIRM
    else
        read -r -p "Type 'yes' to continue: " CONFIRM < /dev/tty
    fi
    if [[ "$CONFIRM" != "yes" ]]; then
        echo "Aborted. (You must type 'yes' literally.)"
        exit 1
    fi
else
    echo "--yes passed; skipping confirmation"
fi

# Verify the backup is actually gzip before piping — fail loud, not silent
if ! gzip -t "$BACKUP_FILE" 2>/dev/null; then
    echo "ERROR: $BACKUP_FILE is not a valid gzip file" >&2
    exit 1
fi

echo "==> Restoring $BACKUP_FILE"

# gunzip | psql. Capture both exit codes.
if ! gunzip -c "$BACKUP_FILE" | psql "$DATABASE_URL" --set ON_ERROR_STOP=on --single-transaction; then
    echo "ERROR: psql restore failed; database may be in a partial state" >&2
    exit 1
fi

echo "==> Restore complete. Verify with:"
echo "    psql $DATABASE_URL -c '\\dt'"
echo "    psql $DATABASE_URL -c 'SELECT count(*) FROM <table>'"
