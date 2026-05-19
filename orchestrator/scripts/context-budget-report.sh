#!/bin/bash
# Estimate token usage of always-loaded files.
set -e
cd "$(dirname "$0")/../.."

est_tokens() {
  # rough: 1 token ≈ 4 chars
  local bytes=$(wc -c < "$1" 2>/dev/null || echo 0)
  echo $((bytes / 4))
}

echo "=== Always-loaded context (per session) ==="
echo "CLAUDE.md:    $(est_tokens CLAUDE.md) tokens"
echo "HANDOFF.md:   $(est_tokens HANDOFF.md) tokens"
echo "HIERARCHY.md: $(est_tokens HIERARCHY.md) tokens"
TOTAL=$(($(est_tokens CLAUDE.md) + $(est_tokens HANDOFF.md) + $(est_tokens HIERARCHY.md)))
echo "TOTAL:        ~$TOTAL tokens"

if [ "$TOTAL" -gt 8000 ]; then
  echo "WARN: exceeds 8K kernel budget. Trim CLAUDE.md or move detail to core/."
fi
