# Wave-30 Task 01 — Final release verification and submission package

## What to do
The last task. Verify the entire system end to end, cut a real version, and produce the
submission package. **Nothing in this task is allowed to take anything on faith** — every claim
in the final report must be backed by a command you ran and whose output you paste.

**Depends on waves 22, 23, 24, 27, 28, 29 all being complete.** Do not start until every one has
a report in `work/reports/`. If any is missing, stop and say so — do not proceed with a partial
release and do not do the missing wave's work yourself.

## Files to modify
- `pyproject.toml`, `src/frontend/package.json` (version bump)
- `CHANGELOG.md` (release entry)
- `HANDOFF.md`, `plan/EXECUTION.md` (final status)
- CREATE: `deliverables/SUBMISSION.md`

## The work

### 1. Full verification sweep — run everything, paste real output
Run each and record the actual result. Do not summarize as "passing" — paste the counts.
```bash
ps aux | grep pytest                              # must be empty before you start
python3 -m pytest tests/ -q                       # expect 344+ passed, 0 failed
ruff check src/backend/                           # expect clean or documented ignores
cd src/frontend && npx tsc --noEmit                # expect 0 errors
cd src/frontend && npx eslint . --ext ts,tsx --max-warnings 0
cd src/frontend && npx vite build                  # must succeed
docker compose down -v && docker compose up -d --build   # full cold boot
docker compose ps                                  # every service healthy
curl -sf http://localhost:8000/healthz             # 200
npx playwright test tests/e2e/ --workers=1         # expect 7/7
alembic -c src/backend/alembic.ini heads           # record head count
```
If **anything** fails: fix it if it's small and clearly in scope, or stop and report it as a
release blocker. Do not paper over a failure to get to a green report — a truthful "not ready"
is the correct output if that's the reality.

### 2. Live end-to-end business-flow validation
Beyond unit tests, walk the actual client-requested chain against the running stack via the API,
as a real user would. This is the thing the client actually asked for, so it must demonstrably
work:
```
login → create Inquiry → convert (existing-client path AND new-client path)
     → create Service Agreement → issue Token → issue Document Reference
     → log time against it → record a Sustainability metric → generate an invoice (verify GST)
     → export a report
```
Record each step's status code and the generated reference IDs (they should follow
`SWA-{year}-{TYPE}-{seq:03d}`). Confirm the DBR/KDR shared-counter behavior and that a Designer
role can do what wave-22 made possible.

### 3. Version bump — the app has never been versioned
Both `pyproject.toml` and `src/frontend/package.json` still say `0.2.0` despite 25+ waves. Set
both to **`1.0.0`** — this is the client-submission release and semver-wise it is the first
version being handed over as complete. Keep the two files in sync.

### 4. CHANGELOG + final status
- `CHANGELOG.md`: add a `## [1.0.0]` entry summarizing everything since 0.3.0 (waves 22-30),
  grouped Added/Fixed/Changed/Security. Reconcile the link refs at the bottom.
- `plan/EXECUTION.md`: mark waves 22-30 with their real outcomes.
- `HANDOFF.md`: replace the "current state" section with the final delivered state.
- Tag the release: `git tag -a v1.0.0 -m "SWA ERP v1.0.0 — client submission"` (do NOT push the
  tag; leave that to the orchestrator).

### 5. Produce `deliverables/SUBMISSION.md`
The single document handed over with the project. Must contain:
- **What was built** — the modules, in plain language, mapped to the client's original
  Inquiry→Client→Agreement→Token→DocRef→TimeLog chain from `resources/MEETINGS_MASTER.md`
- **Verification evidence** — the actual command outputs from step 1, pasted, with dates
- **What is explicitly NOT included** — the drop list Viraj agreed (HR, finance, complaints,
  satisfaction, marketing), plus anything else deliberately deferred
- **Known limitations, stated honestly** — Celery installed but unimplemented (jobs run
  synchronously), file storage is local disk not MinIO, JWT is HS256 not RS256, whatever wave-24
  couldn't finish. **Do not hide these.** A client discovering an unstated gap after handover
  costs far more trust than one disclosed up front.
- **The 2 open external blockers** — Viraj's 3 decisions (ADR-0002), IT/Vikrant's 8 answers
  (`docs/IT_BRIEF.md`) — with what each blocks and what happens if unanswered
- **How to deploy** — pointer to `docs/DEPLOYMENT_CHECKLIST.md` and `docker-compose.prod.yml`,
  noting the PENDING IT ANSWER placeholders that must be filled first
- **How to import the existing Excel data** — pointer to `scripts/import_excel.py`, dry-run first
- **Where the docs live** — the canonical set after wave-28's consolidation
- **Support/next steps** — what a future developer picks up first

## Acceptance criteria
- [ ] Every command in step 1 run, real output recorded in the report
- [ ] The step-2 business flow completes end to end with real reference IDs recorded
- [ ] Both version files say `1.0.0` and agree
- [ ] `CHANGELOG.md` has a complete, accurate `[1.0.0]` entry
- [ ] `git tag -l` shows `v1.0.0` locally (unpushed)
- [ ] `deliverables/SUBMISSION.md` covers all 8 required sections above
- [ ] Pre-commit preflight passes
- [ ] **The submission document contains no claim you did not personally verify this session**

## How to deliver
1. Verify (steps 1-2) BEFORE writing anything — if verification fails, the release doesn't happen
2. Then version, changelog, submission doc
3. Report to `work/reports/wave-30/01-final-release-and-submission.report.md` with a clear
   top-line verdict: **READY TO SUBMIT** or **NOT READY — <blockers>**
4. Stop. Do not push the tag; the orchestrator does that.

## Constraints
- Time budget: 150 min
- A truthful "not ready" beats a green report that hides a failure — you will not be judged on
  reaching READY, you will be judged on whether the verdict is trustworthy
- Do not do other waves' work; report their absence as a blocker instead
- Allowed tools: file edit, bash, pytest, ruff, npm, docker, playwright, curl, git (no push)
