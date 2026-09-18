#!/usr/bin/env bash
# Usage: ./scripts/restore_db.sh <backup_file.sql.gz> [--force] [--yes]
# DESTRUCTIVE: REPLACES all data in the target database.
#
# Modes:
#   (no flags)   DRY-RUN — prints every command that WOULD run, exits 0.
#   --force      Actually execute the restore (still prompts unless --yes).
#   --yes        Skip the interactive confirmation (only meaningful with --force).
#
# Cadence note (Meeting 2): daily DB backup / weekly files backup.
set -euo pipefail

FORCE=false
AUTO_YES=false
BACKUP_FILE=""

for arg in "$@"; do
    case "$arg" in
        --force) FORCE=true ;;
        --yes)   AUTO_YES=true ;;
        -*)      echo "Unknown flag: $arg" >&2; exit 2 ;;
        *)       BACKUP_FILE="$arg" ;;
    esac
done

if [[ -z "$BACKUP_FILE" ]]; then
    echo "Usage: $0 <backup_file.sql.gz> [--force] [--yes]" >&2
    exit 2
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
    echo "ERROR: backup file not found: $BACKUP_FILE" >&2
    exit 1
fi

# Same default-fallback as backup_db.sh / seed_demo.py / config.py
DEFAULT_DB_URL="postgresql://swa:swa@localhost:5432/swa_erp"
DATABASE_URL="${DATABASE_URL:-$DEFAULT_DB_URL}"

# Parse host / port / db / user from URL for the prompt and dry-run output.
DB_USER="$(printf '%s' "$DATABASE_URL" | sed -E 's#^postgresql://##; s#@.*$##' | cut -d: -f1)"
DB_HOST_PORT="$(printf '%s' "$DATABASE_URL" | sed -E 's#^postgresql://[^@]+@##; s#/.*$##')"
DB_HOST="${DB_HOST_PORT%:*}"
DB_PORT="${DB_HOST_PORT##*:}"
DB_NAME="$(printf '%s' "$DATABASE_URL" | sed -E 's#^postgresql://[^/]+/##; s#\?.*$##')"
[[ -z "$DB_PORT" || "$DB_PORT" == "$DB_HOST" ]] && DB_PORT="5432"

echo "=================================================="
echo "  DATABASE RESTORE"
if [[ "$FORCE" == "true" ]]; then
    echo "  MODE: LIVE (--force)"
else
    echo "  MODE: DRY-RUN (no changes will be made)"
fi
echo "=================================================="
echo "  backup file : $BACKUP_FILE"
echo "  target db   : $DB_NAME"
echo "  host        : $DB_HOST"
echo "  port        : $DB_PORT"
echo "  user        : $DB_USER"
echo "=================================================="

# Verify the backup is actually gzip before reporting success
if ! gzip -t "$BACKUP_FILE" 2>/dev/null; then
    echo "ERROR: $BACKUP_FILE is not a valid gzip file" >&2
    exit 1
fi

# --- DRY-RUN: print the commands and exit ---
if [[ "$FORCE" != "true" ]]; then
    echo ""
    echo "==> DRY-RUN: the following commands would execute:"
    echo ""
    echo "    # 1. Verify gzip integrity (already checked above)"
    echo "    gzip -t $BACKUP_FILE"
    echo ""
    echo "    # 2. Drop and recreate the public schema (destructive)"
    echo "    psql $DATABASE_URL -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'"
    echo ""
    echo "    # 3. Restore from backup"
    echo "    gunzip -c $BACKUP_FILE | psql $DATABASE_URL --set ON_ERROR_STOP=on --single-transaction"
    echo ""
    echo "==> DRY-RUN complete. No changes made."
    echo "==> To actually restore, run: $0 $BACKUP_FILE --force"
    exit 0
fi

# --- LIVE restore (only reached with --force) ---
echo ""
echo "  WARNING: This will REPLACE all data in '$DB_NAME' on"
echo "  $DB_HOST:$DB_PORT."
echo "=================================================="

if [[ "$AUTO_YES" != "true" ]]; then
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

echo "==> Dropping and recreating public schema"
psql "$DATABASE_URL" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "==> Restoring $BACKUP_FILE"
if ! gunzip -c "$BACKUP_FILE" | psql "$DATABASE_URL" --set ON_ERROR_STOP=on --single-transaction; then
    echo "ERROR: psql restore failed; database may be in a partial state" >&2
    exit 1
fi

echo "==> Restore complete. Verify with:"
echo "    psql $DATABASE_URL -c '\\dt'"
echo "    psql $DATABASE_URL -c 'SELECT count(*) FROM <table>'"
