# Task 01 — BOQ Models & Upload API — Report

## Status: COMPLETE

## Files Created/Modified

### New Files
| File | Description |
|------|-------------|
| `src/backend/models/boq.py` | BOQ and BOQItem SQLAlchemy models |
| `src/backend/core/boq_parser.py` | Excel (.xlsx) and JSON file parsers with validation |
| `src/backend/schemas/boq.py` | Pydantic v2 schemas (BOQItemCreate/Read, BOQCreate/Read/ListResponse) |
| `src/backend/db/repositories/boq_repo.py` | Repository functions (create, get, list, soft_delete, get_next_version_number) |
| `src/backend/services/boq_service.py` | Business logic (upload_boq, get_boq, list_boqs, delete_boq) |
| `src/backend/api/boqs.py` | FastAPI router with 5 endpoints |
| `src/backend/alembic/versions/0004_add_boqs.py` | Alembic migration for boqs + boq_items tables |

### Modified Files
| File | Change |
|------|--------|
| `src/backend/models/__init__.py` | Added BOQ, BOQItem exports |
| `src/backend/schemas/__init__.py` | Added BOQCreate, BOQItemCreate, BOQItemRead, BOQListResponse, BOQRead exports |
| `src/backend/api/__init__.py` | Added boqs_router export |
| `src/backend/main.py` | Added boqs_router to app |

## API Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/projects/{project_id}/boqs` | Admin | Upload BOQ file (multipart) |
| `GET` | `/api/projects/{project_id}/boqs` | Any authenticated | List BOQ versions |
| `GET` | `/api/boqs/{boq_id}` | Any authenticated | Get BOQ detail with items |
| `GET` | `/api/boqs/{boq_id}/items` | Any authenticated | Get BOQ items |
| `DELETE` | `/api/boqs/{boq_id}` | Admin | Soft delete BOQ |

## Ruff Result
```
All checks passed!
```

## Notes
- Pre-existing ruff errors in `quote.py` (F821 undefined `Date`) and `quote_service.py` (I001, F401) exist but are unrelated to this task
- `openpyxl` was already in `requirements.txt`
- Migration uses `down_revision = "0003"` matching existing chain
- Parser handles: missing columns (422), empty rows (skipped), Decimal precision via `Decimal(str(value))`
- File storage: `uploads/boqs/{project_id}/{uuid}_{filename}`
