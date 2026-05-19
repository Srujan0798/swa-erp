#!/bin/bash
# Validate the orchestrator's structure is intact.
set -e
cd "$(dirname "$0")/../.."

REQUIRED=(
  "CLAUDE.md"
  "KIMI.md"
  "HANDOFF.md"
  "HIERARCHY.md"
  "README.md"
  "HOW_TO_RUN.md"
  "OS_SETUP.md"
  "plan/PRD.md"
  "plan/ARCHITECTURE.md"
  "plan/EXECUTION.md"
  ".specify/memory/constitution.md"
  "orchestrator/ROLE.md"
  "work/TASK_TEMPLATE.md"
  "work/REPORT_TEMPLATE.md"
  "work/WORKER_PROMPT.md"
)

MISSING=0
for f in "${REQUIRED[@]}"; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f"
    MISSING=$((MISSING+1))
  fi
done

if [ "$MISSING" -eq 0 ]; then
  echo "OK: All required files present."
else
  echo "FAIL: $MISSING required files missing."
  exit 1
fi
