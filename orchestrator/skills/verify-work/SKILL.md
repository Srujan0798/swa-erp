---
name: verify-work
description: Boris's #1 rule. Run executable acceptance criteria yourself, never trust worker's claim.
---

# verify-work

## The rule
"Give Claude a way to verify its work" — Boris Cherny.
For the orchestrator: NEVER approve a worker report without running its acceptance commands yourself.

## What counts as verification
- Run tests, see green
- Hit an API, see expected response
- Open a page, see expected UI (use Playwright + screenshot)
- Query a DB, see expected rows
- Run a script, see expected output

## What does NOT count
- "Worker said it passed" → no
- "Code looks right" → no
- "Tests are written" → no, did you run them?

## After verification
- Document evidence in your review notes (test output snippet, screenshot path, etc.)
- If verification fails → REVISE the task, don't argue with the worker
