# Contributing

## Workflow

This project uses the dual-tier agentic flow:
- **Plan/review** via Claude Code or Kimi (the orchestrator)
- **Execute** via OpenCode CLI workers (parallel windows)

See `HOW_TO_RUN.md` for the full workflow.

## To add a feature

1. Open the orchestrator: `claude` (or Kimi equivalent) in the project root
2. Run `/next` to see what wave is active
3. Run `/plan wave-N` if starting a new wave
4. Run `/dispatch wave-N` to write task files
5. Open OpenCode CLI windows (one per task), paste task files, execute
6. Workers write reports → orchestrator reviews → `/merge`

## Code style

- Python: black + ruff + mypy strict (`pyproject.toml`)
- TypeScript: TS strict + eslint + prettier
- Tests required for any new code; coverage ≥ 75% on services
- No new dependencies without an ADR in `docs/decisions/`

## Commits

- Conventional Commits format: `feat(wave-2): add PDF ingestion`
- Reference wave/task in scope
- Co-authored-by lines welcome but not required

## PRs

- Reference the wave + task brief that drove the change
- Acceptance commands must pass in CI
- At least one human reviewer approves before merge to main
- Auto-format on commit (pre-commit hook enabled)

## Don't do this

- **Don't delete files. Archive to `attic/`.** History matters.
- **Don't write feature code in the orchestrator session.** That's worker work.
- **Don't bypass acceptance commands.** They are the contract.
- **Don't update CLAUDE.md to "remember" things that should be in `core/`.** CLAUDE.md stays short.
- **Don't add files that aren't in the task brief.** Scope guard.
