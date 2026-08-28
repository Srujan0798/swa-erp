# Flow: BOQ → Quote → Invoice

The commercial workflow: from bill of quantities through quotation to invoicing.

**Status:** BUILT — BOQ models, quote workflow, invoicing with GST all exist.

---

## Overview

```mermaid
flowchart LR
    BOQ[("BOQ<br/>Bill of Quantities<br/>SWA-{year}-BOQ-{seq:03d}<br/>line items · total_amount")] -->|review + price| QUOTE[("Quote<br/>SWA-{year}-QUO-{seq:03d}<br/>line_items · total_amount<br/>status lifecycle")]
    QUOTE -->|submit to client| SUBMITTED[("Status: Submitted<br/>→ Approved / Responded")]
    QUOTE -->|approve| APPROVED[("Status: Approved<br/>→ convert to project")]
    QUOTE -->|respond| RESPONDED[("Status: Responded<br/>client feedback")]
    APPROVED -->|generate| INV[("Invoice<br/>SWA-{year}-INV-{seq:03d}<br/>amount · gst_amount · total_amount<br/>wave-18 built")]
    INV -->|paid| CLOSED[("Status: Closed<br/>project complete")]

    BOQ -->|from project| PROJ[("Project<br/>SWA-{year}-PRJ-{seq:03d}")]
    PROJ --> BOQ
    APPROVED --> PROJ
```

---

## BOQ (Bill of Quantities)

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8100
    participant S as boq_service
    participant DB as PostgreSQL

    C->>A: POST /api/boqs
    A->>S: boq_service.create_boq(db, actor_id, data)
    S->>DB: INSERT boqs (reference_id, project_id, title, description, line_items, total_amount, status, version)
    DB-->>S: row
    S-->>A: BoqRead
    A-->>C: 201 Created
```

**Model:** `src/backend/models/boq.py`

**Fields:** id, reference_id (SWA-{year}-BOQ-{seq:03d}), project_id, title, description,
line_items (JSON), total_amount (Decimal), status, version, created_at, updated_at, deleted_at.

**Ingestion:** BOQ can be uploaded as JSON or Excel. The importer (`scripts/import_excel.py`,
wave-13) handles Excel→ERP data migration. Never call `rfq2boq` directly — it's an independent
product.

**Reference ID:** `SWA-{year}-BOQ-{seq:03d}`.

---

## Quote workflow

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8100
    participant S as quote_service
    participant DB as PostgreSQL

    Note over C,DB: Create quote
    C->>A: POST /api/quotes
    A->>S: quote_service.create_quote(db, actor_id, data)
    S->>DB: INSERT quotes (reference_id, project_id, client_id, title, description, line_items, total_amount, status="Draft", version)
    DB-->>S: row
    S-->>A: QuoteRead(status=Draft)
    A-->>C: 201 Created

    Note over C,DB: Submit quote
    C->>A: POST /quotes/{quote_id}/submit
    A->>S: quote_service.submit_quote(db, quote_id)
    S->>DB: UPDATE quotes SET status="Submitted"
    DB-->>S: updated
    S-->>A: QuoteRead(status=Submitted)
    A-->>C: 200

    Note over C,DB: Approve quote (client accepts)
    C->>A: POST /quotes/{quote_id}/approve
    A->>S: quote_service.approve_quote(db, quote_id)
    S->>DB: UPDATE quotes SET status="Approved"
    DB-->>S: updated
    S-->>A: QuoteRead(status=Approved)
    A-->>C: 200

    Note over C,DB: Respond to quote (client feedback)
    C->>A: POST /quotes/{quote_id}/respond
    A->>S: quote_service.respond_quote(db, quote_id, feedback)
    S->>DB: UPDATE quotes SET status="Responded", notes=feedback
    DB-->>S: updated
    S-->>A: QuoteRead(status=Responded)
    A-->>C: 200

    Note over C,DB: Send quote (email/notification)
    C->>A: POST /quotes/{quote_id}/send
    A->>A: send notification/email
    A-->>C: 200
```

**Model:** `src/backend/models/quote.py`

**Fields:** id, reference_id (SWA-{year}-QUO-{seq:03d}), project_id, client_id, title, description,
line_items (JSON), total_amount (Decimal), status (Draft/Submitted/Approved/Responded),
version, created_at, updated_at, deleted_at.

**Status lifecycle:**
1. Draft → Submit → Submitted
2. Submitted → Approve → Approved (client accepts)
3. Submitted → Respond → Responded (client feedback)
4. Approved → convert to project → status stays "Approved"

**Endpoints:**
- `POST /api/quotes` — create
- `PATCH /quotes/{quote_id}` — update
- `DELETE /quotes/{quote_id}` — soft delete
- `POST /quotes/{quote_id}/submit` — submit to client
- `POST /quotes/{quote_id}/approve` — client approves
- `POST /quotes/{quote_id}/respond` — client responds with feedback
- `POST /quotes/{quote_id}/send` — send (notification/email)
- `GET /quotes/{quote_id}` — read
- `GET /api/quotes` — list

