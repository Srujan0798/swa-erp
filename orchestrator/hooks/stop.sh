#!/bin/bash
# Runs at the end of an orchestrator session.

set -e
cd "$(dirname "$0")/../.."

echo "[stop] session ending"
echo "[stop] reminder: run /handoff if state changed significantly"
