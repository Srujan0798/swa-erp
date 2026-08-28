# Wave-44 Task 01 — Brain/Hands/Session durable layer + blast radius

**Status:** DONE — all acceptance criteria met.

## What was done

### 1. Session durable event log

Created the append-only JSONL session log scaffolding and documented the schema.

Files:
- `orchestrator/memory/session/INDEX.md`
- `orchestrator/memory/session/.gitkeep`
- `orchestrator/memory/session/wave-33.events.jsonl`

Schema: `ts`, `event`, `session`, `actor`, `payload`. Supported events:
`dispatch`, `tool_use`, `acceptance_run`, `review`, `merge`, `abandon`.

### 2. `orchestrator/scripts/emit_event.sh`

Append-only helper for emitting one event line into a session JSONL.
Validates payload JSON before appending.
Verified behavior: running twice on the same file grows the file and does not rewrite history.

### 3. `orchestrator/scripts/replay_session.sh`

Reconstructs readable resume context from a session JSONL file.
Produces a compact per-event summary including actor, event type, and key payload fields.

### 4. `orchestrator/core/blast-radius.md`

Defines concrete r0–r5 containment tiers grounded in real SWA-ERP examples:
- r0: read-only analysis
- r1: docs/reports only
- r2: tests only
- r3: app code behind green suite
- r4: migrations/auth/money paths — e.g. `Decimal(18,2)` money convention, RBAC role checks, Alembic heads
- r5: anything touching real data or production deploy — always human-confirmed

### 5. `workflows/*.json`

Declarative workflow definitions for project workflows that actually repeat:
- `workflows/new_wave.json`
- `workflows/bug_fix.json`
- `workflows/verify_and_merge.json`

Each references a state file under `orchestrator/memory/states/`.

### 6. Backfill: wave-33 reconstructed session

Reconstructed `orchestrator/memory/session/wave-33.events.jsonl` from wave-33 reports and commits.
Covers: initial dispatch, hung-run abandon, review/revise, acceptance rerun, successful redo dispatch,
tool-use evidence, acceptance evidence, merge commit `9cb2b22`, and final abandon for the killed opencode run.
Marked as reconstructed-after-the-fact.

## Acceptance criteria

- [x] `bash orchestrator/scripts/emit_event.sh` appends a valid line; verified twice on a temp file: line count went 1 -> 2 and JSON parse stayed valid
- [x] `bash orchestrator/scripts/replay_session.sh orchestrator/memory/session/wave-33.events.jsonl` output:
```
== replay: orchestrator/memory/session/wave-33.events.jsonl ==
== events: 10 ==

[2026-08-23T17:20:00Z] dispatch actor=orchestrator model=opencode/nemotron-3.5-lightning-free task_file=work/wave-33/01-backend-coverage.md
[2026-08-23T17:30:00Z] abandon actor=worker:opencode/nemotron-3.5-lightning-free reason=hung: zero CPU and zero file-mtime changes recovered=None
[2026-08-23T18:05:00Z] dispatch actor=orchestrator model=opencode/nemotron-3.5-lightning-free task_file=work/wave-33/01-backend-coverage.md
[2026-08-23T19:45:00Z] review actor=orchestrator verdict=revise reason=report claimed 562 passed / 66% without backing test files or passing evidence
[2026-08-23T20:00:00Z] acceptance_run actor=orchestrator result=ok
[2026-08-23T20:10:00Z] dispatch actor=orchestrator model=opencode/nemotron-3.5-lightning-free task_file=work/wave-33/02-backend-coverage-redo.md
[2026-08-23T21:05:00Z] tool_use actor=worker:opencode/nemotron-3.5-lightning-free tool=terminal cmd=python3 -m pytest tests/wave-33/ -q --cov=src/backend --cov-report=term
[2026-08-23T21:10:00Z] acceptance_run actor=worker:opencode/nemotron-3.5-lightning-free result=ok
[2026-08-23T21:12:00Z] merge actor=orchestrator commit=9cb2b22 branch=main
[2026-08-23T21:12:30Z] abandon actor=worker:opencode/nemotron-3.5-lightning-free reason=process killed after opencode run recovered=work/reports/wave-44/01-brain-hands-session.report.md
```
- [x] Every JSONL line parses: `python3 -c "import json,sys; [json.loads(l) for l in open('orchestrator/memory/session/wave-33.events.jsonl')]"` -> OK
- [x] `blast-radius.md` maps r0–r5 to concrete swa-erp examples, not generic prose
- [x] Each `workflows/*.json` validates as JSON

## Commits

1. `10dc214` wave-44: durable session layer + blast radius + workflows + wave-33 backfill
