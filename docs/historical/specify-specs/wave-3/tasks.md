# Wave 3 — Tasks

## Overview
Wave 3 implements the **Quotation / BOQ workflow**: upload BOQ files, version them, generate quotations with markup, manage approval workflow, and integrate with project lifecycle.

## Tasks

### 01 — BOQ Models & Upload API
**Owner:** Backend
**File(s):** `src/backend/api/boqs.py`
**Dependencies:** None
**Status:** ✅ Ready

**Description:**
Implement the core BOQ upload and parse API:
- Upload .xlsx or JSON BOQ files against a project
- Parse into structured line items (description, spec, unit, quantity, rate, amount, category)
- Validate required columns: `description`, `quantity`, `unit`, `rate`
- Reject malformed uploads with clear error messages
- Store original file locally at `uploads/boqs/<project_id>/<filename>`
- Create BOQ version `v1` (auto-incremented per project) by default
- Return BOQ ID for subsequent version actions

**Acceptance criteria:**
- `[ ]` POST `/api/boqs/` with `multipart/form-data` containing `project_id` and BOQ file
- `[ ]` Returns JSON `{id: <BOQ_uuid>, version: 1}` on success
- `[ ]` Returns `422` with validation error on malformed Excel/JSON
- `[ ]` File saved to `uploads/boqs/<project_id>/` with timestamped name
- `[ ]` Tests: `tests/wave-3/test_boq_upload.py` passes 100%

**Worker skills needed:** `tdd`, `python`, `fastapi`, `sqlalchemy`, `openpyxl`, `pytest`

---

### 02 — BOQ Versioning & Item API
**Owner:** Backend
**File(s):** `src/backend/api/boqs.py`
**Dependencies:** 01
**Status:** ✅ Ready

**Description:**
Implement BOQ versioning and item retrieval endpoints:
- List all BOQ versions for a project: `GET /api/projects/{project_id}/boqs`
- Get specific BOQ version: `GET /api/boqs/{boq_id}`
- List items within a version: `GET /api/boqs/{boq_id}/items`
- Soft-delete a BOQ version (DB record, keep file)
- Each version auto-incremented (v1, v2, v3...)
- New uploads default to latest version

**Acceptance criteria:**
- `[ ]` GET `/api/boqs/` list BOQs with pagination
- `[ ]` GET `/api/boqs/{id}` returns version number and item count
- `[ ]` GET `/api/boqs/{id}/items` returns all parsed line items
- `[ ]` DELETE `/api/boqs/{id}` soft-deletes version (status 'deleted')
- `[ ]` Tests: `tests/wave-3/test_boq_versions.py` passes 100%

**Worker skills needed:** `sqlalchemy`, `pytest`, `api-design`, `soft-delete`

---

### 03 — Quote Generation & Approval Workflow
**Owner:** Backend
**File(s):** `src/backend/models/quote.py`, `src/backend/api/quotes.py`
**Dependencies:** 01, 02
**Status:** ✅ Ready

**Description:**
Implement quote models and approval workflow:
- Quote model: subtotal, markup%, markup amount, tax%, tax amount, total, terms, validity, status
- QuoteItem model: description, unit, quantity, rate, amount (override BOQ rates in draft)
- Status machine: `draft` → `pending_approval` → `approved` → `sent` → `accepted` | `rejected`
- Admin approval: POST `/api/quotes/{id}/approve`
- PM send quote: POST `/api/quotes/{id}/send`
- Client response: POST `/api/quotes/{id}/respond` (accept/reject)
- Rejected quotes: clone into new draft for revision
- Audit log on every status change

**Acceptance criteria:**
- `[ ]` Quote CRUD endpoints with status validation
- `[ ]` Approve endpoint only for admin, transitions to `pending_approval`
- `[ ]` Send endpoint only for PM/admin, transitions to `sent`, project status to `Quote`
- `[ ]` Respond endpoint records client decision, transitions to `accepted` or `rejected`
- `[ ]` Clone endpoint creates new draft from rejected quote
- `[ ]` Tests: `tests/wave-3/test_quote_workflow.py` passes 100%

**Worker skills needed:** `tdd`, `python`, `fastapi`, `state-machine`, `workflow`, `audit`, `business-logic`

---

### 04 — Quote API & PDF Generation
**Owner:** Backend
**File(s):** `src/backend/api/quotes.py`, `src/backend/services/pdf_service.py`
**Dependencies:** 03
**Status:** ✅ Ready

**Description:**
Implement transition endpoints and quote PDF generation:
- Quote transitions:
  - Submit: `POST /api/quotes/{id}/submit` (draft → pending_approval)
  - Approve: `POST /api/quotes/{id}/approve` (pending_approval → approved)
  - Send: `POST /api/quotes/{id}/send` (approved → sent)
  - Respond: `POST /api/quotes/{id}/respond` with {status: 'accepted'|'rejected'}
  - Clone: `POST /api/quotes/{id}/clone` create new draft from rejected
- PDF generation: `GET /api/quotes/{id}/pdf` returns PDF with quote details
- JSON export: `GET /api/quotes/{id}/export` returns structured quote data
- Print styling: professional quote layout with totals calculation

**Acceptance criteria:**
- `[ ]` All transition endpoints validated (role-specific, status-specific)
- `[ ]` PDF generation creates valid PDF with quote information
- `[ ]` JSON export includes all fields with computed totals
- `[ ]` Email preparation (stub): `POST /api/quotes/{id}/prepare-email`
- `[ ]` Tests: wave-3 quote API tests pass 100%

**Worker skills needed:** `tdd`, `fastapi`, `pdf-generation`, `api-validation`, `business-rules`

---

### 05 — Frontend BOQ & Quotes UI
**Owner:** Frontend
**File(s):** `src/frontend/src/components/boq/`, `src/frontend/src/components/quotes/`, React hooks
**Dependencies:** 01, 02, 03, 04
**Status:** ✅ Ready

**Description:**
Build React UI for BOQ upload, management, and quotes:
- BOQ upload form with drag-and-drop Excel/JSON support
- BOQ version selector with item view (table/list)
- Quote generation form with markup/tax fields, rate overrides
- Quote workflow buttons: submit, approve (admin), send, respond, clone
- Quote display with PDF download and JSON export
- Project breadcrumb navigation linking to client/project
- Real-time status updates via TanStack Query

**Acceptance criteria:**
- `[ ]` Upload component with file validation and progress feedback
- `[ ]` Version viewer showing items in sortable/filterable table
- `[ ]` Quote creation form with automatic totals calculation
- `[ ]` Workflow buttons respecting user roles and quote status
- `[ ]` Quote detail page with PDF download and JSON export
- `[ ]` Tests: wave-3 frontend tests pass with RTL

**Worker skills needed:** `react`, `typescript`, `tailwind`, `shadcn-ui`, `tanstack-query`, `testing-library`, `rtl`

---

## Integration notes
- **Concurrency:** Sequential (one BOQ writer) → one BOQ at a time per project
- **Validation:** Server-side validation (Pydantic) > client-side (React Zod)
- **Security:** Token validation + RBAC (admin/PM for write ops)
- **Data model:** Decimal(18,2) for money, INR default currency
- **Compliance:** Explicit NBC/ECBC/IGBC/IS references in quotes/terms