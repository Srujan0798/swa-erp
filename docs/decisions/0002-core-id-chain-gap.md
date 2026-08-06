# ADR-0002 — Core ID-Chain Gap (Inquiry → Agreement → Token → Document Reference)

**Date:** 2026-07-20 (revised same day — first pass relied on the sanitized meeting summaries
and the old verbal numeric codes; this revision is grounded in the raw transcripts
`resources/MEETINGS_MASTER.md` (raw transcripts archived at `docs/historical/meetings/`) and the actual source files in
`resources/ERP_Sheets_Extracted/ERP Sheets/*.xlsx`.)

## Context

Meeting 1 and Meeting 2 define the client's actual MVP as a linear chain:

```
Inquiry → Client → Service Agreement → Token → Document Reference → Time Log
```

Verified by grep: no `Inquiry`, `Agreement`, `Token`, or `DocumentReference` model exists in
`src/backend/models/`. What was built (waves 1-8) is a generic Client/Project/BOQ/Quote CRM —
useful, but not this chain. Wave-9 closes the gap.

## Resolved by reading the real source data (previously mis-modeled or left as "open")

Reading the actual `.xlsx` files (not just the sheet-name inventory) resolved several things
the first pass got wrong or left unnecessarily open:

1. **ID scheme is confirmed, not guessed.** Every entity uses `SWA-{year}-{3-letter-code}-{seq:03d}`:
   `SWA-2025-INQ-001` (Inquiry), `SWA-2025-CLT-001` (Client), `SWA-2025-SA-011` (Service
   Agreement),    `SWA-2025-TKN-001` (Token), `SWA-2025-EMP-001` (Employee). This supersedes the
   verbal "IESK=12, APEX=0.12, Inner=0.9" numeric codes from Meeting 1 — those are legacy/spoken
   shorthand, not what's actually in the live sheets. **Correction from first pass:** I had
   designed Agreement around the old numeric codes; that was wrong. Build one shared
   `generate_reference_id(db: Session, entity_type: str) -> str` service used by Inquiry,
   Client, Agreement, Token, and (extended) Project — sequential counter per type, reset per
   calendar year (the
   year is literally embedded in the ID, so continuing a `2025` sequence into `2026` would be
   self-contradictory; reset-per-year is a design inference, not itself confirmed by evidence
   spanning two years — flag to Viraj to confirm before locking in the reset behavior).
2. **The Client model already shipped is missing fields the client sheet requires.** Real
   columns: `Industry`, `Date Onboarded`, `Client Status` (dropdown, e.g. "Dormant"),
   `First Lead ID`, `First Inquiry ID`. None of these exist on `src/backend/models/client.py`
   today. This needs a patch migration, not just new tables.
3. **Inquiry→Client conversion is NOT a blind 1:1 create.** Direct transcript quote (Meeting 2):
   *"we inquire the first time into the system, then if the inquiry converts, then we go into
   the client database, check if the client already exists. If the client exists, we go to the
   project and add the project... If the client does not exist, we first add the client details
   and then go to the project and add the project."* So conversion always ends in a **Project**,
   and only conditionally creates a new Client. First pass modeled this as "Inquiry always
   creates a new Client" — wrong. Fixed in wave-9 task 01.
4. **DocumentReference's foreign key is ambiguous in the client's own data, not just
   under-specified by us.** The DRN sheet has two different header rows in the same file: one
   says `Associated Project ID`, another says `Associated Project/Token ID`, and the one sample
   data row present is internally inconsistent (a "Doc Ref No" value that looks like a document
   type code, an "Associated ID" that looks like a different scheme entirely). Rather than
   picking one FK and guessing wrong again, DocumentReference should have **both** `project_id`
   (required) and `token_id` (nullable) — matches how the client's own sheet is actually used in
   practice. First pass had `token_id` only — corrected.
