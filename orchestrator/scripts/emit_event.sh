#!/usr/bin/env bash
# Append one event line to a JSONL session log.
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "usage: $0 <events.jsonl> <event> <json-payload>" >&2
  exit 2
fi

file="$1"
event="$2"
payload="$3"

if ! printf '%s' "$payload" | python3 -m json.tool >/dev/null 2>&1; then
  echo "invalid json payload" >&2
  exit 2
fi

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
session="$(basename "$file" .events.jsonl)"

python3 - <<'PY' "$file" "$ts" "$event" "$session" "$payload"
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
row = {
  "ts": sys.argv[2],
  "event": sys.argv[3],
  "session": sys.argv[4],
  "actor": "manual:emit_event",
  "payload": json.loads(sys.argv[5]),
}
path.parent.mkdir(parents=True, exist_ok=True)
with path.open("a", encoding="utf-8") as f:
  f.write(json.dumps(row, ensure_ascii=False) + "\n")
PY

printf 'ok: appended %s\n' "$file"
