#!/bin/bash
# Gate tool calls per T0-T3 risk tiering. Blocks T3 absolutely.
# This is illustrative; actual gating happens via Claude Code's permissions
# and the orchestrator's own discipline. This script logs and flags.

set -e
TOOL="$1"
ARGS="$2"

# T3 — block unconditionally
case "$ARGS" in
  *"rm -rf /"*|*"git push --force"*|*"DROP TABLE"*|*"DROP DATABASE"*)
    echo "[T3-BLOCK] Destructive command blocked: $ARGS" >&2
    exit 1
    ;;
esac

# T2 — flag, would require human approval
case "$ARGS" in
  *"pip install "*|*"npm install "*|*"alembic upgrade head"*)
    echo "[T2-FLAG] Approval-required command: $ARGS" >&2
    ;;
esac

exit 0
