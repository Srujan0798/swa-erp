# Task 04 — Quote API & PDF Generation

## Goal
Build the REST API for quotes (transitions, CRUD) and basic PDF generation for quotes. Integrate with audit log.

## Files to Create/Modify

### 1. API
Create `src/backend/api/quotes.py`:

```python
router = APIRouter(prefix="/api", tags=["quotes"])

# Project-scoped
@router.post("/projects/{project_id}/quotes", response_model=QuoteRead, status_code=201)
def create_quote(...)

@router.get("/projects/{project_id}/quotes", response_model=QuoteListResponse)
def list_quotes(...)

# Quote-scoped
@router.get("/quotes/{quote_id}", response_model=QuoteRead)
def get_quote(...)

@router.patch("/quotes/{quote_id}", response_model=QuoteRead)
def update_quote(...)

@router.delete("/quotes/{quote_id}", status_code=204)
def delete_quote(...)

# Transitions
@router.post("/quotes/{quote_id}/submit", response_model=QuoteRead)
def submit_quote(...)

@router.post("/quotes/{quote_id}/approve", response_model=QuoteRead)
def approve_quote(...)

@router.post("/quotes/{quote_id}/send", response_model=QuoteRead)
def send_quote(...)

@router.post("/quotes/{quote_id}/respond", response_model=QuoteRead)
def respond_quote(...)

@router.post("/quotes/{quote_id}/clone", response_model=QuoteRead, status_code=201)
def clone_quote(...)

# PDF
@router.get("/quotes/{quote_id}/pdf")
def download_quote_pdf(...)
```

Register in `src/backend/main.py`.

**RBAC enforcement:**
- create_quote: admin/pm
- list_quotes: any authenticated
- get_quote: any authenticated
- update_quote: admin/pm (only if draft)
- delete_quote: admin/pm
- submit: admin/pm (only if draft)
- approve: admin only (only if pending)
- send: admin/pm (only if approved)
- respond: admin/pm (only if sent)
- clone: admin/pm (only if rejected)
- download_pdf: any authenticated

### 2. PDF Service
Create `src/backend/services/pdf_service.py`:
- `generate_quote_pdf(quote: QuoteRead) -> bytes`
  - Build a simple HTML template with quote details, line items table, totals breakdown
  - Use `weasyprint` or `xhtml2pdf` to convert HTML to PDF bytes
  - If neither library is available, fall back to a simple text-based PDF using `fpdf2`
  
**Recommendation:** Use `fpdf2` — it's lightweight, pure Python, no external dependencies.
Install: `pip install fpdf2`

Sample PDF structure:
- Header: "SWA Consultancy Pvt. Ltd. — Quotation"
- Quote #: {quote.code or id}
- Date: {created_at}
- Valid Until: {valid_until}
- Client: {project.client_name}
- Project: {project.name}
- Table: Line # | Category | Description | Spec | Unit | Qty | Rate | Amount
- Totals: Subtotal, Markup ({markup_percent}%), Tax ({tax_percent}%), Total
- Terms & Conditions
- Signature block

### 3. Quote Code
Add a `code` field to Quote model (or generate on the fly). Suggestion: `Q-{project_code}-V{version}-{n}` where n is quote sequence for that project.

Actually, simpler: `quote_number` auto-generated as `Q-2025-001` format. Use a sequence table or just `SELECT COUNT(*) + 1` per year.

For now, keep it simple: `code` is nullable. Frontend can display quote ID if no code.

### 4. Integration with Lifecycle
When quote is `sent`, ensure project status is `Quote`. If not, return 400 with message.

When quote is `accepted`, allow project transition `Quote` → `Awarded`.

This should be handled in `quote_service.py` by calling the lifecycle service or simply checking project status.

### 5. Audit Log
Every quote transition writes to audit_log:
- action: `quote.{transition}` (e.g. `quote.submit`, `quote.approve`)
- entity_type: `quote`
- entity_id: quote.id
- before_json: {status: old_status}
- after_json: {status: new_status, approved_by, etc.}

## Acceptance Criteria
- [ ] All quote CRUD endpoints work with proper RBAC
- [ ] Status transitions enforce rules (e.g., only admin approves)
- [ ] PDF download returns a valid PDF with quote details
- [ ] Audit log records every transition
- [ ] `pytest tests/wave-3/test_quote_api.py` passes
- [ ] `pytest tests/wave-3/test_quote_pdf.py` passes

## Test File
Create `tests/wave-3/test_quote_api.py` with at least:
- `test_create_quote` — 201
- `test_list_quotes` — paginated
- `test_get_quote` — 200
- `test_update_draft_quote` — 200
- `test_update_approved_quote_fails` — 400
- `test_delete_quote` — 204
- `test_submit_quote` — 200
- `test_approve_quote` — 200
- `test_send_quote` — 200
- `test_respond_quote_accepted` — 200
- `test_respond_quote_rejected` — 200
- `test_clone_quote` — 201
- `test_pm_cannot_approve` — 403
- `test_viewer_cannot_create_quote` — 403

Create `tests/wave-3/test_quote_pdf.py` with:
- `test_download_quote_pdf` — returns PDF bytes with correct content-type

## Notes
- PDF generation should be synchronous for now (small quotes). Async/Celery for large quotes in future.
- Content-Type for PDF response: `application/pdf`
- Filename header: `Content-Disposition: attachment; filename="quote-{id}.pdf"`