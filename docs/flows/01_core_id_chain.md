# Flow: Core ID Chain End-to-End

The intellectual core of this project. The client's actual workflow (Meeting 1 + Meeting 2),
NOT a generic CRM.

**Status:** BUILT — all entities and API endpoints exist.

---

## Overview

```mermaid
flowchart LR
    INQ[("Inquiry<br/>SWA-{year}-INQ-{seq:03d}")] -->|convert| CLIEST{"Client exists?"}
    CLIEST -->|No| CLT[("Create Client<br/>SWA-{year}-CLT-{seq:03d}")]
    CLIEST -->|Yes| REUSE[("Reuse existing Client")]
    CLT --> PROJ[("Project<br/>SWA-{year}-PRJ-{seq:03d}")]
    REUSE --> PROJ
    PROJ --> SA[("Service Agreement<br/>SWA-{year}-SA-{seq:03d}")]
    SA --> TKN[("Token<br/>SWA-{year}-TKN-{seq:03d}")]
    TKN --> DRN[("Document Reference<br/>SWA-{year}-DBR-{seq:03d}<br/>DBR/KDR share counter")]
    DRN --> TIME[("Time Log<br/>15-min increments")]
    TIME --> INV[("Invoice / GST<br/>wave-18 built")]
    INV --> SUST[("Sustainability<br/>metrics")]
```

## Step-by-step

### 1. Inquiry (SWA-{year}-INQ-{seq:03d})

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8100
    participant S as inquiry_service
    participant RID as reference_id_service
    participant DB as PostgreSQL

    C->>A: POST /api/inquiries
    A->>A: JWT auth → get_current_user()
    A->>S: inquiry_service.create_inquiry(db, actor_id, data)
    S->>RID: generate_reference_id(db, "INQ")
    RID-->>S: "SWA-2025-INQ-001"
    S->>DB: INSERT inquiries (reference_id, ...)
    DB-->>S: row
    S-->>A: InquiryRead
    A-->>C: 201 Created
```

**Endpoint:** `POST /api/inquiries` — `inquiries.py:12`

**Fields from real Inquiries Sheet.xlsx:** Sr No, Inquiry ID, Inquiry Date, Inquiry Type,
Inquiry Source, Client Name, Requirement Summary, Estimated Value, Priority, Status, Owner,
Technical Lead, Notes.

**Reference ID:** `SWA-{year}-INQ-{seq:03d}`, atomic per-year counter.

---

### 2. Client (SWA-{year}-CLT-{seq:03d})

Client creation happens two ways:
1. Directly via `POST /api/clients` (CRM entry)
2. Via Inquiry conversion (`POST /inquiries/{id}/convert`)

**Conversion flow (from client's own words, Meeting 2 transcript):**

> "we inquire the first time into the system, then if the inquiry converts, then we go into the
> client database, check if the client already exists. If the client exists, we go to the project
> and add the project... If the client does not exist, we first add the client details and then
> go to the project and add the project."

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8100
    participant S as inquiry_service
    participant CS as client_service
    participant PS as project_service
    participant DB as PostgreSQL

    C->>A: POST /inquiries/{id}/convert
    A->>A: JWT auth
    A->>S: inquiry_service.convert_inquiry(db, inquiry_id, data)
    S->>DB: SELECT * FROM clients WHERE name = inquiry.client_name
    alt Client found
        DB-->>S: existing client row
        S->>PS: project_service.create_project(db, client_id, data)
        PS->>DB: INSERT projects (...)
        Note over S,DB: Skip client creation — reuse existing
    else Client not found
        DB-->>S: no rows
        S->>CS: client_service.create_client(db, {name, first_inquiry_id})
        CS->>RID: generate_reference_id(db, "CLT")
        RID-->>CS: "SWA-2025-CLT-001"
        CS->>DB: INSERT clients (...)
        S->>PS: project_service.create_project(db, new_client_id, data)
        PS->>DB: INSERT projects (...)
    end
    S->>DB: UPDATE inquiries SET status='Converted', converted_client_id, converted_project_id
    DB-->>S: updated
    S-->>A: InquiryRead(status=Converted)
    A-->>C: 200 OK
```

**Endpoint:** `POST /inquiries/{id}/convert` — `inquiries.py`

**Edge case:** If `end_date` before `start_date` → 422. Ambiguous client-name match → 300-style
response listing candidates, require `client_id` to disambiguate.

**Client fields missing from original model (patched in wave-9 migration 0017):**
- `industry: String(100)` — from real Client Sheet.xlsx
- `client_status: String(50)` — dropdown, e.g. "Dormant"
- `first_inquiry_id: FK → inquiries.id` — tracks conversion source
- `first_lead_id: String(30)` — legacy LDI-* value (IMPORTER IGNORES this column)

---

### 3. Service Agreement (SWA-{year}-SA-{seq:03d})

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8100
    participant S as agreement_service
    participant RID as reference_id_service
    participant DB as PostgreSQL

    C->>A: POST /api/agreements
    A->>S: agreement_service.create_agreement(db, actor_id, data)
    S->>RID: generate_reference_id(db, "SA")
    RID-->>S: "SWA-2025-SA-011"
    S->>DB: INSERT service_agreements (reference_id, client_id, inquiry_id, service_name, ...)
    DB-->>S: row
    S-->>A: ServiceAgreementRead
    A-->>C: 201 Created
