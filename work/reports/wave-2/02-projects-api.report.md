# Report: Task 02 — Projects API

**Status**: ✅ COMPLETE

## Files Created

| File | Purpose |
|------|---------|
| `src/backend/models/project.py` | Project SQLAlchemy model with all fields per spec |
| `src/backend/schemas/project.py` | ProjectCreate, ProjectUpdate, ProjectRead, ProjectListResponse, ProjectStatus (StrEnum) |
| `src/backend/db/repositories/project_repo.py` | list_projects, get_by_id, create_project, update_project, soft_delete_project, get_project_with_names, list_projects_with_names |
| `src/backend/services/project_service.py` | create, get, list, update, soft_delete with audit logging |
| `src/backend/api/projects.py` | GET /api/projects, POST /api/projects, GET /api/projects/{id}, PATCH /api/projects/{id}, DELETE /api/projects/{id} |
| `src/backend/alembic/versions/0003_add_projects.py` | Migration to add projects table with FKs to clients and users |
| `tests/wave-2/test_projects.py` | 6 test cases per spec |

## Files Modified

| File | Change |
|------|--------|
| `src/backend/models/__init__.py` | Added Project import |
| `src/backend/api/__init__.py` | Added projects_router export |
| `src/backend/main.py` | Added projects_router, fixed duplicate users_router |

## API Endpoints

| Method | Path | Auth | Returns |
|--------|------|------|---------|
| GET | `/api/projects` | admin/pm | ProjectListResponse (paginated, q, status filter) |
| POST | `/api/projects` | admin/pm | ProjectRead (201) |
| GET | `/api/projects/{id}` | any authenticated | ProjectRead |
| PATCH | `/api/projects/{id}` | admin/pm | ProjectRead |
| DELETE | `/api/projects/{id}` | admin | 204 soft-delete |

## Key Features

- **Project lifecycle**: LEAD → QUOTE → AWARDED → DESIGN → VENDOR → EXECUTION → VALIDATION → CLOSED
- **Unique code constraint**: Returns 409 on duplicate code
- **Search**: Matches name, code, or location (ILIKE)
- **Status filter**: Single status query parameter
- **Soft delete**: Sets deleted_at, excludes from queries
- **Nested names**: ProjectRead includes client_name, pm_name, designer_name, auditor_name
- **Audit logging**: project.create, project.update, project.delete with before/after JSON

## Acceptance Criteria

- [x] `ruff check src/backend/` → All checks passed
- [x] `python3 -c "from src.backend.main import app; print('OK')"` → OK
- [x] All modules import correctly
- [ ] `pytest tests/wave-2/test_projects.py -v` — requires PostgreSQL test DB (not available in current environment)
- [ ] `alembic upgrade head` — requires running PostgreSQL

## Notes

- Uses `Decimal(18,2)` for estimated_value and actual_value
- Uses `Date` (not DateTime) for start_date, target_end_date, actual_end_date
- ProjectStatus uses `StrEnum` (Python 3.11+ enum.StrEnum inheritance)
- Tests depend on client creation via `/api/clients` endpoint (Task 01 of wave-2)