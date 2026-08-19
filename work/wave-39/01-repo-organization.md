# Wave-39 Task 01 — Repo organization: make the project *legible*, not just built

## Why this wave exists

The engineering is real. The **organization is not.** A professional evaluator opening this repo
sees 59 top-level entries, 28 of them raw load-test CSVs; a `HIERARCHY.md` that has been padded
with those same 28 filenames (with duplicates) to make a scope-check pass; 39 wave folders with
no indication which are live vs. history; and 9 competing top-level orchestration docs.

Nothing here is *wrong* — it's the exhaust of 38 waves of real work. But it reads as sprawl, and
sprawl is what the reviewer judges. **This wave makes the structure match the quality of the
work.**

## Verified current state (2026-08-19, commit `bfd2c54`)

| Problem | Evidence |
|---|---|
| 28 load-test artifacts tracked at repo root | `git ls-files \| grep -c '^load-test'` → 28 |
| They are NOT gitignored | `.gitignore` has `coverage/`, `test-results/` but no `load-test*` |
| `HIERARCHY.md` padded to hide them | lines 70-102 list all 28 in "Directory inventory", `202748_*` entries **duplicated** |
| `HIERARCHY.md` lists directories that don't exist | `playwright-report/`, `test-results/` — neither present |
| Wave-36's report was never committed | `work/reports/wave-36/` does not exist (code merged, report lost) |
| 39 wave folders, no live/archived distinction | `work/wave-1/` … `work/wave-38/` all flat |
| `docs/historical/` is 349 of 367 doc files | archive dwarfs live docs, no index |

## The work

### 1. Load-test artifacts — move, don't delete
28 files (`load-test-report-*.html`, `load-test-results-*.csv`) at repo root are **real evidence**
backing `docs/PERFORMANCE.md` — do not delete them. Move to `docs/performance-runs/`:
- `git mv` them (preserve history) into `docs/performance-runs/`
- Add `docs/performance-runs/README.md`: which run is which, what concurrency level, which one
  `docs/PERFORMANCE.md` cites, and that the early `200408` run's 28.6% failure rate was a
  since-fixed bug, not a load limit
- Update every reference in `docs/PERFORMANCE.md` and
  `work/reports/wave-35/01-performance-load-validation.report.md` to the new paths
- Add `load-test-report-*.html` and `load-test-results-*` to `.gitignore` so *future* runs don't
  land at root again

### 2. `HIERARCHY.md` — restore it as a real map
It is currently gamed: 28 artifact filenames were appended to the inventory so the FM-08 scope
guard would pass, rather than the artifacts being put somewhere sensible. That is exactly the
"make the check pass instead of fixing the thing" pattern this project has rejected elsewhere.
- Remove all 28 load-test lines (including the duplicated `202748_*` block, lines ~93-102)
- Remove `playwright-report/` and `test-results/` — they don't exist (they're gitignored build
  output; note that in a line rather than listing them as real dirs)
- Fix the broken table: lines 33-34 (`.github/workflows/`, `.claude/`) sit *below* a prose
  paragraph, orphaned from the table they belong to — move them back into the table
- Add the directories that are real but missing from the map: `backups/`, `uploads/`,
  `resources/`, `node_modules/`
- Verify: every top-level entry in `ls -1` appears in the inventory, and every inventory entry
  actually exists. State in the report that you checked both directions.

### 3. Wave folders — separate live from history
39 wave folders with no signal about which matter. Do **not** delete any (project rule: archive,
never delete).
- Create `work/ARCHIVE.md` — a table of waves 1-31: number, one-line purpose, status, link to
  its brief and report. This is the index that makes the history navigable instead of noise.
- Create `work/ACTIVE.md` — waves 33, 34, 36 (in-flight), 37, 38 (queued), with their dependency
  order and current status.
- Leave the folders where they are (moving them breaks every existing cross-reference in reports
  and docs). The two index files are what makes them legible.

### 4. `docs/historical/` — add an index
349 files, no map. Add `docs/historical/README.md` grouping them by what they are (superseded
meeting notes, archived wave specs, superseded briefs, old steering docs) and stating plainly:
"this is frozen archive, see `docs/` for live documentation." One paragraph per group, not per
file.

### 5. Top-level docs — one front door
9 top-level `.md` files compete to be the entry point: `README`, `MASTER-FLOW`, `CLAUDE`, `KIMI`,
`HANDOFF`, `HIERARCHY`, `HOW_TO_RUN`, `CHANGELOG`, `CONTRIBUTING`. Don't delete or merge them —
several are load-bearing (`CLAUDE.md`/`KIMI.md` are agent kernels, `HIERARCHY.md` is checked by a
hook). Instead:
- `README.md` gets a **"Where to look"** table near the top: one row per top-level doc, one line
  on who it's for and when to read it. A reader should never have to guess which of 9 files to
  open.
- Every one of those 9 files gets a one-line header stating its role and linking back to
  `README.md`. No orphans.

### 6. Reconcile `docs/PROJECT_HISTORY.md` and `CHANGELOG.md`
Both claim to record what happened. Check whether they contradict each other or the git log
(this project has a documented history of exactly that drift). If they overlap, make one
authoritative and have the other point to it. Correct, don't silently rewrite — annotate what
changed.

## Files you must NOT touch
- `src/`, `tests/` — no code changes in this wave at all
- `docs/historical/**` file *contents* — add the README index, change nothing inside
- `attic/` — frozen
- Any `work/reports/**` report body — you may fix broken *paths* inside them (§1), nothing else

## Acceptance criteria
- [ ] `ls -1 | wc -l` at repo root drops from 59 to **≤31** — paste before/after
- [ ] `git ls-files | grep -c '^load-test'` → **0**, and the files exist under
      `docs/performance-runs/` — paste both
- [ ] `git log --follow docs/performance-runs/<one-file>` shows pre-move history (proves `git mv`,
      not delete+recreate)
- [ ] Every `ls -1` top-level entry appears in `HIERARCHY.md`; every `HIERARCHY.md` inventory
      entry exists on disk — **state that you verified both directions and how**
- [ ] `work/ARCHIVE.md` and `work/ACTIVE.md` exist; every wave 1-38 appears in exactly one
- [ ] `README.md` has the "Where to look" table covering all 9 top-level docs
- [ ] No broken markdown links introduced: run the repo's own checker
      (`bash ~/Desktop/Adaptoid-OS/validators/preflight.sh` runs `check_references.sh`) and paste
      the FM-03 result
- [ ] Full test suite unchanged — this wave touches zero code. Paste
      `python3 -m pytest tests/ -q` output showing the same counts as before you started.

## Deliver
Report → `work/reports/wave-39/01-repo-organization.report.md`: before/after root listing, what
moved where, what you found that this brief didn't anticipate, and anything you chose *not* to do
with the reason. Commit before writing the report.

## Constraints
- Time budget: 120 min
- **Archive, never delete** — this is a standing project rule
- Use `git mv` for every move so history survives
- Commit in logical chunks (artifacts move, then HIERARCHY, then indexes) — not one giant commit
- Allowed: file edit, git, pytest, bash
