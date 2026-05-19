---
name: merge-work
description: Safely integrate approved worker output into the repo. Runs hooks, formats, tests, updates state.
---

# merge-work

## Steps
1. Confirm /review APPROVED
2. Run `orchestrator/hooks/post-merge-format.sh`
3. Run full wave test suite: `pytest tests/wave-N/ -v`
4. Run lint + type check: `make lint && make type-check`
5. Update `plan/EXECUTION.md` task status → "merged"
6. Append entry to `CHANGELOG.md` [Unreleased]
7. Log to `orchestrator/memory/MEMORY.md`
8. Optional git commit with conventional message

## Bail-out conditions
- Tests fail after merge → STOP, revert, mark as REVISE
- Lint fails → STOP, ask worker to fix or fix yourself if trivial
- Migration conflict → STOP, escalate to user via interviewer
