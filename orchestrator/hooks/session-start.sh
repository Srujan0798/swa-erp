#!/bin/bash
# Runs at the start of an orchestrator session.
# Loads current project state so the orchestrator can resume quickly.

set -e
cd "$(dirname "$0")/../.."

echo "[session-start] swa-erp orchestrator session"
echo "[session-start] reading HANDOFF.md..."
head -30 HANDOFF.md 2>/dev/null || echo "  HANDOFF.md missing"
echo ""
echo "[session-start] active wave:"
grep -E "^\*\*Active wave:\*\*" HANDOFF.md 2>/dev/null || echo "  unknown"
echo ""
echo "[session-start] pending reviews:"
ls work/reports/wave-*/*.report.md 2>/dev/null | head -10 || echo "  none"
