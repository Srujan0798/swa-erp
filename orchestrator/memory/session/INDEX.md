# Session event log index

Location: `orchestrator/memory/session/<wave>-<task>.events.jsonl`

## Schema (one JSON object per line)

| field | type | meaning |
|---|---|---|
| `ts` | ISO-8601 string | Event timestamp (UTC preferred) |
| `event` | string | One of `dispatch`, `tool_use`, `acceptance_run`, `review`, `merge`, `abandon` |
| `session` | string | Logical session id (`<wave>-<task>` is typical) |
| `actor` | string | Who caused the event (`orchestrator`, `worker:<model>`, `human`) |
| `payload` | object | Event-specific data (free-form) |

## Examples by event type

- `dispatch`: `{ "actor": "orchestrator", "task_file": "work/wave-44/01-brain-hands-session.md", "model": "opencode/nemotron-3.5-lightning-free" }`
- `tool_use`: `{ "actor": "worker:opencode/nemotron-3.5-lightning-free", "tool": "terminal", "cmd": "bash orchestrator/scripts/emit_event.sh ..." }`
- `acceptance_run`: `{ "actor": "worker:opencode/nemotron-3.5-lightning-free", "cmd": "bash orchestrator/scripts/emit_event.sh ...", "result": "ok|fail", "stdout_tail": "..." }`
- `review`: `{ "actor": "orchestrator", "verdict": "approve|revise|reject", "reason": "..." }`
- `merge`: `{ "actor": "orchestrator", "commit": "abc123", "branch": "main" }`
- `abandon`: `{ "actor": "worker:opencode/nemotron-3.5-lightning-free", "reason": "oom/hang/manual/timeout", "recovered_path": null }`

## Invariants

- Append-only. Never rewrite history.
- Replay tool: `orchestrator/scripts/replay_session.sh <file>`
- Emit helper: `orchestrator/scripts/emit_event.sh <file> <event> <json-payload>`