```

**Endpoint:** `POST /api/agreements` — `agreements.py`

**Key:** `service_name` is FREE TEXT, not an enum. The real sample value from Service Agreements
Sheet.xlsx is "INSUDESIGN" — this doesn't match the verbally-named list at all. Confirms the enum
approach would be wrong on day one.

**Reference ID:** `SWA-{year}-SA-{seq:03d}`.

---

### 4. Token (SWA-{year}-TKN-{seq:03d})

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8100
    participant S as token_service
    participant RID as reference_id_service
    participant DB as PostgreSQL

    C->>A: POST /api/tokens
    A->>S: token_service.create_token(db, actor_id, data)
    S->>RID: generate_reference_id(db, "TKN")
    RID-->>S: "SWA-2025-TKN-001"
    S->>DB: INSERT tokens (reference_id, client_id, service_agreement_id, project_id, ...)
    DB-->>S: row
    S-->>A: TokenRead
    A-->>C: 201 Created
```

**Endpoint:** `POST /api/tokens` — `tokens.py`

**Reference ID:** `SWA-{year}-TKN-{seq:03d}`.

---

### 5. Document Reference (SWA-{year}-DBR-{seq:03d})

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8100
    participant S as document_reference_service
    participant RID as reference_id_service
    participant DB as PostgreSQL

    C->>A: POST /api/document-references
    A->>S: document_reference_service.create_doc_ref(db, actor_id, data)
    S->>RID: generate_reference_id(db, "DBR")
    RID-->>S: "SWA-2025-DBR-001"
    S->>DB: INSERT document_references (reference_id, client_id, project_id, token_id, ...)
    DB-->>S: row
    S-->>A: DocumentReferenceRead
    A-->>C: 201 Created
```

**Endpoint:** `POST /api/document-references` — `document_references.py`

**Key design decision (ADR-0002 #4):** The DRN sheet has TWO different header rows — one says
"Associated Project ID", another says "Associated Project/Token ID". Rather than picking one FK and
guessing wrong, DocumentReference has BOTH `project_id` (required) and `token_id` (nullable).

**Reference ID:** `SWA-{year}-DBR-{seq:03d}`. DBR and KDR share the same counter.

---

### 6. Time Log → Invoice / GST

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8100
    participant S as time_tracking_service
    participant INV_S as invoice_service
    participant DB as PostgreSQL

    C->>A: POST /api/time-entries
    A->>S: time_tracking_service.create_time_entry(db, actor_id, data)
    S->>DB: INSERT time_entries (project_id, user_id, hours, billable, ...)
    DB-->>S: row
    S-->>A: TimeEntryRead
    A-->>C: 201 Created

    Note over C,DB: Later: generate invoice from time entries
    C->>A: POST /api/invoices
    A->>INV_S: invoice_service.create_invoice(db, actor_id, data)
    INV_S->>RID: generate_reference_id(db, "INV")
    INV_S->>DB: INSERT invoices (reference_id, project_id, client_id, token_id, amount, gst_amount, total_amount, ...)
    DB-->>INV_S: row
    INV_S-->>A: InvoiceRead(with GST)
    A-->>C: 201 Created
```

**Time entries:** 15-minute increments, `billable` flag. — `time_tracking.py`

**Invoices:** GST built in wave-18 (commit 2073c36 "invoice GST"). Fields: `amount`, `gst_amount`,
`total_amount`. — `invoices.py`

---

### 7. Sustainability Metrics (SWA-{year}-SM-{seq:03d})

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8100
    participant S as sustainability_service
    participant RID as reference_id_service
    participant DB as PostgreSQL

    C->>A: POST /api/sustainability-metrics
    A->>S: sustainability_service.create_metric(db, actor_id, data)
    S->>RID: generate_reference_id(db, "SM")
    RID-->>S: "SWA-2025-SM-001"
    S->>DB: INSERT sustainability_metrics (reference_id, project_id, compliant_with_green_standards, ...)
    DB-->>S: row
    S-->>A: SustainabilityMetricRead
    A-->>C: 201 Created
```

**Endpoint:** `POST /api/sustainability-metrics` — `sustainability_metrics.py`

**Fields (corrected from first pass, wave-10):**
- `compliant_with_green_standards: Boolean` (not string)
- `payback_period_months: Integer` (not years)
- `insulation_efficiency: Float` ratio (not percentage)

---

## Reference ID scheme summary

| Entity | Code | Format | Counter |
|--------|------|--------|---------|
| Inquiry | INQ | SWA-{year}-INQ-{seq:03d} | Per-year, atomic |
| Client | CLT | SWA-{year}-CLT-{seq:03d} | Per-year, atomic |
| Service Agreement | SA | SWA-{year}-SA-{seq:03d} | Per-year, atomic |
| Token | TKN | SWA-{year}-TKN-{seq:03d} | Per-year, atomic |
| Document Reference | DBR | SWA-{year}-DBR-{seq:03d} | Per-year, shared with KDR |
| Sustainability Metric | SM | SWA-{year}-SM-{seq:03d} | Per-year, atomic |
| Project | PRJ | SWA-{year}-PRJ-{seq:03d} | Per-year, atomic |

**Generator:** `src/backend/services/reference_id_service.py:generate_reference_id(db, entity_type)`

**Counters:** `reference_counters` table, keyed by `(entity_type, year)`. Resets each calendar year.

**Confirmed by Viraj** (ADR-0002, Aug 2026): "Yes — reset every year, everywhere."

---

## BUILT vs TARGET-STATE

- **BUILT:** All 7 entities, all API endpoints, reference_id_service, atomic per-year counters,
  GST on invoices, sustainability metric fields corrected.
- **TARGET-STATE:** None — the core chain is complete.