5. **Document types are richer than "DBR/KDR/Reforge."** The DRN sheet's actual `Document Type`
   sample value is `"Concept Note"`, with a separate `Type` column for `"Submittal"`-style
   classification, and Meeting 1's verbal walkthrough separately mentions `PRN`, `GED` (GA
   drawing), `CON` (design basis report) as 3-letter document codes. Treat `document_type` and
   `doc_code` (the 3-letter prefix baked into the reference ID) as free-text, not a hardcoded
   DBR/KDR/Reforge enum — the real system has more categories than the summary implied.
6. **`First Lead ID` uses a `SWA-{year}-LDI-{seq}` format distinct from Inquiry's `INQ` code**,
   but there is no separate "Leads Sheet.xlsx" among the 21 source files. Working conclusion:
   `LDI` is a legacy/alternate ID scheme for the same concept Meeting 1 calls "Inquiry (ML)" —
   not a new entity to model. Treat as a historical ID-format quirk to handle in the wave-13
   importer (map old `LDI-*` values into the `Inquiry` table on import), not a new domain object.
   Flag to Viraj to confirm this reading is correct before the importer ships.
7. **Sustainability fields have different types than first modeled.** Real columns:
   `Compliant with Green Standards` (Yes/No **boolean**, not a standard-name string),
   `Payback Period (Months)` (**months**, not years), `Insulation Efficiency (Actual/Expected)`
   (a **ratio**, sample value `0.89`, not a percentage). First pass had `green_standard: str` and
   `payback_period_years` — both corrected in wave-10.
8. **Time Logging has more structure than first modeled**: `Employee Role`, `Revision` (with the
   sheet's own note: "write reason if Yes, otherwise No" — i.e. revision reason is conditionally
   required), and a `Reference ID` column explicitly documented as *"primary linkage with
   project or token or Doc etc"* — i.e. genuinely polymorphic by design, not sloppy modeling.
   Existing `time_tracking.py` (wave-7, already shipped) should be checked against this and
   patched if these fields are missing — added as a wave-11 follow-up item, not blocking wave-9.

## Still genuinely open — need Viraj's answer, no reliable default exists in the data

| # | Question | Why the data doesn't resolve it |
|---|----------|----------------------------------|
| 1 | What is the 4th Service Agreement type/service name? | Sample row's `Service Name` is `"INSUDESIGN"` — doesn't match any of the 3 verbally-named agreements (IESK/APEX/Inner) or confirm a 4th. `agreement_type`/`service_name` should stay free-text, not an enum, until Viraj confirms the full list. |
| 2 | Does the yearly ID sequence actually reset on Jan 1, or run continuously across years? | Only 2025 data exists in the sample sheets; no year boundary to observe. Build the counter table so a reset policy is a config value, not hardcoded, so this is a one-line change either way. |
| 3 | Is `LDI-*` really the legacy Inquiry ID (see item #6 above), or a distinct concept that just never got its own sheet exported? | No "Leads Sheet.xlsx" exists among the 21 files to check directly. |
| 4 | Excel → ERP migration owner (dev team vs. internal admin)? | Explicitly unresolved in the Meeting 2 transcript itself — Viraj states *"we have everyone, like everyone has answers to the data as of now... it's hosted on OneDrive"* — this is not a data question, it's a still-pending organizational decision. Wave-13 builds the tool; **do not assume who runs it against real data** — that's a separate go-live decision for Viraj, not something to default silently. |
| 5 | Compliance standard versions (which NBC/ECBC/IGBC/IS years)? | Not in any sheet; cosmetic data-entry question, no code blocked on it. |
| 6 | GST invoicing required in wave-7 (already shipped)? | Meeting 2 flagged this as pending "before Wave-7" — need to confirm the shipped invoice module actually includes it; checked in wave-11. |
| 7 | Client portal timing? | Explicitly deferred in Meeting 2 ("Wave-8 or later?") — out of scope for this dispatch. |

## How to apply

Wave-9 task briefs (`work/wave-9/`) now use the confirmed `SWA-{year}-{TYPE}-{seq}` ID scheme
and the corrected field lists/FKs above. Where an item is still genuinely open (table above),
the field is free-text/nullable so answering it later doesn't require a schema rewrite — but
these should be sent to Viraj as an actual question list, not silently defaulted the way item
#4 almost was in the first pass.
