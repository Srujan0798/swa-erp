# Review Protocol — How to review worker reports

## Step 1 — Read the report
Open `work/reports/wave-N/0X-task.report.md`. Look for:
- Result: DONE / BLOCKED / PARTIAL / FAILED
- Acceptance checks list — did the worker run them?
- Decisions made — flag any that violate constitution
- Issues / blockers — does it need re-dispatching?

## Step 2 — Run the acceptance commands YOURSELF
Don't trust the worker's "passed" claim. Boris's rule.

```bash
# For backend tasks:
pytest tests/wave-N/test_<task>.py -v
make lint
make type-check

# For frontend tasks:
cd src/frontend && pnpm test
cd src/frontend && pnpm build

# For E2E:
pytest tests/e2e/test_<flow>.py -v
```

If anything fails → REVISE, not APPROVE.

## Step 3 — Spawn `verifier` sub-agent
For non-trivial tasks, spawn the `verifier` agent in a separate context. The verifier:
- Reads the code with no bias toward what was just written
- Checks for hidden assumptions, missing edge cases
- Returns APPROVED or REVISE with specifics

## Step 4 — Cross-check with spec
Open `.specify/specs/wave-N/spec.md` and `.specify/specs/wave-N/contracts/test_acceptance.py`. Did the worker hit every user story?

## Step 5 — Style + path-scoped rules
Check files against `orchestrator/rules/{python,typescript,security,docs}.md`. Mismatches → REVISE.

## Decision
- **APPROVE** → run `/merge`
- **REVISE** → rewrite the task file in `work/wave-N/0X-*.md` with specific corrections, redispatch
- **REJECT** → run `/rollback`, move worker output to `attic/rejected-task-N-task-M/`, re-plan
