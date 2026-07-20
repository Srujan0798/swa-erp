# Project History — extracted from ULTIMATE_HANDOFF.md

**Status:** This file replaces `ULTIMATE_HANDOFF.md` (7,142 lines, archived at
`docs/historical/ULTIMATE_HANDOFF-superseded.md`) as the place to look for genuinely
historical/durable context that isn't already covered by current docs.

## Honest assessment of the source material

`ULTIMATE_HANDOFF.md` claimed to be a three-level merge ("142 handoffs → 29 L1 batches → 6 L2
groups → 1 L3 ULTIMATE") synthesizing 142 OpenCode sessions. Read in full: it is not a synthesis.
It is a mechanical concatenation of per-session telemetry blocks — session ID, tool, model,
token counts, cost, "what this session worked on" (usually the literal worker prompt pasted
verbatim), and a truncated "last assistant summary." There is no distillation step visible
anywhere in the file: no section that states a decision and its reasoning in prose, no "we tried
X, it didn't work, here's why," no synthesis across sessions. It reads exactly like what its own
"Merge Tree" section implies happened mechanically, not editorially.

Concretely, of the ~7,100 lines:
- The large majority are repeated worker-dispatch prompts ("You are an OpenCode worker. Read
  work/wave-N/...") and matching "Files changed: 0, Lines added: 0" telemetry — noise, already
  superseded by the actual code and by `plan/EXECUTION.md` / `HANDOFF.md`.
- A recurring thread of wave-9 "Fix A" through "Fix I" sessions chasing a cascading test-suite
  regression is the one place with real signal (captured below).
- No architectural decisions, client-facing reasoning, or process lessons appear anywhere that
  aren't already captured — and captured in far more depth and readable form — in
  `resources/MEETINGS_MASTER.md` and `docs/decisions/0001` through `0004`.
- Several sections reference a since-abandoned timeline (waves numbered 9–15 covering
  Inquiries/Marketing/R&D/HR/CRM modules, a `PROJECT_COMPLETE.md`, Windows deploy docs) that does
  not match the current wave plan in `plan/EXECUTION.md` / `HANDOFF.md`. That earlier numbering
  was superseded when the orchestrator re-scoped the project around the real Inquiry→Agreement→
  Token→DocumentReference chain (see `docs/decisions/0002-core-id-chain-gap.md`). Nothing from
  that abandoned numbering is carried forward here since it no longer describes the live plan.

**Bottom line: this file is short because the source material earned a short file.** The one
substantive extraction follows.

## The one real technical lesson: Postgres native ENUM types + pytest fixture scoping

A cluster of wave-9 "fix" sessions (originally titled "Fix A" through "Fix I" in the source
handoff) chased a cascading test failure across the token, DRN, sustainability, time-logging,
employee, HR, and agreement/inquiry modules simultaneously. The common root cause, as diagnosed
mid-chain by one of those sessions (partially truncated in the original, reconstructed here from
the surrounding fix sessions that all referenced it as "already fixed"):

- `_reset_tables()` in the test setup dropped the schema without `checkfirst=True`.
- Postgres native `ENUM` types created via `CREATE TYPE` aren't automatically dropped by
  `DROP TABLE` / `Base.metadata.drop_all()` the way plain columns are — they're separate
  catalog objects with their own OIDs.
- Both a session-scoped and a function-scoped fixture were independently calling
  `Base.metadata.create_all(bind=engine)`, so on the second call Postgres would refuse to
  recreate a type that still existed from the first, and pooled connections could end up holding
  stale OIDs for types that had technically been dropped and recreated.
- This surfaced as unrelated-looking failures across many different modules at once (tests
  failing on `deleted_at` missing, `token_id` NULL, dict-vs-model-instance mismatches) because the
  DB fixture itself was silently inconsistent between test runs, not because each module was
  independently broken — which is why nine separate "fix" sessions were dispatched before the
  shared root cause was found and the individual module fixes actually landed cleanly.

**Why this is worth keeping**: `tests/conftest.py` today (see `_reset_tables()` and the
`create_all` calls around line 23-57) reflects the fixed state, so there's nothing to change
right now. But if `conftest.py`'s DB reset/fixture-scoping logic is ever touched again — e.g.
adding a new session-scoped fixture, or adding another native Postgres `ENUM` column — re-check
for this exact class of bug: symptoms show up as unrelated multi-module test failures, not an
obvious schema error, and the fix is almost never in the failing module itself.

Smaller, module-local fixes from the same chain (already reflected in current code, listed only
so nobody "fixes" them again from scratch if this pattern resurfaces):
- DELETE endpoints returning bare `None` with `status_code=204` raised
  `TypeError: 'NoneType' object is not callable` — must return `Response(status_code=204)`
  explicitly.
- `SWA-{year}-{TYPE}-{seq}` business IDs are 16 characters (`SWA-YYYY-CLT-NNN`), not 18 — a test
  once asserted the wrong length.
- The ID generator originally displayed a literal `year=0` in generated IDs before being fixed to
  use `current_year()`.

## Everything else worth knowing is already documented elsewhere

Checked against the source material and confirmed there is nothing else to extract — these are
the current, authoritative docs for the topics ULTIMATE_HANDOFF.md gestured at:

- **Client meeting content, verbatim quotes, business logic, open questions** —
  `resources/MEETINGS_MASTER.md` (far more complete and correctly attributed than anything in the
  handoff).
- **Architectural decisions and their rejected alternatives** — `docs/decisions/0001-tech-stack.md`.
- **The core ID-chain gap, what was mis-modeled and corrected, and what's still open** —
  `docs/decisions/0002-core-id-chain-gap.md`.
- **Infra/deployment planning** — `docs/decisions/0003-it-server-call-brief.md`.
- **How to work with the client (Viraj) — communication style, closed-question norm** —
  `docs/decisions/0004-meeting-2-flow-and-next-steps.md` and §10 of
  `resources/MEETINGS_MASTER.md`. (ULTIMATE_HANDOFF.md contains no equivalent content; this
  entire thread of process learning lives only in the meeting notes and ADRs, not the handoff.)
- **Wave status, what shipped, what's next** — `plan/EXECUTION.md` and `HANDOFF.md`.

## Note on other stale root-level docs

`FINAL_SPEC.md` (root, dated 2026-07-01) is materially stale as of this writing: it lists waves
3-8 as uncommitted and Docker as unverified, but `git log` shows waves 3-8 through 13 are all
committed (e.g. `6a1ed3b`, `540242e`, `5da7a33`, `58864df`, `a155000`, `4e0655d`, `466d8ae`,
`c3367fa`), and wave-12 (`9852ec0`) specifically did the independent verification `FINAL_SPEC.md`
still lists as blocked. Left untouched per instruction — flagged here and in the handoff back to
the orchestrator for a separate decision.
