# SWA ERP — Master Meeting Record (Meeting 1 + Meeting 2, consolidated)

**Status:** This is the single source of truth for what the client actually said, wanted, and
decided across both meetings. It replaces `meeting 1.md`, `meeting 2.md`, `MEETING_1_CLEAN.md`,
and `MEETING_2_CLEAN.md`, which are archived (not deleted) at `docs/historical/meetings/` for
exact original wording if ever needed. This file was built by re-reading the raw transcripts
directly — the earlier "CLEAN" summaries had flattened or dropped real detail (see
`docs/decisions/0002-core-id-chain-gap.md` for the specific corrections that resulted).

Every section below distinguishes **what was decided** from **what was said but left open** from
**how it was said** (tone/reasoning, verbatim, where it changes how you should act on it).

---

## MEETING 1 — Client Flow & Document Reference System

**Participants:** Viraj (founder), Balram (team), Software Engineer (dev)
**Purpose:** Document the current manual (Excel-based) flow for client onboarding, document
reference generation, token IDs, and how the 20+ sheets relate to each other.

### 1. The core flow, as the client actually described it (paraphrased from the raw recording)

> "First of all, inquiry came, and then converted into client... based on client's requirement,
> we generated a specific document based on work... if IESK came through any work, then we go
> into tokens... token ID... document reference number. First of all we generate document
> reference number... each ID has a specific flow."

```
Inquiry (ML — Marketing Lead)
    ↓
Client Created → Client ID generated
    ↓
Service Agreement Selected (1 of 4 known types)
    ↓
Agreement ID assigned (per client source)
    ↓
Token Number Sheet → Continuous token sequence
    ↓
Document Reference Number (DBR/KDR/Reforge/PRN/GED/CON...) → Continuous per type/shared counter
    ↓
Document Generated (Word) → Sent to Client
    ↓
Time Log Entry (Hours worked) → Dashboard
```

Additional detail from the raw recording not present in the earlier clean summary: the flow
described here is what the team does *manually today*, and Viraj said directly — **"we are
doing this flow in live. Currently we are doing this flow, but the final flow decided by
Viraj."** This is an important tone signal: what's described is the *current, ad-hoc* process,
not a finalized spec. Treat every field/format below as "how it's done today," subject to
Viraj's final word, not as immutable requirements.

### 2. Key entities & ID formats (as described verbally in Meeting 1)

| Entity | ID format (as spoken) | Source | Notes |
|--------|------------------------|--------|-------|
| Client | Auto-generated | On inquiry → client conversion | Primary key |
| Agreement | Numeric shorthand (12, 0.12, 0.9) | Pre-defined per source | "IESK=12, APEX=0.12, Inner=0.9, [4th unnamed]" — **superseded**: real sheet data (see §6 below) shows the *actual* live ID format is `SWA-{year}-SA-{seq}`, not these numbers. The numeric codes are legacy verbal shorthand the team still uses out loud, not what's in the current system of record. |
| Token | Continuous (spoken example: "1801, 1802...") | Token Sheet | Described as year-aware ("1801 = previous year") — **superseded**: real sheet shows `SWA-2025-TKN-001` format. See §6. |
| DBR | Continuous (spoken example: "138, 139...") | DBR Sheet | Design Basic Report |
| KDR | Continuous, **shares the same counter as DBR** | Same sequence | Confirmed directly: *"if it is KDR, then we'll also put 139... number is continuous"* — this specific fact (shared counter) held up against the real sheet data and is implemented as designed. |
| Reforge | `INNN074`-style | Reforge Sheet | Certification projects — exact format still not fully confirmed (see open items) |

