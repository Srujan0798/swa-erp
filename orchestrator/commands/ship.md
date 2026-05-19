---
name: ship
description: Close a wave end-to-end. Usage /ship wave-N
---

# /ship

## What this does
After all tasks in a wave are merged, run the final integration + PR.

## Steps
1. Verify all tasks marked merged in `plan/EXECUTION.md`
2. Run full acceptance suite: `pytest .specify/specs/wave-N/contracts/`
3. Run E2E tests for this wave
4. Run perf budget tests
5. Bump version in `pyproject.toml` and `package.json`
6. Update `CHANGELOG.md` from [Unreleased] to [vX.Y.Z]
7. Update `HANDOFF.md` "Active wave" to wave-N+1
8. Create git tag `wave-N-complete`
9. Open PR from current branch to main with full changelog

## Output
"Wave N shipped. PR opened. Active wave is now wave-N+1."
