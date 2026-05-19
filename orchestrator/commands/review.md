---
name: review
description: Review a worker report. Approve, revise, or reject. Usage /review path/to/report.md
---

# /review

## What this does
Reads a worker report, runs acceptance commands, decides APPROVE / REVISE / REJECT.

## Steps
1. Load report and matching task file
2. For each acceptance criterion: RUN the command via Bash
3. Cross-check against `.specify/specs/wave-N/plan.md`
4. Check files against `orchestrator/rules/`
5. Spawn `agents/verifier.md` for independent review
6. Decide:
   - APPROVE → run /merge
   - REVISE → rewrite task file with corrections, redispatch
   - REJECT → /rollback, move output to attic/

## Notes
Never trust the worker's "passed" claim. Always re-run the acceptance commands yourself.
