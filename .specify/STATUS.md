# .specify/ status

**Added 2026-07-21** during a full-project file-by-file audit — this note exists so nobody
assumes `.specify/` is a maintained, current system when it isn't.

`.specify/specs/` has formal `{spec,plan,tasks,contracts}` for waves 1-4, one orphaned
`wave-9/spec.md` (added by the orchestrator alongside `work/wave-9/` on 2026-07-20 for that
specific wave, not part of a resumed practice), and **nothing for waves 5-8 or 10-25**.

This isn't accidental loss — waves 5-8 shipped via a single bulk commit (`ed71fac`) that
bypassed the formal spec-then-dispatch process entirely (see `plan/EXECUTION.md`'s note on this),
and every wave from 9 onward used `work/wave-N/*.md` task briefs as the operative spec instead of
`.specify/specs/wave-N/`. `work/wave-N/` + `work/reports/wave-N/` is the actual, current
source of truth for what was asked and what was delivered — treat `.specify/specs/` as a
historical record of how waves 1-4 were originally run, not a live index.

`.specify/memory/constitution.md` and `.specify/steering.md` are process/methodology documents,
not wave-specific — not evaluated for staleness here, check them separately if their content is
ever in question.
