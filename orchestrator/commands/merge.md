---
name: merge
description: Integrate approved worker output into the repo. Usage /merge path/to/report.md
---

# /merge

## What this does
After /review APPROVES, integrate the worker's changes safely.

## Steps
1. Confirm acceptance commands re-passed
2. Run `hooks/post-merge-format.sh` (format + lint)
3. Run full test suite for the affected wave: `make test-wave wave=N`
4. Update `plan/EXECUTION.md` task status to "merged"
5. Append to `CHANGELOG.md` under [Unreleased]
6. Log to `orchestrator/memory/MEMORY.md`
7. Optional: create git commit with conventional message

## Output
"Task <task> merged. Wave-N progress: X/K complete."
