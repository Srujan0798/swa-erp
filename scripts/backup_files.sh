#!/usr/bin/env bash
# Usage: ./scripts/backup_files.sh [output_dir] [source_dir] [retention_days]
# Backs up the uploads/ directory (local filesystem storage) to a timestamped
# .tar.gz archive, then deletes backups older than retention_days (default 90).
#
# File storage in this project is currently local-fs (`uploads/` at the repo
# root); see src/backend/core/config.py and the brief. If/when MinIO/S3 is
# wired in, add a second code path here that uses `mc mirror` or `aws s3 sync`
# — for now the brief explicitly says: "back up whichever is actually active".
set -euo pipefail

OUTPUT_DIR="${1:-./backups/files}"
SOURCE_DIR="${2:-./uploads}"
RETENTION_DAYS="${3:-90}"

if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "ERROR: source directory $SOURCE_DIR does not exist" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="$OUTPUT_DIR/swa_erp_files_backup_${TIMESTAMP}.tar.gz"

echo "==> Backing up files"
echo "    source       = $SOURCE_DIR"
echo "    output       = $OUT_FILE"
echo "    retention    = ${RETENTION_DAYS} days"

# tar with -C so the archive root is the contents of uploads/ (not uploads/ itself)
# Capture failure so we can clean up the partial archive.
if ! tar -czf "$OUT_FILE" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")"; then
    echo "ERROR: tar failed; removing partial $OUT_FILE" >&2
    rm -f "$OUT_FILE"
    exit 1
fi

FINAL_SIZE=$(stat -f%z "$OUT_FILE" 2>/dev/null || stat -c%s "$OUT_FILE")
echo "==> File backup complete: $OUT_FILE (${FINAL_SIZE} bytes)"

# Retention pruning
PRUNED=0
while IFS= read -r -d '' f; do
    rm -f "$f"
    PRUNED=$((PRUNED + 1))
done < <(find "$OUTPUT_DIR" -maxdepth 1 -type f -name 'swa_erp_files_backup_*.tar.gz' -mtime +"${RETENTION_DAYS}" -print0)

if [[ "$PRUNED" -gt 0 ]]; then
    echo "==> Pruned $PRUNED file backup(s) older than ${RETENTION_DAYS} days"
fi

echo "==> Done."
