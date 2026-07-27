# Task 04 — Quote API & PDF Generation — Report

## Status: COMPLETE

## Files Created/Modified

### New Files
| File | Purpose |
|------|---------|
| `src/backend/models/quote.py` | Quote + QuoteItem SQLAlchemy models |
| `src/backend/core/quote_workflow.py` | Status machine: draft → pending → approved → sent → accepted/rejected |
| `src/backend/schemas/quote.py` | Pydantic v2 schemas: QuoteCreate, QuoteUpdate, QuoteRead, QuoteListResponse, QuoteRespondRequest |
| `src/backend/db/repositories/quote_repo.py` | CRUD + clone + status update + soft delete |
| `src/backend/services/quote_service.py` | Business logic: generate, transition, update, clone, audit logging |
| `src/backend/services/pdf_service.py` | PDF generation using fpdf2 |
| `src/backend/api/quotes.py` | 11 API endpoints with RBAC enforcement |

### Modified Files
| File | Change |
|------|--------|
| `src/backend/main.py` | Registered quotes router |
| `src/backend/models/__init__.py` | Added Quote, QuoteItem exports (already done by Task 03) |
| `src/backend/requirements.txt` | Added `fpdf2==2.8.1` |
| `src/backend/alembic/versions/0005_add_quotes.py` | Added missing `code` column |

## API Endpoints (11 total)

| Method | Path | RBAC | Description |
|--------|------|------|-------------|
| POST | `/api/projects/{project_id}/quotes` | PM+ | Create quote from BOQ |
| GET | `/api/projects/{project_id}/quotes` | Any auth | List quotes (paginated) |
| GET | `/api/quotes/{quote_id}` | Any auth | Get quote detail |
| PATCH | `/api/quotes/{quote_id}` | PM+ | Update draft quote |
| DELETE | `/api/quotes/{quote_id}` | PM+ | Soft delete quote |
| POST | `/api/quotes/{quote_id}/submit` | PM+ | Draft → pending_approval |
| POST | `/api/quotes/{quote_id}/approve` | Admin only | pending → approved |
| POST | `/api/quotes/{quote_id}/send` | PM+ | approved → sent |
| POST | `/api/quotes/{quote_id}/respond` | PM+ | sent → accepted/rejected |
| POST | `/api/quotes/{quote_id}/clone` | PM+ | rejected → new draft |
| GET | `/api/quotes/{quote_id}/pdf` | Any auth | Download PDF |

## PDF Output
- Header: "SWA Consultancy Pvt. Ltd. — Quotation"
- Metadata: Quote #, Date, Valid Until, Project, Client, Status
- Line items table: #, Category, Description, Unit, Qty, Rate, Amount
- Totals: Subtotal, Markup (%), Tax (%), Grand Total
- Terms & Conditions section
- Signature block (SWA + Client)

## Ruff Result
All checks passed (0 errors across all Task 04 files).

## Acceptance
- [x] `python3 -m ruff check src/backend/models/quote.py src/backend/core/quote_workflow.py src/backend/schemas/quote.py src/backend/db/repositories/quote_repo.py src/backend/services/quote_service.py src/backend/services/pdf_service.py src/backend/api/quotes.py src/backend/main.py` — clean (0 errors)
- [x] `python3 -m pytest tests/wave-3/ -q` — all tests passed

## Integration Notes
- Task 03 was implemented in parallel; the service layer (`quote_service.py`, `quote_repo.py`) already existed when Task 04 ran
- Added `code` field to the enriched dict in the service for schema compatibility
- Migration 0005 was updated to include the `code` column
- Audit logging writes `quote.transition.{status}` for every transition
