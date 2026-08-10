# swa-erp Phase 2 dispatch — the actual protocol, written out plainly

This is what's being run right now, so you can hand identical instructions to another agent
instead of trying to follow it live. Copy the sections below as-is.

## Why worktrees, not just "open 5 terminals in the same folder"

If two agents edit the same repo folder at the same time, one can silently overwrite the other's
uncommitted changes — no error, no warning, just lost work. Wave-22 and wave-24 both touch
`api/tasks.py`; wave-27's lint pass touches most of the backend. So each wave runs in its own
**git worktree** — a separate folder checked out on its own branch, physically isolated. They
can't collide. Conflicts, if any, show up later at merge time, visibly, where they're safe to
resolve.

## Step 1 — create one worktree per wave (run once, from the main repo)

```bash
cd /Users/srujansai/Desktop/swa-erp
mkdir -p /Users/srujansai/Desktop/swa-erp-worktrees
for w in 22 23 24 27 28; do
  git worktree add -b "wave-$w-work" "/Users/srujansai/Desktop/swa-erp-worktrees/wave-$w" main
done
```

## Step 2 — launch one OpenCode process per worktree, each in its own terminal

**Check memory before launching anything new** — this machine runs out of RAM fast with several
OpenCode instances open at once:
```bash
top -l 1 -n 0 | grep PhysMem
```
If "unused" is under ~1GB, wait — don't launch more, one will get silently killed (this already
happened once to wave-27).

For each wave, open a terminal, `cd` into its worktree, and run:
```bash
cd /Users/srujansai/Desktop/swa-erp-worktrees/wave-<N>
opencode run --auto -m "<model>" "Read work/WORKER_PROMPT.md, then read and execute work/wave-<N>/01-<taskname>.md. Follow it exactly — it's self-contained. Write your report to the path specified inside it, then stop."
```

**Model assignment used (OpenCode Zen free tier):**
| Wave | Task | Model |
|---|---|---|
| 22 | Critical RBAC/auth gaps | `opencode/north-mini-code-free` |
| 23 | Correctness bugs | `opencode/deepseek-v4-flash-free` |
| 24 | Dead code + UI wiring | `opencode/longcat-2.0-free` (first choice `nemotron-3-ultra-free` hit a provider capacity error — swap models if you see `502 ResourceExhausted`) |
| 27 | Security findings + lint | `opencode/north-mini-code-free` |
| 28 | Doc consolidation | `opencode/deepseek-v4-flash-free` |

Free-model fallback order if one errors out: `north-mini-code-free` → `deepseek-v4-flash-free`
→ `longcat-2.0-free` → `mimo-v2.5-free` → `ling-3.0-flash-free` → `laguna-s-2.1-free`.

**Pipe output to a log so progress can be checked without watching the terminal:**
```bash
... | tee /tmp/wave-<N>-opencode.log
```

## Step 3 — check on progress

```bash
ps aux | grep "[o]pencode run"                    # which are still running
tail -20 /tmp/wave-<N>-opencode.log                # what it's doing / any error
ls /Users/srujansai/Desktop/swa-erp-worktrees/wave-<N>/work/reports/wave-<N>/   # done when this has a file
```

## Step 4 — merge a finished wave back into main (do this the moment its report appears)

```bash
cd /Users/srujansai/Desktop/swa-erp

# 1. Read the report first — confirm it actually says DONE with real evidence, not just claimed
cat /Users/srujansai/Desktop/swa-erp-worktrees/wave-<N>/work/reports/wave-<N>/*.report.md

# 2. Merge
git merge wave-<N>-work --no-ff

# 3. Verify — this is not optional. Every wave gets tested before it's considered merged.
python3 -m pytest tests/ -q
# Must show 344+ passed, 0 failed. If it regresses, investigate — do not leave a broken merge.

# 4. Push
git push origin main

# 5. Clean up
git worktree remove /Users/srujansai/Desktop/swa-erp-worktrees/wave-<N>
```

**A pre-commit hook (Adaptoid preflight) runs automatically on every commit and can fail the
commit** — that's intentional, it's this project's own quality gate. Don't bypass it with
`--no-verify`. If it fails, fix what it flags (it tells you exactly what's wrong) and recommit.

## Dependency order — do not violate this

```
Round 1 (parallel, already running): 22, 23, 24, 27, 28
Round 2: 29  — only after 27 AND 28 are merged (29 fixes doc claims about what 27/28 changed)
Round 3: 30  — only after 22, 23, 24, 27, 28, 29 are ALL merged (final verification + release)
```
Wave-29 and wave-30 briefs already exist at `work/wave-29/01-stale-claim-fixes.md` and
`work/wave-30/01-final-release-and-submission.md` — dispatch them with the exact same
worktree-per-wave pattern once their dependencies clear.

## Live status as of this writing

- **Memory:** critically low (78MB unused of ~23GB) — do not add more concurrent processes right now
- **Running:** waves 22, 23, 24, 28 — all in progress, no reports yet
- **Needs relaunch:** wave-27 — its process died mid-run (memory pressure), no report was
  written. Its worktree has uncommitted partial changes touching more files than its brief
  scoped (likely legitimate `ruff --fix` output across the backend, but **diff each file against
  `main` and confirm they're style-only before trusting them**, don't merge blind). Relaunch it
  fresh once memory frees up, or resume its session with `opencode session list` in that
  worktree to find its session ID and continue with `opencode run -c -s <session_id> ...`.
- **Not started:** 29, 30

## If you want ONE prompt to hand another agent to run this whole thing autonomously

```
Follow work/wave-26/DISPATCH-GUIDE.md exactly, starting from wherever "Live status" says
things currently stand. Check memory before every launch. Merge each wave into main the
moment its report appears, verifying with the full pytest suite before pushing. Respect the
dependency order (29 needs 27+28 merged; 30 needs everything merged). Keep going, dispatching
the next wave the moment its dependencies clear, until wave-30 reports either READY TO SUBMIT
or a clear list of blockers. Update the "Live status" section of this file every time something
changes so progress stays visible to anyone reading it cold.
```
