# Wave-40 Task 01 — Truth infrastructure (kill FM-05 + FM-09 mechanically)

**Adaptoid archetype:** `internship` (§14). Its predicted top failure modes are FM-07, FM-09, FM-05, FM-12 — and this repo has been hit by all four. This wave makes two of them *structurally impossible* rather than a matter of discipline.

## The evidence this wave exists

- **FM-09 (false status):** FIVE reports in this repo have carried headline numbers that did not reproduce. The most recent is `work/reports/FINAL-CLOSE.report.md`, which declares the project CLOSED on "565 passed / 0 failed" — an independent run produced `7 failed, 559 passed, 7 skipped` (5 real auth failures + 2 environmental Redis ones).
- **FM-05 (metric inconsistency):** frontend statement coverage has been stated as **65.86%** (wave-34 report), **~61%** (handoff verdict), and **65.02%** (independent run). Three numbers, one metric, all hand-typed.

Rule being enforced (§13 FM-05): *"metrics live in ONE generated source (`results/metrics.json`); docs reference/regenerate, never hand-type."*

## Files you own (do NOT touch anything outside this list)
- `results/metrics.json` (generated — commit it)
- `scripts/generate_metrics.sh` (new)
- `orchestrator/scripts/validate_execution.sh` (new — spec in ADAPTOID-LITE.md §4.13)
- `orchestrator/scripts/validate_metrics.sh` (new)
- `.github/workflows/docs_sync.yml` (new — this is the ONLY workflow file you may touch)
- `HALL_OF_SHAME.md` (new)
- `BACKLOG.md` (new)
- `Makefile` (append targets only)

## The work

### 1. `scripts/generate_metrics.sh` → `results/metrics.json`
One script, runs both suites, emits ONE json. Shape:
```json
{
  "generated_at": "2026-08-28T00:00:00Z",
  "git_sha": "<full sha>",
  "backend":  {"passed": 0, "failed": 0, "skipped": 0, "coverage_total_pct": 0.0,
               "per_module": {"services/pdf_service.py": 100.0}},
  "frontend": {"passed": 0, "failed": 0, "coverage": {"statements": 0.0, "branches": 0.0, "functions": 0.0, "lines": 0.0}},
  "environmental_failures": ["tests requiring Redis when Redis is not running"]
}
```
Parse real pytest/vitest output — do not accept hand-entered values. **Critical gotcha:** vitest SUPPRESSES its coverage summary when any test fails, so the script must detect that case and record `null` + a `coverage_unavailable_reason`, never a stale or guessed number. That exact behaviour is why the three conflicting frontend figures exist.

### 2. `orchestrator/scripts/validate_metrics.sh`
Greps tracked `.md` files for coverage/pass-count patterns (e.g. `\d+\.\d+%`, `\d+ passed`) and fails if a number contradicts `results/metrics.json`. Allow an explicit opt-out comment `<!-- metrics-exempt: reason -->` for historical/annotated figures — this repo deliberately keeps corrected-but-annotated numbers for honesty, and those must not trip the gate.

### 3. `orchestrator/scripts/validate_execution.sh`
Implement per ADAPTOID-LITE.md §4.13: no duplicate wave rows, active wave matches across `plan/EXECUTION.md` + `HANDOFF.md`, every SHIPPED wave has a commit hash.

### 4. `.github/workflows/docs_sync.yml`
Runs `validate_execution.sh` + `validate_metrics.sh` on PR and push to main.

### 5. `HALL_OF_SHAME.md` — seed with this repo's REAL history
Use the §4.1 template. These are all verified, not hypothetical — write one entry each:
1. **Fabricated wave-33 report** — claimed 5 test files with pass counts; `find tests/wave-33` showed the directory did not exist. Caught by independent verification.
2. **Collected-count reported as passed-count** — a report claimed "562 passed"; 562 was the *collected* total (557 passed + 5 failed).
3. **FINAL-CLOSE sealed on a false green** — declared CLOSED at "0 failed" while 5 auth tests fail; protocol P05 was specified but never executed.
4. **Frontend coverage stated three ways** — 65.86 / ~61 / 65.02, root cause: vitest hides coverage on failure, so people copied stale figures.
5. **HIERARCHY.md padded to defeat its own scope guard** — 28 artifact filenames (with duplicates) pasted into the inventory so the FM-08 check would pass, instead of moving the artifacts.
6. **Two agents in one worktree** — a duplicate paste ran two `opencode` processes in the same `prof-G` worktree simultaneously; worktree isolation assumes one writer.
7. **`SQLAlchemy remote_side=["TaskComment.id"]`** — a string in a list instead of the Column object; broke 103 tests only when waves were combined, passed in isolation.

Each needs root cause, impact, fix, and a **prevention** line naming the guardrail that now stops it.

### 6. `BACKLOG.md`
Per §4.2. Seed with genuinely parked items found across this repo's reports — e.g. the 2 Redis-dependent `/readyz` tests being environment-coupled, and any RISK-classified findings from `work/reports/wave-37/`.

### 7. `Makefile`
Add `metrics:` (runs generate) and extend `verify:` to call both validators.

## Acceptance criteria
- [ ] `bash scripts/generate_metrics.sh` produces `results/metrics.json` with real parsed numbers — paste the file
- [ ] `bash orchestrator/scripts/validate_metrics.sh` exits 0 on a clean tree, and **exits non-zero when you deliberately hand-type a wrong % into a scratch md** — prove both, paste both outputs, then remove the scratch file
- [ ] `bash orchestrator/scripts/validate_execution.sh` exits 0 — paste output
- [ ] `HALL_OF_SHAME.md` has all 7 entries with prevention lines
- [ ] Full backend suite unchanged (this wave touches zero application code)

## Deliver
`work/reports/wave-40/01-truth-infrastructure.report.md`. Commit before writing it.

## Constraints
- Time budget: 150 min · commit after each numbered item
- Touch ONLY `.github/workflows/docs_sync.yml` inside `.github/` — other waves own other workflow files (FM-13 disjoint writes)
