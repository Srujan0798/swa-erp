#!/usr/bin/env bash
# validate_execution.sh — kill FM-09 (false status) + FM-12 mechanically.
#
# Implements the ADAPTOID-LITE §4.13 execution-integrity contract:
#   1. No duplicate wave rows in plan/EXECUTION.md (each Wave | row is unique).
#   2. The "active wave" declared in HANDOFF.md matches the highest in-progress wave
#      in plan/EXECUTION.md (when HANDOFF declares one).
#   3. Every SHIPPED wave row carries a commit hash (git sha), so a green claim is
#      always traceable to a real commit.
#
# Exits non-zero on any violation.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EXEC="$REPO_ROOT/plan/EXECUTION.md"
HANDOFF="$REPO_ROOT/HANDOFF.md"

if [ ! -f "$EXEC" ]; then
  echo "FAIL: $EXEC not found."
  exit 1
fi

VIOLATIONS=0

# ── 1. Duplicate wave rows ────────────────────────────────────────────────────
DUPES=$(grep -oE '^\| *[0-9]+ *\|' "$EXEC" 2>/dev/null \
  | grep -oE '[0-9]+' \
  | sort \
  | uniq -d \
  || true)
if [ -n "$DUPES" ]; then
  echo "VIOLATION: duplicate wave row(s) in $EXEC for wave(s): $DUPES"
  VIOLATIONS=$((VIOLATIONS+1))
else
  echo "OK: no duplicate wave rows in $EXEC."
fi

# ── 3. Every SHIPPED wave row has a commit hash ───────────────────────────────
# A SHIPPED row must reference a 7+ char hex sha somewhere on the line.
SHIPPED_TOTAL=0
SHIPPED_OK=0
while IFS= read -r line; do
  # Match a table row beginning with a wave number that contains SHIPPED.
  if echo "$line" | grep -qE '^\| *[0-9]+ *\|' && echo "$line" | grep -qiE 'SHIPPED'; then
    SHIPPED_TOTAL=$((SHIPPED_TOTAL+1))
    if echo "$line" | grep -qE '[0-9a-f]{7,40}'; then
      SHIPPED_OK=$((SHIPPED_OK+1))
    else
      # Extract the wave number for the message.
      wn=$(echo "$line" | grep -oE '^\| *[0-9]+' | grep -oE '[0-9]+' | head -1)
      echo "VIOLATION: SHIPPED wave $wn row has no commit hash in $EXEC."
      VIOLATIONS=$((VIOLATIONS+1))
    fi
  fi
done < "$EXEC"
echo "OK: SHIPPED waves with commit hash: $SHIPPED_OK/$SHIPPED_TOTAL."

# ── 2. Active wave matches across EXECUTION + HANDOFF ──────────────────────────
if [ -f "$HANDOFF" ]; then
  # Find an explicit "active wave" / "current wave" declaration in HANDOFF (case-insensitive).
  ACTIVE_LINE=$(grep -iE 'active wave|current wave|in-progress wave' "$HANDOFF" 2>/dev/null | head -1 || true)
  if [ -n "$ACTIVE_LINE" ]; then
    ACTIVE_W=$(echo "$ACTIVE_LINE" | grep -oE 'wave-?[0-9]+' | grep -oE '[0-9]+' | head -1 || true)
    if [ -n "$ACTIVE_W" ]; then
      # Highest in-progress wave in EXECUTION.
      MAX_INPROG=$(grep -iE 'IN PROGRESS|in progress|🚧' "$EXEC" 2>/dev/null \
        | grep -oE '^\| *[0-9]+' | grep -oE '[0-9]+' | sort -n | tail -1 || true)
      if [ -n "$MAX_INPROG" ] && [ "$ACTIVE_W" != "$MAX_INPROG" ]; then
        echo "VIOLATION: HANDOFF active wave $ACTIVE_W != EXECUTION highest in-progress wave $MAX_INPROG."
        VIOLATIONS=$((VIOLATIONS+1))
      else
        echo "OK: HANDOFF active wave ($ACTIVE_W) consistent with EXECUTION."
      fi
    fi
  else
    echo "NOTE: HANDOFF.md declares no explicit active-wave line; skipping cross-check (2)."
  fi
else
  echo "NOTE: HANDOFF.md not found; skipping cross-check (2)."
fi

if [ "$VIOLATIONS" -eq 0 ]; then
  echo "OK: execution integrity checks passed."
  exit 0
else
  echo "FAIL: $VIOLATIONS execution-integrity violation(s)."
  exit 1
fi
