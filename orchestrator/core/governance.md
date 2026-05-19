# Governance — Risk Tiering (T0–T3)

Per kmshihab Claude OS pattern.

## Tiers

| Tier | What it covers | Gate |
|---|---|---|
| **T0 — Auto** | Read files, run tests, lint, format | Execute immediately, no log needed |
| **T1 — Log + proceed** | Write to src/, modify tests, run migrations on dev DB | Log to MEMORY.md, proceed |
| **T2 — Await approval** | Add deps (pip/npm), change CI workflows, modify migrations applied in main, change auth model | Pause; ask human via `interviewer` |
| **T3 — Block** | `rm -rf`, `git push --force` on main, drop tables, delete branches | Block unconditionally |

## Enforcement
- `hooks/pre-tool-use.sh` checks every tool call
- T3 actions return error immediately
- T2 actions trigger user confirmation via interviewer agent

## Examples
- `pytest tests/` → T0
- `git add src/backend/services/auth.py` → T1
- `pip install some-new-package` → T2 (needs ADR)
- `git push --force-with-lease` → T3 unless explicitly authorized for current branch
