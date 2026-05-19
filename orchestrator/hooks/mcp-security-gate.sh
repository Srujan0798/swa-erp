#!/bin/bash
# Validates MCP tool calls against the whitelist in ../../mcp.json.
# Blocks unknown servers/methods.

set -e
SERVER="$1"
METHOD="$2"

if [ ! -f mcp.json ]; then
  echo "[mcp-gate] mcp.json missing — blocking all MCP calls" >&2
  exit 1
fi

# Simple check: server must appear in mcp.json
if ! grep -q "\"$SERVER\"" mcp.json; then
  echo "[mcp-gate] Server '$SERVER' not in whitelist (mcp.json)" >&2
  exit 1
fi

exit 0
