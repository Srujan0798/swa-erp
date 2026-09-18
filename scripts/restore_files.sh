#!/usr/bin/env bash
# Usage: ./scripts/restore_files.sh <backup_file.tar.gz> [--force] [--yes]
# DESTRUCTIVE: OVERWRITES files in the target uploads/ directory.
#
# Modes:
#   (no flags)   DRY-RUN — prints the tar extraction command, exits 0.
#   --force      Actually extract the archive (still prompts unless --yes).
#   --yes        Skip the interactive confirmation (only meaningful with --force).
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
    echo "Usage: $0 <backup_file.tar.gz> [--force] [--yes]" >&2
    exit 2
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
    echo "ERROR: backup file not found: $BACKUP_FILE" >&2
    exit 1
fi

DEFAULT_DB_URL="postgresql://swa:swa@localhost:5432/swa_erp"
DATABASE_URL="${DATABASE_URL:-$DEFAULT_DB_URL}"

# Match backup_files.sh defaults
SOURCE_DIR="./uploads"

echo "=================================================="
echo "  FILES RESTORE"
if [[ "$FORCE" == "true" ]]; then
    echo "  MODE: LIVE (--force)"
else
    echo "  MODE: DRY-RUN (no changes will be made)"
fi
echo "=================================================="
echo "  backup file : $BACKUP_FILE"
echo "  target dir  : $SOURCE_DIR"
echo "=================================================="

# --- DRY-RUN ---
if [[ "$FORCE" != "true" ]]; then
    echo ""
    echo "==> DRY-RUN: the following command would execute:"
    echo ""
    echo "    tar -xzf $BACKUP_FILE -C $(dirname "$SOURCE_DIR")"
    echo ""
    echo "==> DRY-RUN complete. No changes made."
    echo "==> To actually restore, run: $0 $BACKUP_FILE --force"
    exit 0
fi

# --- LIVE restore ---
echo ""
echo "  WARNING: This will OVERWRITE files in $SOURCE_DIR."
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

echo "==> Extracting $BACKUP_FILE to $(dirname "$SOURCE_DIR")"
if ! tar -xzf "$BACKUP_FILE" -C "$(dirname "$SOURCE_DIR")"; then
    echo "ERROR: tar extraction failed" >&2
    exit 1
fi

echo "==> Files restored to $SOURCE_DIR"
