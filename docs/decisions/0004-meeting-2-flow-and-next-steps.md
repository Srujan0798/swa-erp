# ADR-0004 — Meeting 2, re-read clearly: what was actually said, what it means, what's next

**Date:** 2026-07-20
**Source:** `resources/MEETINGS_MASTER.md` §Meeting 2 (raw transcript archived at
`docs/historical/meetings/meeting-2-raw.md`), re-read in full against the passage the
user highlighted). This is not new information beyond ADR-0002/0003 — it's the same transcript
re-walked step by step so nothing is glossed over, with each point turned into a concrete action.

## What actually happened in the meeting, in order

1. **Server confirmed.** Windows Server, on-prem, file-storage server today (no other apps
   hosted on it yet), 128GB RAM extendable, VPN access, staff reach things via a shortcut in
   their folders, some people already use RDP on it. IT said it can handle 100+ users. Viraj is
   "99% confident" it's Windows, not 100% — this is a real, acknowledged uncertainty, not settled.
   (*Wave-35 note: the "100+ users" figure is IT's claim and remains **unverified by our load
   tests** — measured: 10 concurrent users, p95 ≈ 29 ms on a dev machine, see `docs/PERFORMANCE.md`.*)
2. **Tech choices handed to the dev.** Viraj explicitly said "whatever you're willing to do, I'm
   okay with that... I can do anything... I'm okay with any configuration" when asked about SQL.
   This is Viraj deferring the technical stack decision entirely — already exercised via ADR-0001.
3. **IT introduction promised.** Viraj: "I'll connect you with a person who is setting up the
   server... that person will have a con call... that can be sorted on what the architecture or
   application architecture will consist of." **This is the IT call now happening** — ADR-0003 /
   `docs/IT_BRIEF.md` is the direct output of this line.
4. **Data ownership problem stated plainly, still unresolved.** Viraj: "who owns the data
   migration from Excel to ERP... we have everyone, like everyone has answers to the data as of
   now... it's hosted on OneDrive itself, we cannot have the read-only version." Translation: no
   single owner of the source data exists yet, and the data is live-edited by multiple people
   with no way to freeze it for migration. **This is still an open organizational problem**, not
   something code can solve — flagged again below under "what's genuinely still open."
5. **Five MVP modules confirmed by Viraj directly**, in his own words: "for the five modules, I'm
   like I would recommend the client's inquiries and the service agreements and the tokens and
   the projects... one module requires document referencing and time logging." This is the exact
   five: Clients, Inquiries, Service Agreements, Tokens, Projects — with Document Referencing +
   Time Logging as effectively a sixth/bundled module. **This matches what wave-9/10 already
   built** — no new scope here, just re-confirms the ADR-0002 chain was the right target.
6. **Scope-drop confirmed again, directly.** "We can ignore the independent chains and just
   focus on the interconnected chains... client complaints and client satisfaction we can also
   not have in the first build." Matches ADR-0002's existing drop list — no change needed.
7. **Communication process feedback — this is the part that mattered most for how we work
   together.** Direct quotes worth sitting with:
   - *"It's not your whole assignment, you'll get a little problem statement step by step what
     you need to do, right? It's not like your MBA classes that it's their project... you cannot
     like generally say 'give me everything to do and I'll do it step by step.' Somewhere you
     have to do your brain and figure it out."*
   - *"If you can point by point ask me, can you give answers to these questions that I have,
     that can be dealt with. But superlatively, I don't know what exactly you want and what can
     be shared. You can share a list of questions if you have."*

   This is the direct source of the scolding referenced earlier in this project. The pattern
   Viraj is rejecting: asking him to hand over a complete specification. The pattern he's asking
   for: come with your own analysis/plan already done, and ask *specific, closed, answerable*
   questions only for the things that genuinely can't be inferred (like server specifics only IT
   knows, or business decisions only he can make — e.g. the 4th agreement type). This is exactly
   the shape `docs/decisions/0002-core-id-chain-gap.md`'s "still open" table and `docs/IT_BRIEF.md`
   are already built to — each open item states a specific, closed question, not "tell me
   everything."
8. **Live demo walkthrough happened.** Viraj was shown the actual flow (Inquiry → check-existing-
   client → Project; Document Reference sheet structure with PRN/DBR/GED codes; service agreement
   /token annual-engagement logic) — this is the exact flow ADR-0002 documents and wave-9 built
   against. Viraj's own words confirm the flow independently: *"we inquire the first time into
   the system, then if the inquiry converts, then we go into the client database, check if the
   client already exists..."* — already implemented, matches the transcript word for word.
9. **A real confusion surfaced and was resolved on the call.** Someone had conflated the BOQ/
   quotation module with `rfq2boq` (a separate, independent product) because a problem statement
   was copied from the wrong starting point. Viraj corrected this directly: *"you and rfq2boq is
   separate and this thing is separate."* **This is already respected** — CLAUDE.md's domain
   rules explicitly say "never call rfq2boq directly (independent product)," and no code in this
   repo does.
10. **Architecture sharing logistics** — Viraj asked for the architecture overview in text/
    screenshot form to forward to the IT person for their own review before the con-call. This is
    a live action item, separate from `docs/IT_BRIEF.md` (which is the direct message *to* IT) —
    Viraj also wants something forwardable *through him* first.

## What this re-read changes vs. what was already documented

Nothing factually new for the technical model — ADR-0002 and ADR-0003 already captured the
chain logic and infra requirements correctly from this same transcript. What this pass adds:
- Explicit confirmation, in Viraj's own words, that the five-module scope (wave-9/10) was the
  right target — no scope correction needed.
- A clearer read on point 7 (communication style) — already being followed in this project's
  question-asking pattern (closed, specific questions with a stated default), but now the
  rationale is on record in case a future session second-guesses that approach.
- Point 10 is a genuine action item that hadn't been separately tracked: Viraj wants an
  architecture overview he can forward to IT himself, *in addition to* IT receiving the direct
  brief. See action list below.

## What's genuinely still open (from this transcript, not resolved by code)

| # | Item | Who owns resolving it | Status |
|---|------|------------------------|--------|
| 1 | Excel→ERP data migration owner — no single person currently has authority over the live-edited OneDrive data | Viraj | Still unresolved as of this transcript; wave-13 built the *tool*, this is a separate go-live/organizational decision (see ADR-0002 open item #4) |
| 2 | Whether the server is actually Windows (Viraj said 99%, not 100%) | IT person | Confirm on the IT call — first question, even before the 8 in `docs/IT_BRIEF.md` |
| 3 | Architecture overview in shareable text/screenshot form, for Viraj to forward to IT before the con-call | You (Srujan) | Action item below |

## Action items, in order

1. **Send `docs/IT_BRIEF.md` to the IT person** (already drafted, ready).
2. **Separately, send Viraj a short shareable architecture summary** (text or a simple diagram
   image) he can forward to IT on his own, per his explicit request in the transcript (point 10
   above). This is smaller and more visual than the full IT brief — a one-screen version of
   Part 3 of `docs/IT_BRIEF.md` (the 6 components: backend, frontend, database, file storage,
   background jobs, auth) plus the confirmed infra list, no lengthy business-context section.
3. **On the IT call, confirm Windows vs. Linux as literally the first question** — Viraj himself
   flagged this as unconfirmed, don't assume it going in.
4. **Do not raise the Excel migration ownership question to Viraj again as an open-ended ask.**
   Per point 7, frame it as a closed decision request: e.g. "Wave-13 built the import tool. For
   go-live, should [specific named person] run it, or should I? I need one name, not a process."
