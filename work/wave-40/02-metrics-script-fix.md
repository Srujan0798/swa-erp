# Wave-40 Task 02 — Fix the broken generate_metrics.sh + restructure EXECUTION.md's commit column

Wave-40's first pass landed the parts that were genuinely correct (HALL_OF_SHAME.md, BACKLOG.md, both validator scripts). Two real, specific defects remain — not vague, both precisely diagnosed by the orchestrator.

## Defect 1: `scripts/generate_metrics.sh` silently produces nothing

**Symptom:** running it takes ~3 minutes (it runs the full backend `pytest` + frontend `vitest` suites internally — that's real and expected), exits with code 0, but `results/metrics.json` is never created and no JSON is printed to stdout.

**What's suspicious:** the script has `set -euo pipefail` at line 4, which should make any real failure inside it propagate as a non-zero exit — but it doesn't. This means either:
- a command inside a `$(...)` substitution is failing but its exit code is being swallowed (command substitution doesn't always propagate under `pipefail` the way people expect), or
- one of the intermediate variables (`$BACKEND_OBJECT`, `$FRONTEND_OBJECT`) ends up empty/malformed, and the final `python3 -c "..." ` heredoc's `json.loads('''$BACKEND_OBJECT''')` call raises — check whether that specific `python3 -c` block's own exit code is actually reaching the shell, or is itself being absorbed somewhere.

**Do this:**
1. Run the script with `bash -x scripts/generate_metrics.sh 2>&1 | tail -100` to see exactly which line stops producing expected output.
2. Find where `$BACKEND_OBJECT` and `$FRONTEND_OBJECT` are actually built (grep the script for how it parses pytest/vitest text output) — print them before the final JSON assembly to check they're non-empty valid JSON.
3. Fix the actual bug. Do not add a workaround that hides a future silent failure — this script's entire purpose is to prevent silent failures (FM-05/FM-09), so it must fail LOUD if it can't produce a real result.

## Defect 2: `plan/EXECUTION.md` has no dedicated commit-hash column

**Symptom:** `validate_execution.sh` reports 23 violations for "SHIPPED with no commit hash," but on inspection most of those rows DO cite a real hash — it's embedded in prose in the `Notes` column, because the table's actual header is:
```
| Wave | Name | Status | Tasks | Notes |
```
There is no `Commit` column at all, contradicting `orchestrator/core/12-factor.md` §4.12's format (`| Wave | Name | Status | Tasks | Commit | Notes |`).

**Do this:**
1. Add a `Commit` column to the table header.
2. For each of the 43 rows: extract the commit hash currently sitting in prose in `Notes` (e.g. row 4: "bulk commit `ed71fac`") and move it into the new `Commit` column, leaving `Notes` for actual prose.
3. For any row that genuinely has no commit hash anywhere (verify with `git log --oneline | grep -i "wave-N"` before concluding this), leave `Commit` as `—` and say so honestly rather than inventing one.
4. Re-run `validate_execution.sh` until the SHIPPED-without-hash count is 0 or every remaining flag is a genuine, explained gap.

## Then, only after both are fixed and verified
- Commit `scripts/generate_metrics.sh` (fixed) and `results/metrics.json` (real generated output)
- Commit the corrected `plan/EXECUTION.md`
- Re-add the `Makefile` `metrics`/`verify-truth` targets and `.github/workflows/docs_sync.yml` NOW that the script actually works (both already exist in `git show 06e3c3b:Makefile` / were prepared in the first pass — check the earlier w40 worktree if it still exists, otherwise recreate per `work/wave-40/01-truth-infrastructure.md`)

## Acceptance criteria
- [ ] `bash scripts/generate_metrics.sh` produces a real `results/metrics.json` with real parsed numbers — paste the file
- [ ] `bash orchestrator/scripts/validate_metrics.sh` passes
- [ ] `bash orchestrator/scripts/validate_execution.sh` reports 0 unexplained violations
- [ ] `make verify` (with the Makefile change re-added) runs end to end without failing on the metrics step
- [ ] Full backend suite still green (this touches no application code, but confirm)

## Deliver
`work/reports/wave-40/02-metrics-script-fix.report.md`. Commit before writing it — and commit each of the 2 defects separately as you fix them, not as one giant commit at the end.

## Constraints
- Time budget: 90 min
- This is a debugging task — use the `systematic-debugging` skill if available
- Do not touch HALL_OF_SHAME.md, BACKLOG.md, or the 2 validator scripts — they're already correct and merged
