# HALL OF SHAME

> Wave-40 Task 01 truth infrastructure. Every entry below is **verified from this
> repo's own history**, not hypothetical. They are the kill-evidence for FM-05
> (metric inconsistency) and FM-09 (false status). The guards that now stop each one
> are named in the `prevention:` line.

## 1. Fabricated wave-33 report
- **What:** A report claimed 5 test files with specific pass counts for `tests/wave-33`.
- **Root cause:** The numbers were hand-authored; `find tests/wave-33` showed the
  directory **did not exist**.
- **Impact:** A wave was reported done on tests that were never written. Audit trail
  poisoned — anyone trusting the report would believe coverage that didn't exist.
- **Fix:** Independent verification caught it; the report was corrected/retracted.
- **prevention:** `validate_execution.sh` + `results/metrics.json` — pass counts are
  parsed from real `pytest` output, never hand-typed (FM-05 guard).

## 2. Collected-count reported as passed-count
- **What:** A report claimed "562 passed"; 562 was the *collected* total
  (557 passed + 5 failed).
- **Root cause:** `pytest` prints "562 collected"; the author copied the collected
  number as the passed number, dropping the 5 failures.
- **Impact:** A 0.9% failure rate was erased from the headline; the system looked
  green when it was not.
- **Fix:** Re-parsed as "557 passed, 5 failed".
- **prevention:** `generate_metrics.sh` parses the explicit `X passed, Y failed`
  summary line; `validate_metrics.sh` flags any doc asserting a clean pass while the
  source shows failures (FM-09 guard).

## 3. FINAL-CLOSE sealed on a false green
- **What:** `work/reports/FINAL-CLOSE.report.md` declared the project **CLOSED** at
  "0 failed / 565 passed". An independent run produced `7 failed, 559 passed, 7 skipped`
  (5 real auth failures + 2 environmental Redis ones).
- **Root cause:** Protocol P05 (independent re-run before seal) was specified but
  **never executed**; the seal was written from memory/intent, not a live run.
- **Impact:** The repo was declared submission-ready on a false green. The 5 auth
  failures were real RBAC regressions, not environmental noise.
- **Fix:** Re-run surfaced the failures; seal re-opened pending fixes.
- **prevention:** `docs_sync.yml` runs `validate_metrics.sh` + `validate_execution.sh`
  on push to main; seals must reference `results/metrics.json`, which is generated, not
  authored (FM-09 guard).

## 4. Frontend coverage stated three ways
- **What:** Frontend statement coverage was reported as **65.86%** (wave-34 report),
  **~61%** (handoff verdict), and **65.02%** (independent run) — three numbers, one
  metric.
- **Root cause:** `vitest` **suppresses its coverage summary when any test fails**, so
  people copied whichever stale number was on screen instead of a regenerated one.
- **Impact:** The single most-quoted quality metric was non-reproducible; reviewers
  couldn't tell which figure was real.
- **Fix:** Established ONE generated source (`results/metrics.json`).
- **prevention:** `generate_metrics.sh` detects the vitest-failure case and records
  `coverage: null` + `coverage_unavailable_reason` — it **never** writes a stale or
  guessed number. Docs must reference the generated file (FM-05 guard).

## 5. HIERARCHY.md padded to defeat its own scope guard
- **What:** 28 artifact filenames (with duplicates) were pasted into `HIERARCHY.md`'s
  inventory so the FM-08 scope check would pass — instead of actually moving the
  artifacts out of the scope-bloated directory.
- **Root cause:** The scope guard counted inventory entries; padding the inventory
  satisfied the letter of the check while violating its intent.
- **Impact:** Scope creep was hidden; the guard became theater.
- **Fix:** Inventory trimmed; artifacts relocated.
- **prevention:** Scope checks now sample actual file paths, not declared inventory
  strings (FM-08 hardening).

## 6. Two agents in one worktree
- **What:** A duplicate paste launched two `opencode` processes in the same `prof-G`
  worktree simultaneously.
- **Root cause:** Worktree isolation assumes a single writer; a copy-paste error
  started a second agent against the same checkout.
- **Impact:** Interleaved writes corrupted intermediate state; non-deterministic
  results and lost edits.
- **Fix:** Killed the second process; re-ran serially.
- **prevention:** One writer per worktree is now an enforced session rule; concurrent
  agent spawns in the same worktree are rejected (FM-13 disjoint-writes guard).

## 7. `SQLAlchemy remote_side=["TaskComment.id"]`
- **What:** A string inside a list — `["TaskComment.id"]` — instead of the Column
  object, in a self-referential relationship `remote_side`.
- **Root cause:** Typo / string-vs-Column confusion; it passed when waves ran in
  isolation but **broke 103 tests only when waves were combined** (the relationship was
  finally imported/exercised together).
- **Impact:** 103 tests failed only in the integrated suite — a latent landmine that
  isolated runs never caught.
- **Fix:** Changed to `remote_side=[TaskComment.id]` (Column object).
- **prevention:** Full-suite integration run is now a mandatory gate (not just
  per-wave); `generate_metrics.sh` runs `tests/` wholesale so combined-regression
  landmines surface before seal.
