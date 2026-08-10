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

## Resolved by Viraj (2026-08) — data questions Q1–Q3

Answers received from Viraj (verbatim summary locked here for future sessions):

| # | Question | Viraj's answer | How the system implements it |
|---|----------|----------------|------------------------------|
| 1 | 4th Service Agreement type / INSUDESIGN? | **APEX and INNER are client names**, not agreement types. **INSUDESIGN is the service name.** Earlier verbal "IESK / APEX / Inner as three SA types" was a misread. | `service_name` stays free-text (not an enum). No 4th-type enum. INSUDESIGN is a valid service product name. |
| 2 | Yearly ID sequence reset? | **Yes — reset every year, everywhere.** Example: `SWA-2025-SA-011` in 2025 → `SWA-2026-SA-001` in 2026. Same rule on all sheets / entity types. | Already built: `reference_counters` is keyed by `(entity_type, year)`; new calendar year starts at `001`. No code change required. |
| 3 | What is `LDI-*` / Leads? | No Leads sheet (removed). **Follow-up: remove Lead ID columns everywhere; do not keep even for historical values.** | **No Leads module. No `first_lead_id` column. Importer ignores Excel "First Lead ID". Migration `0030` drops residual DB column.** |

## Implementation status (2026-08-11)

**Lead ID — REMOVED (final, Viraj instruction):**
- Do **not** store `LDI-*` / First Lead ID anywhere (not even historical)
- Excel column "First Lead ID" is **ignored** on import
- New work is **Inquiry only** (`SWA-{year}-INQ-…`)
- Migration `0030_drop_first_lead_id.py` applied (single head)

**Still open:**
| # | Question | Status |
|---|----------|--------|
| 4 | Excel → ERP migration owner (dev vs internal admin)? | Still organizational — Viraj decides who runs real import at go-live. |
| 5 | Compliance standard versions (NBC/ECBC/IGBC/IS years)? | Cosmetic; no code blocked. |
| 6 | GST on invoices? | Shipped and verified (wave-7 / wave-11). |
| 7 | Client portal timing? | Explicitly deferred — out of MVP scope. |

## How to apply

Wave-9+ already use `SWA-{year}-{TYPE}-{seq}` with per-year counters and free-text
`service_name`. Viraj's answers **confirm** those defaults — they do not reverse them.
Remaining go-live work is IT deploy answers + real Excel migration ownership (item #4).
