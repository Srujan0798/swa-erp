# Wave-47 Task 01 — Final seal: close Definition-of-Done A–E

**This is the last wave.** When it lands honestly, the project is closed for internship submission. Read `work/FINAL-CLOSE/DEFINITION-OF-DONE.md` first — your job is to make A–E true and prove it.

## Verified state at HEAD `4d1135f` (orchestrator measured this — do not re-derive, but DO re-verify)

```
python3 -m pytest tests/ -q --tb=no
564 passed / 2 failed / 7 skipped
  - both failures: /readyz probes needing Redis (environmental)
  - 6 of 7 skips: MinIO-dependent; 1 manual-only
cd src/frontend && npx vitest run
523 passed / 0 failed
```
Migrations: single head `0033`. HIERARCHY.md valid both directions. Preflight: PASS.

## Files you own
- `work/reports/FINAL-CLOSE.report.md`
- `work/ACTIVE.md`, `HANDOFF.md`, `plan/EXECUTION.md`, `CHANGELOG.md`
- `work/reports/wave-47/` (your report)
- Any lint/type fix required by step 1 (source files allowed ONLY for gate failures)

## The work

### 1. DoD section B — the gates nobody has verified
Run each, paste real output:
```bash
ruff check src/backend/
black --check src/backend/
mypy src/backend/ --explicit-package-bases
cd src/frontend && npx tsc --noEmit
cd src/frontend && npx eslint . --ext ts,tsx --max-warnings 0
cd src/frontend && npx vite build
```
Fix what fails. If mypy has pre-existing library-stub noise (openpyxl/fpdf/jose were previously documented as such), separate **real code errors** from **missing third-party stubs** and say which is which — do not claim clean if it isn't.

### 2. DoD section B — full-stack run with Docker
The 2 failing tests and 6 skips are environmental. Bring the stack up and prove the real number:
```bash
docker compose up -d postgres redis minio   # adjust to actual service names
python3 -m pytest tests/ -q --tb=no
```
Expected: **0 failed**, skips reduced. If Docker is unavailable to you, write "NOT MEASURED — Docker unavailable" and keep the macOS numbers with their caveat. **Do not guess.**

### 3. DoD section A + D — reconcile the trackers to reality
- `work/ACTIVE.md`: waves 32–47 status, one row each, matching git
- `HANDOFF.md`: rewritten (never appended) so a cold session resumes correctly
- `plan/EXECUTION.md`: every SHIPPED wave has a commit hash
- `CHANGELOG.md`: `[Unreleased]` covers waves 40–47
Run `bash orchestrator/scripts/validate_execution.sh` if wave-40 has landed; otherwise verify by hand and say so.

### 4. Rewrite `work/reports/FINAL-CLOSE.report.md`
The current one declared CLOSED on numbers that did not reproduce; wave-46 corrected it. Rewrite it as the true seal:
- Real measured suite numbers + the exact commands
- What is environmental vs what is a defect
- Honest external remainder (DoD section E): Viraj server facts, deploy, Excel migration owner, client-box load test — all **external**, none blocking engineering close
- A short, honest "known limitations" list

**Forbidden:** "100% complete", "zero residual risk", any pass count you did not read from output this session, global "no module under 70%".

### 5. Verdict
End your report with exactly one of:
- `ENGINEERING CLOSE COMPLETE` — only if DoD A–E are all true, with evidence for each
- `NOT CLOSED — <the specific unmet criteria>`

## Acceptance criteria
- [ ] Every DoD A–E box addressed explicitly with evidence or an honest NOT MET
- [ ] All six gate commands in step 1 run, output pasted
- [ ] Suite numbers came from a run you performed this session
- [ ] `FINAL-CLOSE.report.md` contains no number without an adjacent command
- [ ] Trackers match `git log` (no wave marked SHIPPED without a hash)

## Deliver
`work/reports/wave-47/01-final-seal.report.md`. Commit before writing it.

## Constraints
- Time budget: 180 min · commit per numbered item
- Six prior reports in this repo failed on fabricated or non-reproducing numbers. Yours is the seal — if it lies, the whole record is worthless.
- Source edits ONLY to fix a gate failure from step 1. No features.