**PDF export:** `GET /quotes/{quote_id}/pdf` — generates quote PDF (synchronous or async via Celery).

---

## Invoice (with GST)

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8100
    participant S as invoice_service
    participant RID as reference_id_service
    participant DB as PostgreSQL

    C->>A: POST /api/invoices
    A->>S: invoice_service.create_invoice(db, actor_id, data)
    S->>RID: generate_reference_id(db, "INV")
    RID-->>S: "SWA-2025-INV-001"
    S->>DB: INSERT invoices (reference_id, project_id, client_id, token_id, invoice_number, issue_date, due_date, amount, gst_amount, total_amount, status)
    DB-->>S: row
    S-->>A: InvoiceRead(amount=100000, gst_amount=18000, total_amount=118000)
    A-->>C: 201 Created

    Note over C,DB: Update invoice status
    C->>A: PATCH /invoices/{invoice_id}/status
    A->>S: invoice_service.update_invoice_status(db, invoice_id, new_status)
    S->>DB: UPDATE invoices SET status = ?
    DB-->>S: updated
    S-->>A: InvoiceRead
    A-->>C: 200

    Note over C,DB: PDF export
    C->>A: GET /api/reports/financial.pdf
    A->>A: generate financial PDF (sync or async)
    A-->>C: 200 PDF bytes (or 202 + job_id if async)
```

**Model:** `src/backend/models/invoice.py`

**Fields:** id, reference_id, project_id, client_id, token_id, invoice_number, issue_date, due_date,
amount (Decimal), gst_amount (Decimal), total_amount (Decimal), status, created_at, updated_at,
deleted_at.

**GST:** Built in wave-18 (commit 2073c36 "invoice GST"). `total_amount = amount + gst_amount`.

**Status lifecycle:** Draft → Issued → Paid → Closed (or Cancelled).

**Endpoints:**
- `POST /api/invoices` — create
- `PATCH /invoices/{invoice_id}/status` — update status
- `DELETE /invoices/{invoice_id}` — soft delete
- `GET /invoices/{invoice_id}` — read
- `GET /api/invoices` — list

---

## BOQ → Quote → Invoice end-to-end

```mermaid
sequenceDiagram
    participant PM as PM (React)
    participant A as FastAPI :8100
    participant BS as boq_service
    participant QS as quote_service
    participant IS as invoice_service
    participant RID as reference_id_service
    participant DB as PostgreSQL

    PM->>A: POST /api/boqs {project_id, line_items, ...}
    A->>BS: boq_service.create_boq(db, pm_id, data)
    BS->>RID: generate_reference_id(db, "BOQ")
    RID-->>BS: "SWA-2025-BOQ-001"
    BS->>DB: INSERT boqs (...)
    DB-->>BS: row
    BS-->>A: BoqRead
    A-->>PM: 201 Created { data: {...} }

    PM->>A: POST /api/quotes {project_id, client_id, line_items from BOQ, ...}
    A->>QS: quote_service.create_quote(db, pm_id, data)
    QS->>RID: generate_reference_id(db, "QUO")
    RID-->>QS: "SWA-2025-QUO-001"
    QS->>DB: INSERT quotes (status="Draft")
    DB-->>QS: row
    QS-->>A: QuoteRead
    A-->>PM: 201 Created

    PM->>A: POST /quotes/{id}/submit
    A->>QS: quote_service.submit_quote(db, quote_id)
    QS->>DB: UPDATE quotes SET status="Submitted"
    QS-->>A: QuoteRead
    A-->>PM: 200

    Note over PM,DB: ... client reviews, approves ...

    PM->>A: POST /quotes/{id}/approve
    A->>QS: quote_service.approve_quote(db, quote_id)
    QS->>DB: UPDATE quotes SET status="Approved"
    QS->>DB: CREATE project from approved quote
    QS-->>A: QuoteRead + ProjectRead
    A-->>PM: 200

    PM->>A: POST /api/invoices {project_id, amount, ...}
    A->>IS: invoice_service.create_invoice(db, pm_id, data)
    IS->>RID: generate_reference_id(db, "INV")
    RID-->>IS: "SWA-2025-INV-001"
    IS->>DB: INSERT invoices (amount, gst_amount, total_amount)
    DB-->>IS: row
    IS-->>A: InvoiceRead
    A-->>PM: 201 Created { amount: 100000, gst: 18000, total: 118000 }
```

---

## BUILT vs TARGET-STATE

- **BUILT:** BOQ models + Excel/JSON ingestion, full quote status lifecycle (Draft→Submitted→
  Approved→Responded), invoice with GST (wave-18), PDF export for quotes and financial reports,
  async export via Celery.
- **TARGET-STATE:** None — the BOQ→Quote→Invoice flow is complete.