**Document type codes**, described later in the same meeting during a live document-sheet
walkthrough (this detail was in the raw recording but missing from the clean summary): three-
letter codes exist for different document types — **PRN, DBR, GED** — where GED is "standard
assembly drawing or GA drawing," and CON/DBR both refer to a "design basis report." The document
type list is **richer than just DBR/KDR/Reforge** — treat `document_type` as free text, not a
fixed enum (already corrected in the implementation, see ADR-0002 item #5).

### 3. Sheet relationships (Primary/Foreign Keys) — how the client thinks about their own data

```
Segmentation Sheet (source of the inquiry/lead)
    │
    ├─→ Agreement ID Sheet (FK: Agreement ID)
    │       │
    │       └─→ Token Sheet (FK: Agreement ID + Token #)
    │               │
    │               ├─→ DBR Sheet (FK: Token # → DBR #)
    │               ├─→ KDR Sheet (FK: Token # → KDR #)
    │               ├─→ Reforge Sheet (FK: Reforge ID → DPR Sheet)
    │               │       └─→ Time Log Sheet (FK: Reforge ID → Hours)
    │               │
    │               ├─→ DRM Sheet (FK: Token #)
    │               ├─→ Bangalore Sheet (FK: Token #)
    │               └─→ Western Utility Sheet (FK: Token #)
    │
    └─→ Independent Sheets (no FKs)
            ├─→ HR/Admin Sheet (restricted)
            ├─→ Employee Satisfaction (restricted)
            ├─→ Finance Sheet (founder only)
            └─→ Client Satisfaction / Complaints (dropped from MVP)
```

**Core 4 sheets carry ~80% of all entries:** Segmentation, Token, DBR/KDR, Time Log.
**Linked but secondary:** DRM, Bangalore, Western Utility, Reforge/DPR.
**Independent (access-restricted):** HR, Finance, Satisfaction.
**Explicitly dropped from MVP:** Client Satisfaction, Complaints.

### 4. Access control matrix — maps directly to the RBAC roles already built

| Sheet / Function | Current (manual) restriction | Mapped role in the ERP |
|-------------------|-------------------------------|--------------------------|
| Segmentation (lead entry) | All | PM, Designer |
| Agreement ID lookup | All | PM |
| Token generation | All | PM |
| DBR/KDR generation | All | PM, Designer |
| Reforge/DPR | Certification team only | Auditor, Designer |
| Time Log (hours) | Owner only | PM, Designer (own entries), Admin (all) |
| HR/Admin | HR only | Drop from MVP / Admin-only if ever added |
| Finance | Founder only | Admin only |
| Employee Satisfaction | HR | Drop from MVP |
| Client Satisfaction | — | Drop from MVP |
| Client Complaints | — | Drop from MVP |

### 5. Time Logging — as currently done, manually

- Per token/project: Date, Token ID, Description, Website/Reference, Hours worked (example
  given: "2-3 hrs")
- Currently stored in a personal sheet called **"My Dashboard"**
- Future intent (not yet built, explicitly deferred): auto-calculate available hours, efficiency
  metrics per employee

### 6. Sustainability metrics — explicitly framed as future/optional

> "In future, we are planning to do like... first time with the metrics when the client figures
> out the ID... sustainability metrics is like project sustainability — carbon savings, initial
> savings or energy savings, insulation efficiency, and payback period, lifecycle assessment."

Confirmed built in wave-10. Fields corrected against the real sheet during implementation (Yes/
No compliance flag, months not years, ratio not percentage — see ADR-0002 item #7).

### 7. Open decisions Viraj was explicitly asked for, at the end of Meeting 1

| Decision | Options given | Impact | Status as of this writing |
|----------|----------------|--------|-----------------------------|
| 4th Agreement ID | What is it? (IESK/APEX/Inner known, 4th unnamed) | Data model | **Still open** — real sheet sample data doesn't resolve it either (see ADR-0002 open item #1) |
| Independent sheets | Drop HR/Finance/Satisfaction/Complaints from MVP? | Scope | **Resolved: yes, drop them** (confirmed again in Meeting 2, §3 below) |
| Access control | Map the matrix above to RBAC roles? | Auth design | **Resolved** — done, table in §4 above matches implementation |
| Token year reset | Annual reset (1801→2001) or continuous? | DB schema | **Still open** — implementation keeps this as a one-line config change, not hardcoded (ADR-0002 item #2) |
| DBR vs KDR sequence | Shared counter confirmed? | DB schema | **Resolved: yes, shared**, confirmed verbatim in the recording |
| Reforge ID format | `INNN074` fixed pattern? | Validation | **Still open** — not strictly validated in code, stored as free text pending confirmation |
| Sustainability metrics | Required in which wave? | Timeline | **Resolved: wave-8/10-equivalent**, i.e. after the core chain, matches "future" framing |

### 8. Verbatim pain points — why this project exists, in the client's own words

> "We are doing this flow in live. Currently we are doing this flow, but the final flow decided
> by Viraj."

> "I need clear documentation... how to proceed further. Like I should know how to do this, in a
> way of a website or any workflow."

> "I have understood the problem and I can do this, but I need that clear documentation."

**Read on this:** the client isn't asking for a redesigned process — they're asking for their
*existing* process, which currently only exists as tribal knowledge plus scattered Excel sheets,
to be turned into software with the same logic. This ERP *is* that documentation and workflow
automation. Every design decision should default to "match what they already do," not "improve
on it," unless explicitly told otherwise.

---

## MEETING 2 — Infrastructure, Architecture & Module Scope

**Participants:** Viraj (founder), Balram (team), IT person (pending introduction at time of
this meeting), dev
**Purpose:** Finalize infrastructure, confirm module scope, align on data migration ownership.

### 1. Production infrastructure — confirmed, with one caveat

> **Note (2026-08-07):** "Confirmed" below = the client confirmed these are the intended
> **target** decisions, not that they're built today. In the current code, file storage is a
> local `uploads/` dir and there is no Celery worker (see `HIERARCHY.md`); MinIO and Celery
> remain target-state.

| Item | Decision | Confidence |
|------|----------|------------|
| OS | Windows Server, on-prem | Viraj: **"99% confident it's Windows only"** — not 100%. Confirm on the IT call, don't assume. |
| RAM | 128 GB, extendable | Confirmed, "not an issue" |
| Current load | File storage only; some RDP sessions | Confirmed |
| Capacity | IT said it can handle 100+ concurrent users | Confirmed (per IT, secondhand via Viraj — verify directly with IT) |
| Network | VPN access; app reached via a shortcut in user folders | Confirmed |
| Database | PostgreSQL | Viraj: **"I need, whatever you're willing to do, I'm okay with that... I can do anything"** — this was Viraj explicitly deferring the technical decision, not specifying Postgres himself. Postgres was the dev's proposal, accepted without pushback. |
| File storage | MinIO (S3-compatible), same server | Confirmed |
| Containerization | Docker Desktop on Windows Server | Confirmed, pending IT's confirmation of feasibility (see `docs/IT_BRIEF.md`) |
| IT contact | Viraj to introduce the server admin for a con-call | **This call is what `docs/decisions/0003-it-server-call-brief.md` and `docs/IT_BRIEF.md` prepare for** |

Action stated at the time: schedule a con-call with IT to finalize Postgres+Redis on Windows
(via Docker), MinIO setup, Celery worker as a Windows service, and backup strategy (daily DB
dump, weekly file backup).

### 2. Application architecture (as proposed by the dev, accepted by Viraj without changes)

```
Browser (React) → FastAPI (Python 3.11) → PostgreSQL
                                    ↘ Redis (Celery broker)
                                    ↘ MinIO / Local FS (uploads)
```

- Internal REST APIs only — Viraj asked directly whether the APIs were paid/external; answer:
  no, all internal, calling between the app's own interconnected data, not third-party services.
- Auth: JWT (HS256 dev / RS256 prod) + RBAC
- Background jobs: Celery + Redis (email, PDF generation, reports)
- PDF: WeasyPrint (HTML→PDF)
- Excel import/export: openpyxl
- **Deliberately not a single master database serving everything cross-project** — when asked
  "are you creating a master database?", the dev explained keeping things separate so a crash in
  one place doesn't take down everything else. Viraj's reaction: **"Interesting choice"** —
  accepted, not challenged further.

### 3. Module scope — 5 modules for MVP, confirmed directly by Viraj

> "For the five modules, I'm like I would recommend the client's inquiries and the service
> agreements and the tokens and the projects... I am already doing five, like clients, inquiries,
> service agreements, tokens and projects... I think one module requires document referencing and
> time logging."

| Module | Status at meeting time | Notes |
|--------|--------------------------|-------|
| Inquiries | Claimed done (later found incomplete — see below) | ML → Client conversion |
| Service Agreements | Claimed done (later found incomplete) | Annual contracts per client |
| Tokens | Claimed done (later found incomplete) | Continuous numbering, Agreement ID link |
| Projects | Done | Lifecycle: Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed |
| Document Referencing + Time Logging | Next up at meeting time | Per-project + non-project (R&D, Marketing) work |

**Important correction, found later (2026-07-20) when the actual codebase was checked against
this claim:** despite this table showing Inquiries/Agreements/Tokens as "done" at meeting time,
none of those three existed as real database models in the code — what existed was a generic
Client/Project CRM. This gap is fully documented and closed in
`docs/decisions/0002-core-id-chain-gap.md` and wave-9. Recorded here so the history is honest:
the meeting-time status table was optimistic/inaccurate, not malicious — likely conflating
"Client and Project exist" with "the full chain exists."

**Explicitly agreed in this meeting:**
- ✅ 5 modules for MVP (table above)
- ❌ Client Complaints & Satisfaction → drop from MVP (reconfirms Meeting 1 §7)
- ❌ Independent sheets (HR, Finance, Marketing, R&D) → drop from MVP, or a separate app entirely
- ✅ Focus only on the **interconnected chain**: Inquiry → Client → Agreement → Token → Project →
  Doc Ref → Time Log

### 4. The core conversion logic — stated precisely, this is the exact business rule

> "We inquire the first time into the system, then if the inquiry converts, then we go into the
> client database, check if the client already exists. If the client exists, we go to the
> project and add the project, and the inquiry got converted into a project. And if the client
> does not exist, we first add the client details and then go to the project and add the
> project."

This is the single most load-bearing sentence in either meeting for the data model — it defines
exactly what "converting an inquiry" means (check-existing-client-first, always land on a
Project), and it was initially mis-implemented as "always create a new client" before being
corrected. Implemented correctly in wave-9 task 01.

Also stated in the same breath: **time logging and document referencing also happen outside
project scope** — for marketing work, R&D work, non-project internal work. The data model
supports this (nullable project linkage on Token/DocumentReference), but no marketing/R&D UI is
in scope per the drop-list in §3.

Sustainability metrics are explicitly **post-project**: *"sustainability is like after the
project completes, we have to make the metrics for what all impact it has created."*

### 5. Service Agreements & Tokens — the actual business logic behind them

> "For a limited number of clients... what happened was that we signed a service agreement for
> an entire year, and it would be like not project-by-project engagement, but an entire year
> engagement. And then the token would be what the applicable unit is."

Plain-language translation: a Service Agreement is a retainer — one client, one year, not tied
to a single project. A Token is the unit of billable/trackable work requested under that
retainer (e.g., "run this calculation," "submit this report") — many Tokens can exist under one
Agreement over the year.

### 6. The Document Reference Sheet — walked through live on screen

This is where the most granular detail lives, and it's the part most likely to be missed by a
summary — captured here directly:

> "Serial number and date... print number, we have three-letter codes for different types of
> documents. So PRN or DBR or GED. And then the concatenated project or token ID, that is the
> foreign key, the primary key of this database. So the three-letter code can be different, but
> every new entry would be 1, 2, 3, 4, serial number-wise."
>
> "CON and DBR are like a design basis report... GED is standard assembly drawing or GA drawing."
>
> "Document type — is it for research purpose, presentation, interview purpose, or a submittal
> for a project — that's kept, but it's not necessary, just categorization for analysis."
>
> "The user of the document — is it for something we're making internally, then for whom — we're
> not sure to have it or maybe remove it. No implications of this data in any further, no
> dependence on this data on any other data."
>
> "In the DRN [Document Reference Number sheet], we have written unit document numbers, that's
> the primary key. And associated project ID is from the project sheet itself."

**What this confirms, precisely:**
- Document Reference's primary FK target is the **Project** (Viraj's own words: "associated
  project ID is from the project sheet itself") — this directly supports the corrected design in
  ADR-0002 item #4 (project_id required, token_id optional), rather than the first draft's
  token-only linkage.
- The "User" field is explicitly **uncertain even to the client** ("we're not sure to have it or
  maybe remove it") — treat as optional/free-text, never required, and don't over-engineer
  validation on it.
- Document type categorization ("research/presentation/interview/submittal") is explicitly
  **not load-bearing** ("not necessary, just categorization for analysis") — confirms free-text
  is the right modeling choice, not an enum with business logic attached.

### 7. Data migration — stated as a real, still-unresolved problem

> "I should know who owns the data migration from Excel to ERP... who has all this... we should
> convert all this data into this ERP platform, no?"
>
> "We have everyone, like everyone has answers to the data as of now. Because right now it's
> hosted on OneDrive itself. So we cannot have the read-only version... because right now it's
> just been three months or so [since starting]."

**Read on this:** there is no single data owner today, the source data is live and multi-editor,
and there's no way to freeze/snapshot it for a clean one-time migration yet. This is not a
technical problem — wave-13 already built the import tool. It's an organizational decision only
Viraj can make: who gets named as the person who runs the real migration, and when the source
data gets frozen. **Still open as of 2026-07-20.**

### 8. Wave progress, as demoed live in this meeting

**Backend tests:** 97/97 passing (at meeting time — later independently re-verified with a much
larger and different actual count once waves 4-13 landed; see
`work/reports/wave-12/01-independent-verification.report.md`).
**Frontend:** flagged as having TypeScript errors to fix at meeting time (Badge import, unused
vars, type mismatches) — resolved in wave-11.

### 9. A real confusion that surfaced and was corrected on the call

Someone had built part of the BOQ/quotation module by copying a problem statement that actually
belonged to a *different, separate product* called rfq2boq. Viraj caught this directly:

> "I have seen in those BOQ transformations... I think this came from the statement at the
> starting... I don't know how the communication happened with you guys, but you and rfq2boq are
> separate and this thing is separate."

**Already enforced going forward**: `CLAUDE.md`'s domain rules explicitly state "never call
rfq2boq directly (independent product)" — this rule exists *because of* this exact incident.

### 10. Communication-process feedback — read this section carefully, it governs how to work with Viraj

This is the most consequential part of Meeting 2 for how work should be scoped and questions
asked going forward. Verbatim:

> "It's not your whole assignment, you'll get a little problem statement step by step what you
> need to do, right? It's not your, like, MBA classes that it's their project. Now they still
> want something specific — like you cannot generally say 'give me everything to do and I'll do
> it step by step.' Somewhere you have to do your brain and figure it out."

> "From a communication point of view, if you can point by point ask me, 'can you give answers to
> these questions that I have' — that can be dealt with. But superlatively, I don't know what
> exactly you want and what can be shared. You can share a list of questions if you have."

**What this means concretely, going forward:**
- Never ask Viraj (or IT) an open-ended "what should we do" question when the answer is
  derivable from existing meeting notes, sheet data, or code inspection — do that work first.
- When something genuinely can't be resolved without him (a business decision like the 4th
  agreement name, or a fact only IT knows like which ports are free), ask a **specific, closed,
  answerable question**, ideally with a stated default/assumption already in place so he can
  just confirm or correct it rather than starting from a blank page.
- This is exactly the shape `docs/decisions/0002-core-id-chain-gap.md`'s open-questions table and
  `docs/IT_BRIEF.md` are built in — each item is closed-form, not "tell me everything."

### 11. Architecture sharing — a real, standalone action item

Viraj asked for the architecture overview in text or screenshot form so **he can forward it to
IT himself**, ahead of / alongside the direct IT con-call:

> "Can you share this architecture overview just in text format, or a screenshot, then we can
> forward it and ask for their comments, because they do app development for us, so we can ask
> them."

**This is distinct from `docs/IT_BRIEF.md`** (which is written to be sent *directly* to IT).
Viraj wants a shorter, forwardable version he controls sending himself. **Not yet produced** —
see action items below.

### 12. Immediate action items stated in the meeting

| Item | Owner | Deadline (as stated) |
|------|-------|------------------------|
| Schedule IT con-call | Viraj | "This week" |
| Share the 20 Excel files | Balram | ASAP |
| Confirm migration owner | Viraj | Before Wave-4 (**still open**, see §7) |
| Confirm drop list (independent sheets) | Viraj | Before Wave-4 (**resolved: yes, drop**) |
| Provide full Agreement ID list (the 4th type) | Viraj | Before Wave-4 (**still open**) |
| Share compliance standard versions (NBC/ECBC/IGBC/IS years) | Viraj + Auditor | Before Wave-6 (**still open, no code blocked on it**) |
| GST invoicing requirement | Viraj + Finance | Before Wave-7 (**needs a quick verification the shipped invoice module actually includes it — see wave-11 report**) |

---

## What's still genuinely open, across both meetings (single consolidated list)

1. **4th Service Agreement type/name** — never resolved verbally or in the real sheet data.
2. **Token/reference-ID annual reset behavior** — implemented as a config-level choice, not
   hardcoded, pending confirmation either way.
3. **Reforge ID exact format** (`INNN074`) — stored as free text pending confirmation.
4. **Excel → ERP migration owner** — an organizational decision, not a technical one; still no
   named owner as of the last meeting.
5. **Windows vs. actual OS confirmation** — Viraj said 99%, not 100%; confirm on the IT call.
6. **Compliance standard versions** (which NBC/ECBC/IGBC/IS years) — cosmetic, no code blocked.
7. **Architecture summary for Viraj to forward to IT himself** — requested, not yet produced.

---

## Where the rest of the source material lives

- `resources/EXCEL_SHEETS_INVENTORY.md` — sheet-by-sheet wave mapping (kept, still current)
- `resources/ERP_Sheets_Extracted/ERP Sheets/*.xlsx` — the actual real source data (kept; this
  is what resolved several of the "open questions" above into confirmed facts — see
  `docs/decisions/0002-core-id-chain-gap.md`)
- `resources/ERP Structure.zip` — original zip the sheets were extracted from (kept)
- `docs/historical/meetings/` — the original raw transcripts and earlier clean summaries,
  archived for exact original wording if ever needed; this file supersedes them for day-to-day
  reference
