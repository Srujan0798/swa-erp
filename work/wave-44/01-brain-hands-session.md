# Wave-44 Task 01 — Brain/Hands/Session durable layer + blast radius

Adaptoid §1.6 (Anthropic Apr 2026 "Scaling Managed Agents") + §4.25 + §4.26. This repo has **lost work three times** to crashed or hung agent sessions. The durable event log is the specific fix for that.

## The evidence this wave exists
- A wave-36 report was written but never committed; the worktree was removed and the report was gone permanently.
- Sessions hung repeatedly with no record of what they had done, forcing full re-derivation each time.
- Session state lives only in `git log` today, which captures commits but not decisions, tool calls, or why something was abandoned.

Per §1.6 the three failure modes are: Brain crash (recoverable), Hand crash (recoverable), **Session lost (fatal)**. Right now this project has no Session layer at all.

## Files you own (touch nothing else)
- `orchestrator/memory/session/INDEX.md` + `.gitkeep`
- `orchestrator/memory/states/.gitkeep` + `README.md`
- `orchestrator/scripts/replay_session.sh`
- `orchestrator/scripts/emit_event.sh`
- `orchestrator/core/blast-radius.md`
- `workflows/*.json`

## The work

### 1. Event log format (§4.25)
`orchestrator/memory/session/<wave>-<task>.events.jsonl` — append-only JSONL. One event per line: timestamp, event type (`dispatch`, `tool_use`, `acceptance_run`, `review`, `merge`, `abandon`), and payload. Document the schema in `INDEX.md`.

### 2. `emit_event.sh`
Tiny helper a worker or the orchestrator calls to append an event. Must be append-only and never rewrite history.

### 3. `replay_session.sh`
Reconstructs readable context from an events file so a cold session can resume: what was attempted, what passed, what was abandoned and why. This is the `wake(sessionId)` primitive.

### 4. `orchestrator/core/blast-radius.md` (§4.26)
Define r0–r5 containment tiers for THIS project concretely. Ground them in real examples from this repo:
- **r0** read-only analysis (safe, auto)
- **r1** docs/reports only (auto)
- **r2** tests only
- **r3** application code behind a green suite
- **r4** migrations / auth / money paths — e.g. the `Decimal(18,2)` money convention, the RBAC role checks, Alembic heads
- **r5** anything touching the client's real data or a production deploy — always human-confirmed
Map each tier to what an agent may do without asking.

### 5. `workflows/*.json` (§4.11)
Declarative definitions for the workflows this project actually repeats: `new_wave.json`, `bug_fix.json`, `verify_and_merge.json`. Each references its state file under `orchestrator/memory/states/`.

### 6. Backfill one real session
Reconstruct an events file for a wave that already shipped (wave-33 or wave-37 — read their reports and commits) so `replay_session.sh` has real data to prove against. Mark it clearly as reconstructed-after-the-fact, not live-captured.

## Acceptance criteria
- [ ] `bash orchestrator/scripts/emit_event.sh` appends a valid line; run it twice and show the file grows and nothing is rewritten
- [ ] `bash orchestrator/scripts/replay_session.sh <file>` prints usable resume context — paste it
- [ ] Every JSONL line parses: `python3 -c "import json,sys; [json.loads(l) for l in open(f)]"` — paste result
- [ ] `blast-radius.md` maps r0–r5 to concrete swa-erp examples, not generic prose
- [ ] Each `workflows/*.json` validates as JSON

## Deliver
`work/reports/wave-44/01-brain-hands-session.report.md`. Commit before writing it.

## Constraints
- Time budget: 150 min · commit per component
- Zero application-code changes
