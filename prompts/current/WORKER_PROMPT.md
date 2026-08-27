#!/usr/bin/env bash
# If the project tolerates symlinks (check preflight), make AGENTS.md a symlink to CLAUDE.md.
# KIMI.md is already a symlink to CLAUDE.md by design.

set -euo pipefail

REPO_ROOT="${1:-.}"
AGENTS="$REPO_ROOT/AGENTS.md"
CLAUDE="$REPO_ROOT/CLAUDE.md"

if [ ! -f "$CLAUDE" ]; then
  echo "ERROR: CLAUDE.md not found at $CLAUDE" >&2
  exit 1
fi

if [ -L "$AGENTS" ]; then
  echo "OK: AGENTS.md already a symlink -> $(readlink "$AGENTS")"
elif [ -f "$AGENTS" ]; then
  echo "WARNING: AGENTS.md exists as a regular file — not overwriting" >&2
  echo "Run manually: rm $AGENTS && ln -s CLAUDE.md $AGENTS" >&2
  exit 1
else
  cd "$REPO_ROOT"
  ln -s CLAUDE.md AGENTS.md
  echo "CREATED: AGENTS.md -> CLAUDE.md"
fi

# CI check: verify all three resolve to identical content
if command -v md5 >/dev/null 2>&1; then
  SUM_CLAUDE=$(md5 -q "$CLAUDE")
  SUM_AGENTS=$(md5 -q "$AGENTS")
  if [ "$SUM_CLAUDE" = "$SUM_AGENTS" ]; then
    echo "PASS: AGENTS.md and CLAUDE.md are identical (md5: $SUM_CLAUDE)"
  else
    echo "FAIL: AGENTS.md and CLAUDE.md differ" >&2
    exit 1
  fi
else
 diff -q "$CLAUDE" "$AGENTS" >/dev/null 2>&1 && echo "PASS: AGENTS.md and CLAUDE.md are identical" || {
    echo "FAIL: AGENTS.md and CLAUDE.md differ" >&2
    exit 1
  }
fi
