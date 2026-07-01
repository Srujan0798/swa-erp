# Wave 7 Task 03 — Invoicing: Report

## Files Created
| File | Status |
|------|--------|
| `src/backend/models/invoice.py` | ✅ Created — Invoice + InvoiceItem models |
| `src/backend/schemas/invoice.py` | ✅ Created — Pydantic v2 schemas |
| `src/backend/db/repositories/invoice_repo.py` | ✅ Created — CRUD + invoice number generation |
| `src/backend/services/invoice_service.py` | ✅ Created — Business logic layer |
| `src/backend/api/invoices.py` | ✅ Created — 6 REST endpoints |
| `src/backend/alembic/versions/0013_add_invoices.py` | ✅ Created — Migration for invoices + invoice_items tables |

## Files Modified
| File | Change |
|------|--------|
| `src/backend/models/__init__.py` | Added `Invoice`, `InvoiceItem` imports and `__all__` entries |
| `src/backend/main.py` | Added `invoices_router` import and `app.include_router(invoices_router)` |

## Ruff Result
```
ruff check src/backend/models/invoice.py src/backend/schemas/invoice.py \
  src/backend/db/repositories/invoice_repo.py src/backend/services/invoice_service.py \
  src/backend/api/invoices.py
→ All checks passed!
```

Pre-existing ruff issues in other files (48 total) are not from this task.

## API Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/projects/{project_id}/invoices` | PM+ | Create invoice with items |
| POST | `/api/projects/{project_id}/invoices/generate-from-time` | PM+ | Generate from billable time entries |
| GET | `/api/projects/{project_id}/invoices` | Any | List invoices (filterable by status) |
| GET | `/api/invoices/{invoice_id}` | Any | Get invoice with items |
| PATCH | `/api/invoices/{invoice_id}/status` | Any | Update status (draft→sent→paid) |
| DELETE | `/api/invoices/{invoice_id}` | PM+ | Soft delete (draft only) |

## Key Design Decisions
- **Invoice number format**: `INV-{YYYYMM}-{sequence:04d}` — monthly sequence from DB
- **Tax calculation**: `subtotal = Σ(qty × rate)`, `tax = subtotal × tax_rate / 100`, `total = subtotal + tax`
- **Status machine**: `draft → sent → paid` (forward-only, no backward)
- **Delete guard**: Only draft invoices can be deleted (400 otherwise)
- **Time entry rate**: Default 5000 INR/hour, grouped per entry as individual line items
- **Soft delete**: Uses `deleted_at` timestamp, consistent with project/quote patterns

## Issues
- None in new code
- Pre-existing ruff issues in `main.py` (undefined routers), `task_repo.py`, `material_service.py`, etc. are unrelated
