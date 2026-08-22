# Historical Archive — index

This directory is a **frozen archive**. Nothing here is the current source of truth — contents
were superseded by later waves and are kept for reference, audit, and "we tried X and here is
why" value. **Live documentation lives in `docs/`** (and `README.md`, `HIERARCHY.md`,
`plan/`, `resources/`). If you are looking for how the project works today, start there, not
here. 349 files, grouped below.

## Superseded handoffs and session telemetry

`handoffs/` (142 files) and `merged_handoffs/` (35 batch files) are the raw per-session
OpenCode telemetry blocks (session IDs, prompts, tool usage, token counts) from early
development. They were mechanically concatenated into `ULTIMATE_HANDOFF.md`, which itself was
distilled down to the genuinely durable lessons in `docs/PROJECT_HISTORY.md`. Read those, not
these. The raw exports that generated them are gitignored (`docs/historical/session_exports/`).

## Superseded root docs

The six `*-superseded.md` files at the top of this folder are earlier versions of documents
that still exist live: `FINAL_SPEC` (stale as of wave-12 — its wave-3-8-uncommitted claims were
long since resolved), `ULTIMATE_HANDOFF` (superseded by `docs/PROJECT_HISTORY.md`),
`HANDOFF_FINAL`, `wave9handoff` / `wave10handoff` (superseded by `work/ARCHIVE.md` and the
current `HANDOFF.md`), and `IT_BRIEF` (superseded by `docs/IT_BRIEF.md`).

## Superseded meeting records

`meetings/` holds the raw transcripts and early "clean" summaries of the two client meetings.
They were consolidated and corrected into `resources/MEETINGS_MASTER.md`, which is the
authoritative record — including IT's "100+ concurrent users" claim (marked there as
unverified on the client's hardware).

## Archived wave specs

`specify-specs/` contains the wave spec archives for waves 1-4 and 9 (the generic
specification-process output from early planning). They describe target-state designs that
were partly superseded by the re-scoped core ID chain (see
`docs/decisions/0002-core-id-chain-gap.md`).

## Superseded steering docs

`specify-steering/` holds early steering notes from the specification process; superseded by
`plan/` (PRD / ARCHITECTURE / EXECUTION) and `orchestrator/`.

## House rules

- **This archive is frozen.** Do not edit contents; append new superseded material, never
  modify or delete existing files.
- If you need a definitive answer, check `docs/` and `resources/` first — the answer is
  almost certainly already distilled there.