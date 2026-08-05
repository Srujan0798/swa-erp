# Wave-26 Task 01 — Extract the 3 root handoffs (HIGHEST VALUE — do this one first)

**Read `work/wave-26/00-EXTRACTION-SCHEMA.md` first.** All its rules bind you, especially:
you edit NOTHING except your own report.

## Scope — exactly these 3 files, read every line of each
- `HANDOFF_FINAL.md` (8.7KB, dated 2026-07-03)
- `wave9handoff.md` (7.6KB, dated 2026-08-05, self-titled "FULL HANDOFF — all 25 waves")
- `wave10handoff.md` (3.8KB, dated 2026-08-05, self-titled "Complete Session Handoff")

These came directly out of OpenCode worker sessions and were dropped in the repo root. They are
the **newest and least-processed** material in the project — unlike the 142 archived handoffs,
these have never been reviewed, distilled, or cross-checked by anyone. Treat them as the
highest-value target in wave-26.

## What makes this task non-trivial
`HANDOFF_FINAL.md` is confidently, comprehensively **wrong about status**: it says "Waves 1-3
SHIPPED | Wave-4 IN PROGRESS | 97/97 tests". Reality is waves 1-21 shipped and 344 tests pass.
It is a month stale. **But its non-status content may still be valuable** — it contains a
5-stakeholder-decision list, a 21-Excel-sheet mapping, a tech-debt list, and a key-files index.
Your job is to separate the durable signal from the stale status claims, not to dismiss the
whole file because its header is wrong.

The other two are recent and probably largely accurate, but still verify — `wave9handoff.md`
claims "all 25 waves" and `wave10handoff.md` gives a chronological account; check their specific
factual claims (test counts, what's committed, what's blocked) against the actual repo.

## Specific things to hunt for and report
1. **The 5 stakeholder decisions** in `HANDOFF_FINAL.md` — list all 5 verbatim. For each, check
   whether it is already tracked in `docs/decisions/0002-core-id-chain-gap.md`'s open-questions
   table or `docs/IT_BRIEF.md`. Flag any that are NOT tracked anywhere — those are decisions at
   risk of being lost, and finding them is the single most valuable outcome of this task.
2. **The 21-Excel-sheet mapping** — compare against `resources/EXCEL_SHEETS_INVENTORY.md`. Is
   anything in the handoff's mapping missing from the inventory doc?
3. **The tech-debt list** — compare each item against what's already captured in the wave-22,
   wave-23, wave-24 task briefs (`work/wave-22/`, `work/wave-23/`, `work/wave-24/`). Report any
   tech-debt item NOT already covered by those briefs.
4. **Anything about waves 22-25** in the two recent handoffs — those waves have briefs but were
   never executed; if these handoffs say anything about their status, that's important.
5. Any **decision, constraint, or client statement** not already in
   `resources/MEETINGS_MASTER.md`.

## Verification requirement
For every factual claim you carry forward into your report, either verify it against the repo
(cite the file/command that proves it) or mark it `UNVERIFIED`. Specifically verify any claim
about: test counts, what's committed, wave status, what's implemented. Cheap verification
commands: `git log --oneline -20`, `python3 -m pytest tests/ -q 2>&1 | tail -3`,
`ls work/reports/`.

## Deliver
Report to `work/reports/wave-26/01-extract-root-handoffs.report.md` using the mandatory schema
in `00-EXTRACTION-SCHEMA.md`. Then STOP.

## Constraints
- Time budget: 60 min
- Edit nothing but your report
- Allowed tools: read, grep, git (read-only), pytest (read-only verification)
