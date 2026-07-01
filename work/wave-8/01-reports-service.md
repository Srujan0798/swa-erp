# Task 01 — Backend Reports Service

## Goal
Build a ReportService that aggregates data across projects, time entries, tasks, and invoices to produce project health, team utilization, revenue forecast, and client summary reports. Export results as JSON (CSV export deferred).

## Files to Create/Modify

### 1. Schemas
Create `src/backend/schemas/report.py`:
- `ProjectHealthReport` — `total_projects: int`, `by_status: dict[str, int]`, `overdue_tasks: int`, `budget_variance_total: Decimal`, `at_risk_projects: list[dict]`
- `UtilizationReport` — `period_start: date`, `period_end: date`, `members: list[MemberUtilization]` where each has `user_id`, `name`, `billable_hours: Decimal`, `non_billable_hours: Decimal`, `utilization_pct: float`
- `RevenueForecast` — `monthly_revenue: list[MonthlyRevenue]`, `forecast: list[ForecastEntry]` with `project_id`, `project_name`, `pipeline_value: Decimal`, `probability: float`, `expected_value: Decimal`
- `ClientSummaryReport` — `clients: list[ClientSummary]` with `client_id`, `client_name`, `project_count: int`, `total_revenue: Decimal`
- `ExecutiveKPIs` — `active_projects: int`, `total_revenue_mtd: Decimal`, `avg_utilization: float`, `overdue_tasks: int`, `pipeline_value: Decimal`

### 2. Repository queries
Create `src/backend/db/repositories/report_repo.py`:
- `project_health_query(db)` — aggregate `Project` by `status` (enum count), join `Task` to count overdue (`due_date < now() AND status != 'done'`), sum `Project.budget` minus actual cost for variance
- `utilization_query(db, start_date, end_date)` — join `TimeEntry` with user, group by `user_id`, sum hours where `is_billable=True` vs `False`
- `revenue_query(db)` — join `Invoice` (status=paid) grouped by month, return monthly totals
- `forecast_query(db)` — join `Project` where status in pipeline stages, multiply `budget × probability` (default 0.5 for awarded, 0.2 for quoted)
- `client_summary_query(db)` — join `Client` → `Project` → `Invoice`, group by client, sum revenue

All queries use SQLAlchemy 2 `select()` syntax with `func.sum`, `func.count`, `case`, `extract`. Use `session.execute()`.

### 3. Service
Create `src/backend/services/report_service.py`:
```python
class ReportService:
    def get_project_health(self, db: Session) -> ProjectHealthReport
    def get_utilization(self, db: Session, start_date: date, end_date: date) -> UtilizationReport
    def get_revenue(self, db: Session) -> RevenueForecast
    def get_client_summary(self, db: Session) -> ClientSummaryReport
    def get_executive_kpis(self, db: Session) -> ExecutiveKPIs
    def export_json(self, report: BaseModel) -> dict  # model_dump(mode="json")
```
- Each method delegates to repo query, then constructs the Pydantic model
- `export_json` calls `.model_dump(mode="json")` for safe serialization

### 4. Migration (conditional)
Only if needed for materialized views or summary tables. If all queries are live aggregations, skip migration and note "no schema changes required" in report.

## Files you must NOT touch
- `src/backend/main.py` — register router in Task 02
- `src/backend/models/*.py` — no new models unless materialized views needed
- `src/frontend/` — frontend is Task 03

## Acceptance criteria
- [ ] `pytest tests/wave-8/test_reports_service.py` passes
- [ ] `project_health` returns correct status distribution for test data
- [ ] `utilization` correctly separates billable vs non-billable hours
- [ ] `revenue` aggregates paid invoices by month
- [ ] `client_summary` groups revenue per client
- [ ] `export_json` returns JSON-serializable dict
- [ ] All queries handle empty database gracefully (return zeros/empty lists)
- [ ] `make lint` clean

## Test File
Create `tests/wave-8/test_reports_service.py`:
- `test_project_health_counts` — seed projects in different statuses, verify counts
- `test_project_health_overdue` — create task with past due date, verify overdue count
- `test_utilization_calculation` — seed time entries with billable/non-billable, verify percentages
- `test_revenue_monthly` — seed paid invoices across months, verify aggregation
- `test_client_summary` — seed clients with projects and invoices, verify grouping
- `test_empty_database` — all reports return gracefully with zero values
- `test_export_json_serialization` — verify output is JSON-safe

## Constraints
- Time budget: 45 min
- Use existing patterns from `src/backend/db/repositories/project_repo.py` for query style
- Decimal arithmetic — never use float for money
- No new pip dependencies
- Allowed tools: Read, Write, Edit, Bash, Glob, Grep

## Notes
- Default date range for utilization: current month (1st to today)
- Project probability mapping: Lead=0.1, Quoted=0.3, Awarded=0.6, Design=0.7, Execution=0.9, Closed=1.0
- Budget variance = budget - actual_cost; negative means over budget
- Register models in `src/backend/models/__init__.py` only if new DB tables are created
