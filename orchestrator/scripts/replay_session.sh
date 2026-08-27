#!/usr/bin/env bash
# Reconstruct readable resume context from a session JSONL file.
# Usage: replay_session.sh <events.jsonl>
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <events.jsonl>" >&2
  exit 2
fi

file="$1"

if [ ! -f "$file" ]; then
  echo "missing: $file" >&2
  exit 1
fi

python3 - <<'PY' "$file"
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
print(f"== replay: {path} ==")
print(f"== events: {sum(1 for _ in path.open())} ==")
print()
for line in path.open(encoding="utf-8"):
  line = line.strip()
  if not line:
    continue
  e = json.loads(line)
  ts = e.get("ts", "?")
  event = e.get("event", "?")
  actor = e.get("actor", "?")
  payload = e.get("payload", {})
  tail = ""
  if event == "tool_use":
    tail = f"tool={payload.get('tool','?')} cmd={payload.get('cmd','?')}"
  elif event == "acceptance_run":
    tail = f"result={payload.get('result','?')}"
  elif event == "review":
    tail = f"verdict={payload.get('verdict','?')} reason={payload.get('reason','')}"
  elif event == "merge":
    tail = f"commit={payload.get('commit','?')} branch={payload.get('branch','?')}"
  elif event == "abandon":
    tail = f"reason={payload.get('reason','?')} recovered={payload.get('recovered_path')}"
  elif event == "dispatch":
    tail = f"model={payload.get('model','?')} task_file={payload.get('task_file','?')}"
  print(f"[{ts}] {event} actor={actor} {tail}".rstrip())
PY
