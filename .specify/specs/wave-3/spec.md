# Wave 3 — Quotation / BOQ Workflow

## Objective
Enable SWA to upload BOQ (Bill of Quantities) files, version them, generate quotations with markup, and manage an approval workflow before sending to clients. This is the core revenue-generating workflow of the ERP.

## Background
SWA receives BOQ files from clients (Excel, JSON exports from rfq2boq, or manual spreadsheets). Currently these are processed offline in spreadsheets. The ERP must ingest these, let PMs build quotes with markup and terms, get admin approval, and track client response.

## Functional Requirements

### BOQ Upload & Parse
- Upload Excel (.xlsx) or JSON BOQ files against a project
- Parse into structured line items: description, specification, unit, quantity, rate, amount, category
- Validate required columns: at minimum `description`, `quantity`, `unit`, `rate`
- Reject malformed uploads with clear error messages
- Store original file on disk (local filesystem; `uploads/boqs/<project_id>/<filename>`)

### BOQ Versioning
- Each upload creates a new BOQ version (auto-incremented per project: v1, v2, v3...)
- A project can have multiple BOQ versions; latest is default
- View any version's line items
- Soft-delete a version (not the file itself, just the DB record)

### Quote Generation
- Generate a quote from any BOQ version
- Quote has: subtotal (sum of BOQ items), markup %, markup amount, tax %, tax amount, total amount
- Terms & conditions (free text), validity period (days), valid_until date
- Quote items mirror BOQ items but with potentially overridden rates
- Quote is editable while in `draft` status

### Quote Approval Workflow
- Status machine: `draft` → `pending_approval` → `approved` → `sent` → `accepted` | `rejected`
- Only `admin` can approve a pending quote
- Only `pm` or `admin` can send an approved quote
- Client response (accept/reject) recorded with timestamp and notes
- Rejected quotes can be cloned into a new draft for revision
- Audit log entry on every status change

### Integration with Project Lifecycle
- When a quote is `sent`, the project's status should be `Quote` (enforced)
- When a quote is `accepted`, project can transition `Quote` → `Awarded`
- When a quote is `rejected`, project stays in `Quote` until a new quote is sent

## Non-functional Requirements
- Excel parsing must handle 1000+ line items in <5 seconds
- File size limit: 10MB
- Idempotent uploads: same file hash → warn but allow new version
- All monetary fields: `Decimal(18,2)`

## Data Model

### BOQ
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| project_id | UUID | FK → projects |
| version_number | int | auto-increment per project |
| file_name | str | original filename |
| file_path | str | relative path on disk |
| parsed_by | UUID | FK → users |
| parsed_at | datetime | |
| status | str | active, deleted |
| notes | str | optional |
| created_at | datetime | |
| deleted_at | datetime | soft delete |

### BOQItem
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| boq_id | UUID | FK → boqs |
| line_number | int | 1, 2, 3... |
| category | str | e.g. "Hot Insulation", "Cold Insulation", "Cladding" |
| description | str | item description |
| specification | str | material spec |
| unit | str | m², m³, kg, etc. |
| quantity | Decimal | |
| rate | Decimal | per unit |
| amount | Decimal | quantity × rate |

### Quote
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| project_id | UUID | FK → projects |
| boq_id | UUID | FK → boqs |
| version_number | int | snapshot of BOQ version |
| status | str | draft, pending_approval, approved, sent, accepted, rejected |
| subtotal | Decimal | sum of quote items |
| markup_percent | Decimal | e.g. 15.00 = 15% |
| markup_amount | Decimal | |
| tax_percent | Decimal | e.g. 18.00 = 18% GST |
| tax_amount | Decimal | |
| total_amount | Decimal | subtotal + markup + tax |
| terms | str | T&Cs |
| validity_days | int | default 30 |
| valid_until | date | |
| created_by | UUID | FK → users |
| approved_by | UUID | FK → users, nullable |
| approved_at | datetime | nullable |
| sent_at | datetime | nullable |
| client_response | str | accepted, rejected, nullable |
| client_response_at | datetime | nullable |
| client_response_notes | str | nullable |
| created_at | datetime | |
| updated_at | datetime | |
| deleted_at | datetime | soft delete |

### QuoteItem
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| quote_id | UUID | FK → quotes |
| boq_item_id | UUID | FK → boq_items, nullable |
| line_number | int | |
| category | str | |
| description | str | |
| specification | str | |
| unit | str | |
| quantity | Decimal | |
| rate | Decimal | may differ from BOQ rate |
| amount | Decimal | quantity × rate |

## API Endpoints

### BOQs
- `POST /api/projects/{id}/boqs` — upload + parse BOQ file
- `GET /api/projects/{id}/boqs` — list versions
- `GET /api/boqs/{boq_id}` — get version detail
- `GET /api/boqs/{boq_id}/items` — get line items (paginated)
- `DELETE /api/boqs/{boq_id}` — soft delete version

### Quotes
- `POST /api/projects/{id}/quotes` — create quote from BOQ version
- `GET /api/projects/{id}/quotes` — list quotes
- `GET /api/quotes/{quote_id}` — get quote detail
- `PATCH /api/quotes/{quote_id}` — edit draft (markup, terms, items)
- `POST /api/quotes/{quote_id}/submit` — submit for approval (draft → pending)
- `POST /api/quotes/{quote_id}/approve` — approve (pending → approved)
- `POST /api/quotes/{quote_id}/send` — send to client (approved → sent)
- `POST /api/quotes/{quote_id}/respond` — record client response (sent → accepted/rejected)
- `POST /api/quotes/{quote_id}/clone` — clone rejected quote to new draft
- `DELETE /api/quotes/{quote_id}` — soft delete

## Frontend Pages
- Project detail → "BOQs" tab: upload, version list, view items
- Project detail → "Quotes" tab: list quotes, create quote, edit draft, view details
- Quote builder page: side-by-side BOQ items + quote items with editable rates
- Quote detail page: full quote with totals, status badge, approval buttons, client response form

## RBAC
| Action | Admin | PM | Designer | Auditor | Viewer |
|--------|-------|----|----------|---------|--------|
| Upload BOQ | ✅ | ✅ | ❌ | ❌ | ❌ |
| View BOQ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Delete BOQ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Create Quote | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit Draft Quote | ✅ | ✅ | ❌ | ❌ | ❌ |
| Submit for Approval | ✅ | ✅ | ❌ | ❌ | ❌ |
| Approve Quote | ✅ | ❌ | ❌ | ❌ | ❌ |
| Send Quote | ✅ | ✅ | ❌ | ❌ | ❌ |
| Record Client Response | ✅ | ✅ | ❌ | ❌ | ❌ |
| View Quote | ✅ | ✅ | ✅ | ✅ | ✅ |
| Delete Quote | ✅ | ✅ | ❌ | ❌ | ❌ |

## Acceptance Criteria
- [ ] Can upload a 100-line Excel BOQ and see all items parsed correctly
- [ ] Can upload a second BOQ for same project; version auto-increments
- [ ] Can generate quote from any BOQ version
- [ ] Quote totals recalculate correctly when markup/tax/rates change
- [ ] Full approval workflow: draft → submit → approve → send → accept
- [ ] Rejected quote can be cloned to new draft
- [ ] Audit log records every quote status change
- [ ] Only admin can approve; PM can submit/send
- [ ] `pytest tests/wave-3/` passes 100%
- [ ] Frontend lint and build pass
