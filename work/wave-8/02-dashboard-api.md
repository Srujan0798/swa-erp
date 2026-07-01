# Task 02 — Dashboard Aggregation Endpoints

## Goal
Create the FastAPI router exposing report data. Five endpoints serve project health, utilization, revenue, client summary, and an aggregated executive dashboard KPI endpoint.

## Files to Create/Modify

### 1. API Router
Create `src/backend/api/reports.py`:
```python
router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/project-health", response_model=ProjectHealthReport)
@router.get("/utilization", response_model=UtilizationReport)
@router.get("/revenue", response_model=RevenueForecast)
@router.get("/client-summary", response_model=ClientSummaryReport)
@router.get("/dashboard/executive", response_model=ExecutiveKPIs)
```

- **GET /api/reports/project-health** — no params. Returns `ProjectHealthReport`.
- **GET /api/reports/utilization** — query params `start_date: date | None`, `end_date: date | None`. Defaults: first of current month → today.
- **GET /api/reports/revenue** — no params. Returns `RevenueForecast`.
- **GET /api/reports/client-summary** — no params. Returns `ClientSummaryReport`.
- **GET /api/dashboard/executive** — no params. Returns `ExecutiveKPIs`.

All endpoints require authentication (use `get_current_user` dependency from `src/backend/core/deps.py`).

### 2. Register Router
Modify `src/backend/main.py` — add:
```python
from src.backend.api.reports import router as reports_router
app.include_router(reports_router)
```

### 3. Tests
Create `tests/wave-8/test_reports_api.py`:
- Test each endpoint returns 200 with valid JSON
- Test `/utilization` with custom date range
- Test all endpoints return 401 without auth token
- Test `/project-health` structure has `by_status` dict
- Test `/revenue` structure has `monthly_revenue` list
- Test `/dashboard/executive` has all KPI fields

## Files you must NOT touch
- `src/backend/services/report_service.py` — created in Task 01
- `src/backend/core/deps.py` — use existing `get_current_user` dependency
- `src/frontend/` — frontend is Task 03

## Acceptance criteria
- [ ] `pytest tests/wave-8/test_reports_api.py` passes
- [ ] All 5 endpoints return 200 with correct response shapes
- [ ] All endpoints return 401 without auth token
- [ ] `/utilization` accepts and respects `start_date` and `end_date` params
- [ ] `make lint` clean
- [ ] Response times < 2s for all endpoints (non-blocking; note if slow)

## Test File
Create `tests/wave-8/test_reports_api.py`:
- `test_project_health_200` — authenticated GET returns 200 + ProjectHealthReport shape
- `test_utilization_200` — authenticated GET returns 200 + UtilizationReport shape
- `test_utilization_date_range` — pass start/end, verify period in response
- `test_revenue_200` — authenticated GET returns 200 + RevenueForecast shape
- `test_client_summary_200` — authenticated GET returns 200 + ClientSummaryReport shape
- `test_executive_kpis_200` — authenticated GET returns 200 + ExecutiveKPIs shape
- `test_unauthorized_401` — all endpoints return 401 without token
- `test_invalid_date_range_422` — pass malformed date, expect 422

## Constraints
- Time budget: 30 min
- Follow existing router pattern from `src/backend/api/projects.py`
- Use `get_current_user` dependency — do not create new auth logic
- No new pip dependencies
- Allowed tools: Read, Write, Edit, Bash, Glob, Grep

## Notes
- Router prefix is `/api/reports` — exec dashboard is nested at `/api/dashboard/executive` (separate prefix)
- Consider registering executive dashboard under the same router with `prefix="/api/dashboard"` or keep it flat under `/api/reports/executive`
- Simpler: put exec endpoint as `/api/reports/executive` to keep one router
