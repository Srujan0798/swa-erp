#!/bin/bash
# Runs after the orchestrator /merges worker output.

set -e
cd "$(dirname "$0")/../.."

echo "[post-merge] formatting backend"
ruff check --fix src/backend/ || true
black src/backend/ || true

echo "[post-merge] formatting frontend"
if [ -d src/frontend ]; then
  (cd src/frontend && npx prettier --write src/ 2>/dev/null || true)
fi

echo "[post-merge] running smoke tests"
pytest tests/unit -x -q 2>/dev/null || echo "[post-merge] WARNING: unit smoke failed"

echo "[post-merge] done"
