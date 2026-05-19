# How to Run This Project

## Open the orchestrator
Either:
- Open Claude Code in this directory (auto-loads `CLAUDE.md`), OR
- Open Kimi in this directory (auto-loads `KIMI.md`)

Both work the same way. Pick whichever is up.

## Start work
```text
/status              → see current state
/next                → ask orchestrator what to work on next
/plan wave-N         → decompose wave N into tasks (writes .specify/specs/wave-N/)
/dispatch wave-N     → write task files into work/wave-N/
```

## Dispatch to workers
Open OpenCode CLI windows (one per task you want to run in parallel).

In each window:
1. Paste contents of `work/WORKER_PROMPT.md`
2. Then paste contents of ONE task file from `work/wave-N/`
3. Worker executes, writes code to repo, writes report to `work/reports/wave-N/`

You can run 4–6 tasks in parallel (different OpenCode windows, different files).

## Review and merge
Back in the orchestrator (Claude Code or Kimi):
```text
/review work/reports/wave-N/0X-task.report.md
/merge  work/reports/wave-N/0X-task.report.md
```

The orchestrator runs the acceptance commands itself before approving.

## Ship a wave
When all tasks in a wave are merged:
```text
/ship wave-N
```
Runs integration tests, opens a PR, updates `plan/EXECUTION.md`, bumps `CHANGELOG.md`.

## Local dev (running the app)
```bash
make install      # python venv + node deps + db
make dev          # start backend (8000) + frontend (3000) + postgres + redis
make migrate name="add_client_table"  # create new Alembic migration
make migrate-up   # apply migrations
make test         # full test suite (unit + integration)
make test-e2e     # end-to-end via Playwright
make lint         # ruff + eslint
make format       # black + prettier
```

## Switching orchestrator
If Claude is down, open Kimi in the same directory. Read `HANDOFF.md`. Same workflow.

## Evolving the project
- New decisions → write ADR in `docs/decisions/0NNN-title.md`
- Superseded plans → move to `docs/historical/`
- Superseded prompts → move to `prompts/archive/`
- Anything no longer in flow but worth keeping → `attic/`
- **Never delete. Always archive.**
