#!/usr/bin/env bash
# Usage: ./scripts/backup_db.sh [output_dir] [retention_days]
# Dumps DATABASE_URL (or a sensible default matching scripts/seed_demo.py's pattern) to a
# timestamped .sql.gz file, then deletes backups older than retention_days (default 30).
set -euo pipefail

OUTPUT_DIR="${1:-./backups/db}"
RETENTION_DAYS="${2:-30}"

# Match the default used by scripts/seed_demo.py and src/backend/core/config.py
DEFAULT_DB_URL="postgresql://swa:swa@localhost:5432/swa_erp"
DATABASE_URL="${DATABASE_URL:-$DEFAULT_DB_URL}"

mkdir -p "$OUTPUT_DIR"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="$OUTPUT_DIR/swa_erp_backup_${TIMESTAMP}.sql.gz"

echo "==> Backing up database"
echo "    output       = $OUT_FILE"
echo "    retention    = ${RETENTION_DAYS} days"

# Run pg_dump and gzip. Capture exit codes separately so we can fail loudly
# instead of silently producing an empty/corrupt file.
TMP_SQL="$(mktemp -t swa_erp_backup.XXXXXX.sql)"
trap 'rm -f "$TMP_SQL"' EXIT

if ! pg_dump "$DATABASE_URL" --no-owner --no-privileges --file="$TMP_SQL"; then
    echo "ERROR: pg_dump failed for $DATABASE_URL" >&2
    exit 1
fi

if [[ ! -s "$TMP_SQL" ]]; then
    echo "ERROR: pg_dump produced an empty file; aborting before gzip" >&2
    exit 1
fi

if ! gzip -c "$TMP_SQL" > "$OUT_FILE"; then
    echo "ERROR: gzip failed; removing partial $OUT_FILE" >&2
    rm -f "$OUT_FILE"
    exit 1
fi

FINAL_SIZE=$(stat -f%z "$OUT_FILE" 2>/dev/null || stat -c%s "$OUT_FILE")
echo "==> Backup complete: $OUT_FILE (${FINAL_SIZE} bytes)"

# Retention pruning: delete *.sql.gz files older than RETENTION_DAYS days
PRUNED=0
while IFS= read -r -d '' f; do
    rm -f "$f"
    PRUNED=$((PRUNED + 1))
done < <(find "$OUTPUT_DIR" -maxdepth 1 -type f -name 'swa_erp_backup_*.sql.gz' -mtime +"${RETENTION_DAYS}" -print0)

if [[ "$PRUNED" -gt 0 ]]; then
    echo "==> Pruned $PRUNED backup(s) older than ${RETENTION_DAYS} days"
fi

echo "==> Done."
