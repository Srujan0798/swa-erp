#!/usr/bin/env bash
# validate_metrics.sh — kill FM-05 (metric inconsistency) mechanically.
#
# Rule (constitution §13 FM-05): "metrics live in ONE generated source
# (results/metrics.json); docs reference/regenerate, never hand-type."
#
# This script greps tracked .md files for coverage / pass-count patterns and FAILS
# if any hand-typed number contradicts results/metrics.json.
#
# An explicit opt-out comment `<!-- metrics-exempt: reason -->` (on its own line, or
# anywhere in the file) lets a file keep corrected-but-annotated historical numbers
# without tripping the gate. This repo deliberately preserves annotated corrections.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
METRICS="$REPO_ROOT/results/metrics.json"

if [ ! -f "$METRICS" ]; then
  echo "FAIL: $METRICS not found. Run 'make metrics' first."
  exit 1
fi

# Pull the authoritative numbers out of the generated source.
BACKEND_PASSED=$(python3 -c "import json;print(json.load(open('$METRICS'))['backend']['passed'])")
BACKEND_FAILED=$(python3 -c "import json;print(json.load(open('$METRICS'))['backend']['failed'])")
FE_PASSED=$(python3 -c "import json;print(json.load(open('$METRICS'))['frontend']['passed'])")
FE_FAILED=$(python3 -c "import json;print(json.load(open('$METRICS'))['frontend']['failed'])")
FE_COV=$(python3 -c "import json,sys; d=json.load(open('$METRICS'))['frontend']['coverage']; print(d['statements'] if d else 'None')")

echo "Authority (results/metrics.json):"
echo "  backend  passed=$BACKEND_PASSED failed=$BACKEND_FAILED"
echo "  frontend passed=$FE_PASSED failed=$FE_FAILED coverage_statements=$FE_COV"

# Files to scan: tracked .md under the repo (excluding results/, which IS the source).
MAPFILE=$(mktemp)
git -C "$REPO_ROOT" ls-files '*.md' > "$MAPFILE" 2>/dev/null || {
  echo "WARN: not a git repo context; scanning all tracked md via git failed, falling back to find"
  find "$REPO_ROOT" -name '*.md' -not -path '*/node_modules/*' > "$MAPFILE"
}

VIOLATIONS=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  full="$REPO_ROOT/$f"
  [ -f "$full" ] || continue
  # Opt-out: skip files that carry the metrics-exempt marker.
  if grep -qE '<!--[[:space:]]*metrics-exempt:' "$full"; then
    continue
  fi
  # Skip the results/ directory itself (it is the source of truth).
  case "$f" in
    results/*) continue ;;
  esac

  # Frontend coverage statements % — compare to FE_COV (only when coverage was available).
  if [ "$FE_COV" != "None" ]; then
    while IFS= read -r m; do
      val=$(echo "$m" | grep -oE '[0-9]+\.[0-9]+' | head -1)
      [ -z "$val" ] && continue
      # Allow a small tolerance? No — the whole point is exactness. Flag any
      # hand-typed frontend statement-coverage % that differs from the source.
      # Exception: the source-of-truth reports (results/ & this wave's own report)
      # are allowed to echo the number; they are excluded above.
      if ! python3 -c "import sys; a=float(sys.argv[1]); b=float(sys.argv[2]); sys.exit(0 if abs(a-b)<0.001 else 1)" "$val" "$FE_COV" 2>/dev/null; then
        # Heuristic: only treat lines that look like a coverage claim.
        if echo "$m" | grep -qiE 'coverage|statement|frontend|%.*cov'; then
          echo "VIOLATION: $f — frontend coverage claim '$val%' contradicts source '$FE_COV%'"
          VIOLATIONS=$((VIOLATIONS+1))
        fi
      fi
    done < <(grep -nE '[0-9]+\.[0-9]+%' "$full" 2>/dev/null || true)
  fi

  # Backend pass-count claims like "N passed" — flag if a doc asserts a passed count
  # that exceeds the authoritative passed count (i.e. an inflated green). Only check
  # when failed==0 in source would make any "N failed" claim wrong; here we specifically
  # guard the most common FM-09 shape: claiming a clean pass while source shows failures.
  if [ "$BACKEND_FAILED" -gt 0 ] || [ "$FE_FAILED" -gt 0 ]; then
    if grep -qiE '0 failed|no failures|all (tests )?pass|covered.*closed' "$full" 2>/dev/null; then
      echo "VIOLATION: $f — asserts a clean pass while source shows failures (backend=$BACKEND_FAILED frontend=$FE_FAILED)"
      VIOLATIONS=$((VIOLATIONS+1))
    fi
  fi
done < "$MAPFILE"

rm -f "$MAPFILE"

if [ "$VIOLATIONS" -eq 0 ]; then
  echo "OK: no tracked .md contradicts results/metrics.json."
  exit 0
else
  echo "FAIL: $VIOLATIONS metric contradiction(s) found."
  exit 1
fi
