# Wave-9 Spec — Core ID Chain (Inquiry → Agreement → Token → Document Reference)

## Why this wave exists
Waves 1-8 built a generic Client/Project/BOQ/Task/Vendor/Time/Invoice CRM. The client's actual
requested MVP (`resources/MEETING_1_CLEAN.md`, `resources/MEETING_2_CLEAN.md`) is a specific
numbered-ID chain used company-wide for tracking work: Inquiry → Client → Service Agreement →
Token → Document Reference (DBR/KDR/Reforge) → Time Log. None of Inquiry, ServiceAgreement,
Token, or DocumentReference exist in the codebase (verified by grep, 2026-07-20). This wave
closes that gap. See `docs/decisions/0002-core-id-chain-gap.md` for open stakeholder questions
and the defaults used where the client hasn't answered yet.

## Scope
0. **Shared reference-ID generator** — `SWA-{year}-{TYPE}-{seq:03d}`, atomic per-type-per-year
   counter. Confirmed against real sample IDs in the source Excel sheets (not guessed). Every
   entity below uses it. See `work/wave-9/00-shared-id-generator.md`.
1. **Inquiry** — a lead captured before a Client exists. Per the client's own description of the
   flow, converting an Inquiry checks whether the Client already exists (by name) — only creates
   a new Client if not found — and always ends by creating a Project. Fields match the real
   `Inquiries Sheet.xlsx`: type, source, requirement summary, estimated value, priority, owner,
   technical lead.
2. **ServiceAgreement** — linked to a Client, `service_name` is free text (the verbal "4 agreement
   types" naming from Meeting 1 does not match the real sheet's sample data — see ADR-0002 open
   item #1, not a settled enum).
3. **Token** — sequence number issued against an Agreement via the shared generator. Unit of
   work tracking referenced downstream by documents and time logs.
4. **DocumentReference** — numbered document (`DRN`) issued against a Project (required) and
   optionally a Token. DBR/KDR share one counter (confirmed by Meeting 1 transcript); other
   document types (Concept Note, GED, PRN, etc — free text, not DBR/KDR/Reforge-only) get their
   own counters.
5. Frontend: Inquiries list/detail/convert flow (with existing-client disambiguation, not a
   blind create); Agreements tab on Client detail; Tokens list scoped to an Agreement; Document
   References list scoped to a Project with optional Token filter.

Also patches the already-shipped `Client` model (wave-2), which is missing `industry`,
`client_status`, `first_lead_id`, `first_inquiry_id` — required by the real Clients sheet and
only discovered by reading the actual source file, not the sheet inventory summary.

## Out of scope (explicitly dropped per Meeting 2)
HR, Finance (beyond existing Invoice/P&L), Employee Satisfaction, Client Complaints/Satisfaction,
Marketing metrics, Research Collaborations/Innovations.

## Dependency
Depends on wave-1 (auth/RBAC), wave-2 (Client model — Token/Agreement/Inquiry attach to it).
Independent of waves 3-8.

## Acceptance
- `pytest tests/wave-9/` passes 100%
- End-to-end: create Inquiry → convert to Client → create Agreement → issue Token → issue
  Document Reference — all via API, IDs generated correctly and sequentially.
- Token numbers never collide or skip under concurrent creation (test with parallel requests).
- DBR/KDR share one counter; Reforge has its own format validation.
