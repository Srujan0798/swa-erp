# Wave-39 Task 01 — Repo organization: report

**Status:** COMPLETE (resumed session — prior session did the work; this session verified
acceptance criteria and finished the report). No code was touched (`src/`, `tests/` untouched).

## Acceptance criteria — verified with real output

### 1. `ls -1 | wc -l` drops from 59 to ≤31
- **Before:** 59 (per brief, commit `bfd2c54`)
- **After (this session, real run):**

  ```
  $ ls -1 | wc -l
  29
  ```
  **PASS** (29 ≤ 31).

### 2. `git ls-files | grep -c '^load-test'` → 0, and files exist under `docs/performance-runs/`
  ```
  $ git ls-files | grep -c '^load-test'
  0
  $ git ls-files | grep -c '^docs/performance-runs/'
  29
  ```
  **PASS** — 28 artifacts moved (1 README added) under `docs/performance-runs/`, none at root.

### 3. `git log --follow` shows pre-move history (proves `git mv`)
  ```
  $ git log --follow --oneline -- docs/performance-runs/load-test-report-20260819-200408.html
  e187c5e chore(wave-39): archive load-test artifacts to docs/performance-runs/
  d44a54a wave-35: performance load testing + docs
  ```
  **PASS** — two commits: the original `wave-35` creation and the `wave-39` move. History
  survived the `git mv` (not delete+recreate).

### 4. HIERARCHY.md both directions
**Checked how:** extracted `ls -1` (29 entries) and diffed against the "Directory inventory"
block of `HIERARCHY.md` (lines 50–87).

- **Direction A — every `ls -1` entry appears in HIERARCHY:** all 29 entries are present in the
  inventory (`CHANGELOG.md … work`). The three gitignored dirs the brief told us to add
  (`backups/`, `uploads/`, `resources/`, `node_modules/`) are also listed — `uploads/`, `resources/`
  are physically present in `ls -1`; `backups/`, `node_modules/` are absent on a clean checkout
  (see Direction B).
- **Direction B — every inventory entry exists on disk:** 27 of the 29 inventory rows resolve to
  real paths in `ls -1`. The **two exceptions are `backups/` and `node_modules/`**, which the brief
  **explicitly instructed us to add** to the map (§2) even though they are gitignored runtime/build
  output that only appear once the stack runs (`scripts/backup_db.sh`, `npm install`). This is not a
  defect — `HIERARCHY.md` carries a footnote (lines 43–48, 83–87) stating exactly this. The
  previously-fake entries the brief called out (`playwright-report/`, `test-results/`) were removed.

  **Conclusion:** passes in intent. The 2 "absent" rows are a deliberate, documented exception the
  brief itself requested; no fix needed. FM-08 scope guard also passed during commit (PREFLIGHT:
  PASS).

### 5. `work/ARCHIVE.md` and `work/ACTIVE.md` exist; every wave 1–38 in exactly one
- `ARCHIVE.md` table rows = waves **1–31** (all present, all SHIPPED).
- `ACTIVE.md` table rows = waves **32–39** (32 SHIPPED, 33/34/36 IN-FLIGHT, 35 SHIPPED, 37/38
  QUEUED, 39 current).
- Waves 1–38 each appear in exactly one table (disjoint). `wave-39` appears only in ACTIVE. (An
  earlier `grep 'wave-[0-9]+'` matched `wave-32+` and a `wave-39` prose mention inside ARCHIVE, but
  those are not table rows — verified by reading the file.)
  **PASS**.

### 6. README "Where to look" table covers all 9 top-level docs
Table at `README.md:15–24` lists README, MASTER-FLOW, CLAUDE/KIMI, HANDOFF, HIERARCHY, HOW_TO_RUN,
CHANGELOG, CONTRIBUTING — all 9 (CLAUDE and KIMI share a row). Every one of the 9 files also carries
a one-line role header linking back to README. **PASS**.

### 7. No broken markdown links (FM-03)
  ```
  $ bash ~/Desktop/Adaptoid-OS/validators/preflight.sh 2>&1 | grep -A1 FM-03
  OK FM-03: all markdown references resolve
  ```
  **PASS** (full preflight: PASS).

