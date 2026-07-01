# Task 04 — Export Deliverables (PDF Generation)

## Goal
Create backend export endpoints that generate PDF deliverables: project summary paper, financial report, project status slides, and client demo data package. Use `fpdf2` for PDF generation.

## Files to Create/Modify

### 1. PDF Service
Create `src/backend/services/export_service.py`:
```python
class ExportService:
    def export_project_summary(self, db: Session, project_id: uuid.UUID) -> bytes
    def export_financial_report(self, db: Session, start_date: date, end_date: date) -> bytes
    def export_project_slides(self, db: Session, project_id: uuid.UUID) -> bytes
    def export_demo_package(self, db: Session, project_id: uuid.UUID) -> dict
```

- `export_project_summary` — generates a PDF with:
  - Project name, client, status, dates, budget
  - BOQ summary (total value, item count)
  - Task status breakdown
  - Team members list
  - Return PDF as bytes

- `export_financial_report` — generates a PDF with:
  - Date range header
  - Revenue by month table
  - Invoice status summary (paid, pending, overdue)
  - Expense breakdown
  - Net P&L

- `export_project_slides` — generates a simple "slide deck" PDF:
  - Title slide (project name, date)
  - Status overview slide
  - Budget vs actual slide
  - Timeline/milestones slide
  - Next steps slide
  - Use landscape A4, large fonts

- `export_demo_package` — returns dict (JSON) with:
  - Project details
  - Sample BOQ items
  - Task list with statuses
  - Team info
  - For client demo, not a PDF — returns structured JSON

### 2. API Router
Create `src/backend/api/exports.py`:
```python
router = APIRouter(prefix="/api/exports", tags=["exports"])

@router.get("/projects/{project_id}/summary.pdf")
@router.get("/reports/financial.pdf")
@router.get("/projects/{project_id}/slides.pdf")
@router.get("/projects/{project_id}/demo.json")
```
- All endpoints return `Response` with appropriate `Content-Type` and `Content-Disposition` header for download
- Financial endpoint accepts `start_date` and `end_date` query params
- All require authentication

### 3. Register Router
Modify `src/backend/main.py`:
```python
from src.backend.api.exports import router as exports_router
app.include_router(exports_router)
```

### 4. Install dependency
Add `fpdf2` to `requirements.txt` (or `pyproject.toml`):
```
fpdf2>=2.7.0
```
Run `pip install fpdf2`.

### 5. Tests
Create `tests/wave-8/test_exports.py`:
- `test_project_summary_pdf` — verify returns PDF bytes, starts with `%PDF`
- `test_financial_report_pdf` — verify PDF bytes returned
- `test_project_slides_pdf` — verify PDF bytes returned
- `test_demo_package_json` — verify dict structure with expected keys
- `test_unauthorized_401` — all endpoints require auth
- `test_nonexistent_project_404` — summary for non-existent project returns 404

## Files you must NOT touch
- `src/frontend/` — frontend export buttons are in Task 03
- `src/backend/services/report_service.py` — may read from but do not modify
- `src/backend/models/` — no new models

## Acceptance criteria
- [ ] `pytest tests/wave-8/test_exports.py` passes
- [ ] `/projects/{id}/summary.pdf` returns valid PDF with project info
- [ ] `/reports/financial.pdf` returns valid PDF with financial data
- [ ] `/projects/{id}/slides.pdf` returns landscape PDF with multiple pages
- [ ] `/projects/{id}/demo.json` returns structured JSON
- [ ] All endpoints require auth (401 without token)
- [ ] `make lint` clean

## Constraints
- Time budget: 40 min
- `fpdf2` is the only new dependency — do not add others
- PDF layout: clean, readable, SWA branding (company name in header/footer)
- Use `fpdf2`'s built-in fonts (Helvetica) — no custom font files
- Handle missing data gracefully (show "N/A" or "—" in PDF cells)
- Allowed tools: Read, Write, Edit, Bash, Glob, Grep

## Notes
- PDF generation is CPU-bound; for production, offload to Celery workers. For now, synchronous is fine.
- SWA Consultancy branding: add "SWA Consultancy" as header on each page, page numbers in footer
- For `export_demo_package`, this is intentionally JSON (not PDF) — it's meant to be imported into another system
- Content-Disposition header format: `attachment; filename="project-summary-{project_id}.pdf"`
