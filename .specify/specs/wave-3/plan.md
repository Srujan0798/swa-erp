# Wave 3 Implementation Plan

## Architecture Decisions
1. **File storage:** Local filesystem `uploads/boqs/<project_id>/` for MVP. MinIO/S3 in future wave.
2. **Excel parser:** `openpyxl` for .xlsx parsing (pure Python, no external deps). JSON parser is trivial.
3. **Quote totals:** Computed server-side on every save, not stored as DB computed columns.
4. **Quote item rates:** Can override BOQ rates in draft. Once submitted, items are frozen.
5. **BOQ version immutability:** Once parsed, BOQ items cannot be edited. Create new version instead.
6. **Project status integration:** Quote service calls lifecycle service for status validation.

## Task Breakdown

### Task 01 — BOQ Models & Upload API
**Owner:** Backend
**Files:**
- `src/backend/models/boq.py` — BOQ, BOQItem models
- `src/backend/schemas/boq.py` — BOQCreate, BOQRead, BOQItemRead, BOQListResponse
- `src/backend/db/repositories/boq_repo.py` — CRUD + version increment
- `src/backend/services/boq_service.py` — upload + parse orchestration
- `src/backend/api/boqs.py` — endpoints
- `src/backend/core/boq_parser.py` — Excel/JSON parser
**Dependencies:** Wave-2 project API
**Tests:** `tests/wave-3/test_boq_upload.py`

### Task 02 — BOQ Versioning & Item API
**Owner:** Backend
**Files:**
- Extend `boq_repo.py` — list versions, get items, soft delete
- `src/backend/api/boqs.py` — add list, detail, items, delete endpoints
- `src/backend/services/boq_service.py` — add list, detail, delete
**Dependencies:** Task 01
**Tests:** `tests/wave-3/test_boq_versions.py`

### Task 03 — Quote Generation & Approval Workflow
**Owner:** Backend
**Files:**
- `src/backend/models/quote.py` — Quote, QuoteItem models
- `src/backend/schemas/quote.py` — QuoteCreate, QuoteUpdate, QuoteRead, QuoteListResponse
- `src/backend/db/repositories/quote_repo.py` — CRUD
- `src/backend/services/quote_service.py` — generation, totals calculation, transitions
- `src/backend/core/quote_workflow.py` — status machine
- `src/backend/api/quotes.py` — endpoints
**Dependencies:** Task 01, Task 02
**Tests:** `tests/wave-3/test_quote_workflow.py`

### Task 04 — Quote API & PDF Generation
**Owner:** Backend
**Files:**
- Extend `quotes.py` — all transition endpoints (submit, approve, send, respond, clone)
- `src/backend/services/pdf_service.py` — quote PDF generation (using basic HTML→PDF or simple text)
- Integration with audit log on every transition
**Dependencies:** Task 03
**Tests:** `tests/wave-3/test_quote_api.py`, `tests/wave-3/test_quote_pdf.py`

### Task 05 — Frontend: BOQ & Quotes UI
**Owner:** Frontend
**Files:**
- `src/frontend/src/components/boqs/` — BOQUpload, BOQVersionList, BOQItemTable
- `src/frontend/src/components/quotes/` — QuoteList, QuoteBuilder, QuoteDetail, QuoteActions
- `src/frontend/src/pages/` — (add BOQ/Quote tabs to existing ProjectDetailPage)
- `src/frontend/src/hooks/useBoqs.ts`, `useQuotes.ts`
- `src/frontend/src/lib/api.ts` — add BOQ/Quote API methods
**Dependencies:** Task 01–04 backend running
**Tests:** Playwright E2E tests for BOQ upload + quote creation

## Migration
- `0004_add_boqs.py` — BOQ, BOQItem tables
- `0005_add_quotes.py` — Quote, QuoteItem tables

## Risk Mitigation
- Excel format variation: Parser must be tolerant of missing columns, extra rows, merged cells. Log warnings for unparseable rows but don't fail the whole upload.
- Large files: Stream-read Excel, don't load entire workbook into memory.
- Decimal precision: Use `Decimal` everywhere, never float.
