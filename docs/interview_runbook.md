# Interview Runbook — SWA ERP

> **Role:** How to ask questions that get answered. Part of the front-door set — start at
> [README.md](README.md).

## Why this exists

Badly-framed questions waste everyone's time. Well-framed questions get answers that actually
move the project forward. This runbook grounds its examples in **real questions asked during this
project's lifecycle** — specifically, the data questions Viraj answered in August 2026
(see `docs/decisions/0002-core-id-chain-gap.md`, §"Resolved by Viraj").

## The four real questions (used as worked examples)

These are not hypothetical. They were asked, answered, and the answers shaped the codebase.

---

### Q1: "What's the 4th Service Agreement type?" — BADLY FRAMED

**What was asked (badly):** "We have IESK, APEX, Inner as three SA types. What's the 4th?"

**Why it was badly framed:**
- Premise was wrong. APEX and INNER are **client names**, not agreement types.
- The verbal shorthand "IESK=12, APEX=0.12, Inner=0.9" from Meeting 1 was legacy spoken code,
  not what's actually in the live sheets.
- Asking for a "4th type" presupposed an enum that doesn't exist.

**What a well-framed version would look like:**
> "The Service Agreement sheet has a `service_name` column. Looking at the actual `.xlsx`, what
> values appear in that column? Is there a fixed set, or is it free-text? And is INSUDESIGN one
> of those values?"

**Viraj's actual answer:** APEX and INNER are client names. INSUDESIGN is the service name.
`service_name` stays free-text. No 4th-type enum.

**Lesson:** When a question presupposes a structure (enum, list, categories), verify the structure
exists before asking what fills it. Read the actual source data first.

---

### Q2: "Do reference IDs reset yearly?" — WELL FRAMED

**What was asked (well):** "Do the `SWA-{year}-XXX-NNN` reference IDs reset to 001 each calendar
year, or do they continue across years?"

**Why it was well framed:**
- The ID scheme was already confirmed (`SWA-{year}-{3-letter-code}-{seq:03d}`).
- The question was about a specific behavioral detail (reset vs continuous), not about the structure.
- It was grounded in the actual ID format already in place.

**Viraj's answer:** Yes — reset every year, everywhere. `SWA-2025-SA-011` in 2025 →
`SWA-2026-SA-001` in 2026. Same rule on all sheets / entity types.

**Lesson:** Ask about behavior once the structure is pinned down. Be specific about the edge case
you're asking about (cross-year boundary).

---

### Q3: "What is `LDI-*`? Is there a Leads sheet?" — BADLY FRAMED → WELL FRAMED

**What was asked (badly, first pass):** "The `First Lead ID` column uses `LDI-*` format. Is there
a Leads module we need to build? What's the Leads sheet?"

**Why it was badly framed:**
- Assumed a Leads sheet existed because a column referencing it appeared in the data.
- Assumed `LDI-*` meant a new entity to model.
- The assumption drove a modeling decision (First Lead ID column on Client) that later had to be
  reversed.

**What a well-framed version would look like:**
> "The Client sheet has a `First Lead ID` column with values like `LDI-2025-001`. I don't see a
> Leads sheet among the 21 source files. Is this column still relevant? Should we model Leads as
> a separate entity, or is LDI a legacy ID format for something that already exists (like Inquiry)?"

**Viraj's answer:** No Leads sheet (removed). Follow-up: remove Lead ID columns everywhere; do not
keep even for historical values. LDI is a legacy/alternate ID scheme for the same concept Meeting 1
calls "Inquiry (ML)" — not a new entity.

**Lesson:** When you see a reference to something that doesn't exist in the source data, ask whether
the reference is still live or is a historical artifact. Don't model entities based on column names
alone.

---

### Q4: "There's no Leads sheet?" — THE ABSENCE ITSELF IS A GOTCHA

**What happened:** The project team assumed a Leads sheet existed because:
1. `First Lead ID` column appeared on the Client sheet.
2. `LDI-*` values looked like a structured ID scheme.

But among the 21 source `.xlsx` files, there was no Leads sheet. The `LDI` codes were a legacy
alternate ID format for Inquiry, not a separate entity.

**Why this matters as an example:**
- This is a classic "invented entity" trap: seeing a foreign-key-like column and assuming the
  referenced table exists.
- The fix wasn't adding a Leads module — it was removing the Lead ID column entirely (migration
  `0030_drop_first_lead_id.py`).
- The importer was changed to ignore Excel "First Lead ID" on import.

**Lesson:** When a column references something you can't find in the source data, the answer might
be "it doesn't exist" rather than "you haven't found it yet." State the absence explicitly and ask
for confirmation rather than building toward a presumed structure.

---

## What makes a question well-framed

1. **Grounded in evidence.** You've read the actual files/data, not just summaries or verbal
   shorthand.
2. **Structure before content.** You've confirmed the structure (enum vs free-text, entity vs
   column, sheet exists vs doesn't) before asking what fills it.
3. **Specific edge case.** You're asking about a specific behavior (reset vs continuous, nullable
   vs required) rather than a broad "how does this work?"
4. **Absence stated explicitly.** If you can't find something, say "I looked in X and didn't find
   it — is it elsewhere, or does it not exist?" Don't silently assume it exists.
5. **One question at a time.** Don't bundle "what is X, is there a Y, and should we build Z" into
   one question. Each deserves its own answer.

## What makes a question badly-framed

1. **Presupposes a structure that may not exist.** "What's the 4th type?" presupposes 4 types.
2. **Relies on verbal shorthand.** "IESK=12" was spoken shorthand, not sheet data.
3. **Assumes entities from column names.** "First Lead ID" → assumed Leads module.
4. **Multi-part questions bundled together.** Can't get a clean answer when the question spans
   structure, behavior, and implementation.
5. **You haven't looked at the source.** If the actual `.xlsx` or code would answer it, read that
   first.

## How to use this runbook

- Before asking Viraj (or any stakeholder) a data question: read the actual source files first.
  Check `resources/ERP_Sheets_Extracted/` for sheets, check the code for current modeling.
- When framing the question: state what you've already verified, what you're unsure about, and
  whether you're asking about structure, behavior, or implementation.
- When documenting the answer: put it in an ADR (`docs/decisions/`) or in
  `docs/decisions/0002-core-id-chain-gap.md`-style Q&A table, not just in a handoff or chat log.
