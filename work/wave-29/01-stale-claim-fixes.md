# Wave-29 Task 01 — Fix the remaining stale claims across current docs

## What to do
Wave-26 report 04 §10 identified 9 documents that are KEPT but contain specific stale or wrong
factual claims. Fix each. These are small, surgical text corrections — no restructuring.

**Depends on wave-27 and wave-28 landing first**, because several of these claims are about
things those waves change (test counts, wave-19 status, file locations).

## The fix list — verify each against reality before writing the correction

For every item: **check the actual current state first**, then write what's true. Do not copy the
"should be" values below on faith — they were accurate when the audit ran and may have moved.

| # | File | Stale claim | What to verify |
|---|---|---|---|
| 1 | `docs/runbook.md` | wave-19 section says backup scripts don't exist yet | They exist now (`scripts/backup_db.sh` etc.) and wave-27 hardened them — point at `docs/runbook_backup_restore.md` |
| 2 | `deliverables/handover/ADMIN_GUIDE.md` | Same wave-19 "not built yet" caveat | Same fix — this one is **client-facing**, so it must be correct and plainly worded |
| 3 | `docs/conventions.md` | GST described as not implemented; error-shape description | GST shipped in wave-18 (`2073c36`) — verify the real invoice fields before writing |
| 4 | `orchestrator/memory/MEMORY.md` | Test count + GST lines stale | Current count from a real run; GST now implemented |
| 5 | `HANDOFF.md` | Test count stale | Real current number |
| 6 | `plan/ARCHITECTURE.md` | Celery shown in the diagram without marking it target-vs-real | Celery is an **installed dependency with zero implementation** — no app, no `@task`, no worker service. The prose says this correctly; the ASCII diagram doesn't. Mark it clearly as target-state in the diagram itself |
| 7 | `README.md` | Celery/MinIO wording implies both are live | Neither is: storage is a local `uploads/` dir, Celery is unimplemented. Reword honestly without overclaiming |
| 8 | `resources/EXCEL_SHEETS_INVENTORY.md` | Status column marks shipped things "Pending ⏳" and wave-4 "READY TO DISPATCH" | Waves 4-8 shipped. **Fix only the Status column** — the sheet-to-entity mapping itself is correct and canonical, don't touch it |
| 9 | `CHANGELOG.md` | Version vs git tags inconsistent | Reconcile against real tags (`git tag -l`) and the version bump wave-30 will do — coordinate: if wave-30 hasn't run, note the current version honestly rather than inventing one |

## The standard to apply
This project has been burned repeatedly by docs asserting things that were never built (RS256,
Sentry, Prometheus, MinIO, Celery, HTTPS-only cookies, refresh rotation). The rule now:

**Any claim that "X is implemented/working/integrated" must be verifiable by a grep or a command.
If you cannot verify it, either mark it explicitly as target-state/not-yet-built, or delete the
claim. Never restate a plan as an accomplished fact.**

Where you correct something, a brief inline note of what was wrong is welcome (this repo already
uses that pattern, e.g. "**Corrected 2026-07-21** — ..."), because it stops the next reader from
"re-fixing" it back.

## Acceptance criteria
- [ ] All 9 items corrected, each verified against the real repo (state your evidence per item)
- [ ] `grep -rn "Celery" --include="*.md" . | grep -v historical | grep -v attic` — every remaining
  mention is explicitly marked as not-yet-implemented / target-state
- [ ] Same check for `MinIO`
- [ ] No current doc states a test count that disagrees with a live `pytest` run
- [ ] `deliverables/handover/*` (client-facing) contains zero claims about unbuilt features
- [ ] `python3 -m pytest tests/ -q` → 344+ passed (docs-only task; any change is a regression)
- [ ] Pre-commit preflight passes

## How to deliver
1. Verify then fix each of the 9
2. Run the greps above to catch any mention you missed
3. Report to `work/reports/wave-29/01-stale-claim-fixes.report.md` — one line per item: what it
   said, what it says now, how you verified
4. Stop

## Constraints
- Time budget: 75 min
- Text corrections only — do not restructure documents or move files
- If an item turns out to already be correct, say so and move on; don't invent a change
- Allowed tools: file edit, grep, git, pytest
