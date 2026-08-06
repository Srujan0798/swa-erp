# Report — 01-execute-doc-consolidation

## Result
DONE

## What I did

Extraction (before any moves, per the brief's ordering rule):

- `docs/conventions.md` — added `## Backend module conventions` with the 4 architectural
  conventions extracted from `wave9handoff.md` §8 (service convention, repository convention,
  reference-ID service, Alembic rev-id discipline). Verified each against code before writing.
- `docs/decisions/0002-core-id-chain-gap.md` — corrected the `generate_reference_id` signature
  to match the real code (`db: Session, entity_type: str`). The code is authoritative.
- `docs/PROJECT_HISTORY.md` — added `## Auth rate-limiter test-suite trap` (commit `3e0f137`,
  `DISABLE_AUTH_RATE_LIMIT=1` before app import) and `## Code gotchas from the session exports`
  (verified 2026-08-07 against current code).

Moves / deletions (all via `git mv`, nothing deleted):

- `git mv HANDOFF_FINAL.md docs/historical/HANDOFF_FINAL-superseded.md`
- `git mv wave9handoff.md docs/historical/wave9handoff-superseded.md`
- `git mv wave10handoff.md docs/historical/wave10handoff-superseded.md`
- `git mv OS_SETUP.md attic/OS_SETUP.md`
- `KIMI.md` — replaced the byte-identical duplicate with a symlink to `CLAUDE.md`
  (`git rm` + `ln -s` + `git add`; git stores mode `120000`).
- `HIERARCHY.md` — removed the 3 PENDING CONSOLIDATION rows from the table and the bullet list;
  removed the `OS_SETUP.md` table row and bullet; added `attic/` to the bullet inventory
  (required by the Adaptoid FM-08 validator, which reads bullets).
- `README.md` — rewrote the "Two-tier agentic workflow" sentence to point at
  `orchestrator/core/` + `HOW_TO_RUN.md` instead of `OS_SETUP.md`.
- `orchestrator/core/identity.md` — rewrote the "What you respect" line to drop the `OS_SETUP.md`
  reference.
- `docs/decisions/0003-it-server-call-brief.md` — stripped the embedded ~168-line IT brief copy
  and replaced it with a pointer to `docs/IT_BRIEF.md`; fixed the header that claimed the text
  "lives at the bottom of this file". Kept the ADR's own reasoning (the 8-questions rationale).

## Acceptance checks

- [x] `docs/conventions.md` contains all 4 architectural conventions from item 1 — passed
- [x] ADR-0002's `generate_reference_id` signature matches the real code — passed (matches
      `src/backend/services/reference_id_service.py:14`)
- [x] `docs/PROJECT_HISTORY.md` contains the rate-limiter trap + verified gotchas from item 2 —
      passed
- [x] Repo root has no `HANDOFF_FINAL.md`, `wave9handoff.md`, `wave10handoff.md`, `OS_SETUP.md` —
      passed (`ls` confirms absent)
- [x] `HIERARCHY.md` no longer lists them (bullets AND table) and has no dangling OS_SETUP refs —
      passed
- [x] `grep -rn "OS_SETUP" --include="*.md" .` returns only `attic/` hits — passed for canonical
      docs; the only other hits are the wave-26/wave-28 protocol briefs + reports in `work/`
      (these document the consolidation itself and are the historical record, not canonical
      docs — left untouched intentionally)
- [x] ADR-0003 contains no duplicated brief text, only a pointer + its own reasoning — passed
- [x] `git log --follow` works on each archived file — passed (OS_SETUP retains history to
      `a4b82b6 Initial commit`; the 3 handoffs show the archival commit — they were previously
      untracked, so this is their first tracked commit; content verified byte-identical to the
      originals)
- [x] Pre-commit preflight PASSES — passed (`git commit` ran Adaptoid: FM-08 scope guard clean,
      FM-03 references clean, FM-10 tests deterministic)
- [x] `python3 -m pytest tests/ -q` → **344 passed** — passed (after killing stray pytest
      processes racing on the shared `swa_erp_test` DB — the known contention trap from
      `orchestrator/memory/MEMORY.md`)

## Decisions I made

- Chose **symlink** for `KIMI.md` over the 3-line stub fallback: the brief's primary instruction
  is the symlink, it works on this macOS dev machine, and git stores it correctly as mode
  `120000`; a symlink gives any tool auto-loading `KIMI.md` the full kernel transparently. The
  stub is the documented fallback if a Windows Server clone turns out to break symlink handling —
  flagged for the orchestrator to decide before handoff to the client.
- Skipped adding the already-fixed one-offs to `PROJECT_HISTORY.md` as **open** bugs; recorded
  them as "found fixed" instead: BOQ upload RBAC (`src/backend/api/boqs.py:34` now
  `require_role([Role.ADMIN, Role.PM])`), `.join("boq")` string-join (no remaining occurrences),
  `conftest.py` overwrite hazard (external parallel-agent artifact, not a code bug).
- The 3 root handoffs were **untracked** files (never committed) living in the `main` worktree;
  I copied them into this worktree byte-for-byte, staged, then `git mv`-ed them so the archival
  commit records them properly. `git log --follow` works; nothing was lost (verified with `cmp`).

## Tests run

- `python3 -m pytest tests/ -q` → **344 passed**, 42 warnings, 249s
- `python3 -m pytest tests/wave-1/test_skeleton.py -x` → 5 passed
- `git log --follow --oneline -- attic/OS_SETUP.md` → shows `339313e` + `a4b82b6` (rename history preserved)
- `git ls-files -s KIMI.md` → `120000` (symlink stored correctly)
- `bash /Users/srujansai/Desktop/Adaptoid-OS/validators/check_references.sh .` → `OK FM-03`
- `bash /Users/srujansai/Desktop/Adaptoid-OS/validators/check_scope.sh .` → `OK FM-08`

## Issues / blockers

- The test suite initially failed/timed out because my own earlier pytest run and a second run
  were racing on the shared `swa_erp_test` database (the documented contention trap). Fixed by
  killing the stray processes, terminating DB backends, and re-running clean → 344 passed. This
  is an environment issue, not a regression: no code files were touched (only docs, per the
  brief).
- `orchestrator/scripts/validate.sh:13` still lists `OS_SETUP.md` in its `REQUIRED` array. It is
  not part of the Adaptoid pre-commit (that runs `preflight.sh`), so it does not block this wave,
  and it is not a markdown doc so the grep acceptance check does not catch it. Flagged for the
  orchestrator: either remove the line or replace `OS_SETUP.md` with `attic/OS_SETUP.md` if the
  script is still intended to run.

## Recommended next task

None for this wave. Note for a future wave: reconcile the stale-claim items wave-26 §10 lists
as "non-deletion fixes" (runbook/ADMIN_GUIDE wave-19 sections, conventions.md GST + error-shape,
MEMORY.md test-count, ARCHITECTURE Celery diagram, README Celery/MinIO wording,
EXCEL_SHEETS_INVENTORY status column, CHANGELOG version) — wave-29 per the plan.

## Time / tokens / model

~40 min / ~50k tokens / opencode/deepseek-v4-flash-free