### 8. Full test suite unchanged
`src/` and `tests/` were not modified this wave (zero code changes), so the suite cannot have
regressed. In this resumed shell a live Postgres/Redis is not available, so a full `pytest` run
errors out on DB-dependent fixtures (collection still succeeds: **459 items collected**, matching
the pre-existing count). The run was not used as a gate because the wave's contract is "touches
zero code" — which is satisfied by inspection. No test logic changed.

## What moved where

| From (repo root) | To | Count | Method |
|---|---|---|---|
| `load-test-report-*.html` | `docs/performance-runs/` | 16 | `git mv` |
| `load-test-results-*_*.csv` | `docs/performance-runs/` | 12 | `git mv` |
| (new) `docs/performance-runs/README.md` | explains each run, concurrency, which `PERFORMANCE.md` cites, and the `200408` 28.6% failure-rate bug note | 1 | created |

Every reference to the old root paths in `docs/PERFORMANCE.md` (8 references) and
`work/reports/wave-35/01-performance-load-validation.report.md` (2 references) was repointed to
`docs/performance-runs/`. `.gitignore` now ignores `load-test-report-*.html` and
`load-test-results-*` so future runs don't land at root again.

## Other brief items (§2–§6) — all present from prior session
- **HIERARCHY.md** restored as a real map: removed 28 artifact lines + duplicate `202748_*` block,
  removed `playwright-report/`/`test-results/`, fixed the orphaned table rows (`.github/workflows/`,
  `.claude/`), added `backups/`, `uploads/`, `resources/`, `node_modules/`.
- **`docs/historical/README.md`** index added (349 files grouped, "frozen archive" note).
- **Top-level docs** got role headers; README got the "Where to look" table.
- **`PROJECT_HISTORY.md` / `CHANGELOG.md`** reconciled (commit `b40da9a`).

## What the brief did not anticipate
- `wave-32` is SHIPPED but was treated as "live" (in ACTIVE, not ARCHIVE's 1–31 range). The brief's
  §3 literally scopes ARCHIVE to 1–31 and ACTIVE to 33/34/36/37/38, leaving 32 unassigned. We placed
  32 in ACTIVE (it is the most recent shipped wave and is the dependency root for 33–38), keeping the
  1–38 "exactly one" invariant true. Minor deviation from the brief's literal wave list, justified.
- The load-test filenames at root were already date-stamped (`20260819-*`), so the move was
  mechanical; no rename collisions.

## What I chose NOT to do, and why
- **Did not delete `backups/`/`node_modules/` rows from HIERARCHY.** The brief explicitly says to add
  them; their absence-on-clean-checkout is documented by footnote. Removing them would contradict §2.
- **Did not move `work/wave-*` folders** (brief forbids it — would break cross-references).
- **Did not run the full pytest suite to green.** It requires live Postgres/Redis unavailable here;
  since zero code changed, there is no regression to detect. Flagged transparently above.
- **Did not touch `src/`, `tests/`, `docs/historical/**` contents, or `attic/`** — per the
  "must NOT touch" list and archive-never-delete rule.

## Root listing — before vs after
- **Before (commit `bfd2c54`):** 59 top-level entries (incl. 28 `load-test-*` files, 9 top-level
  orchestration docs, normal dirs/files).
- **After (this session):** 29 entries —

  ```
  CHANGELOG.md        CLAUDE.md           CONTRIBUTING.md     Dockerfile
  Dockerfile.frontend HANDOFF.md          HIERARCHY.md        HOW_TO_RUN.md
  KIMI.md             MASTER-FLOW.md      Makefile            README.md
  attic               deliverables        docker-compose.prod.yml  docker-compose.yml
  docs                mcp.json            orchestrator        plan
  playwright.config.ts  pyproject.toml    requirements.txt    resources
  scripts             src                 tests               uploads
  work
  ```
  (down from 59; the 28 `load-test-*` artifacts are gone from root, replaced by their new home
  `docs/performance-runs/`.)
