# Task 01 — Sustainability Metrics API + Frontend

## What to do
Implement SustainabilityMetric: per-project green-building metrics, entered manually when a
client provides data. Field list and types below are taken directly from the real
`resources/ERP_Sheets_Extracted/ERP Sheets/Sustainability Metrics Sheet.xlsx` — NOT guessed.
Confirmed for this wave per `docs/decisions/0002-core-id-chain-gap.md` item #5.

Real header row + one sample data row:
```
Sr No | Date | Reference ID       | Compliant with Green Standards | Total Energy Saved (kWh) | CO2 emissions avoided (tCO2e) | Lifecycle Cost savings delivered (INR) | Insulation Efficiency (Actual/Expected) | Payback Period (Months)
1     |      | SWA-2025-PRJ-065   | No                              |                           |                                |                                         | 0.89                                     |
```
**Correction from an earlier draft of this task**, which invented a `green_standard: str` field
and used years instead of months — wrong on both counts. The real field is a Yes/No compliance
flag, and payback period is tracked in months.

## Files to create
- CREATE: `src/backend/models/sustainability_metric.py`
- CREATE: `src/backend/schemas/sustainability_metric.py`
- CREATE: `src/backend/db/repositories/sustainability_metric_repo.py`
- CREATE: `src/backend/services/sustainability_metric_service.py`
- CREATE: `src/backend/api/sustainability_metrics.py`
- CREATE: `src/backend/alembic/versions/0018_add_sustainability_metrics.py`
- CREATE: `tests/wave-10/test_sustainability_metrics.py`
- CREATE: `src/frontend/src/pages/SustainabilityPage.tsx`
- CREATE: `src/frontend/src/components/sustainability/SustainabilityForm.tsx`
- CREATE: `src/frontend/src/components/sustainability/SustainabilityList.tsx`
- CREATE: `src/frontend/src/hooks/useSustainability.ts`

## Files to modify
- MODIFY: `src/backend/models/__init__.py`, `src/backend/api/__init__.py`, `src/backend/main.py`
- MODIFY: `src/frontend/src/App.tsx` — route `/sustainability`
- MODIFY: `src/frontend/src/components/layout/Sidebar.tsx` — nav item
- MODIFY: `src/frontend/src/lib/api.ts`, `src/frontend/src/types/api.ts`

## Files you must NOT touch
- `src/backend/models/compliance.py` (different domain — regulatory checklist, not metrics)

## The core problem (inline)

### Model
```python
class SustainabilityMetric(Base):
    __tablename__ = "sustainability_metrics"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    reference_id: Mapped[str | None] = mapped_column(String(30), nullable=True)  # e.g. "SWA-2025-PRJ-065" per real sample data
    recorded_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    compliant_with_green_standards: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # Yes/No in sheet
    energy_saved_kwh: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    co2_avoided_tco2e: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    lifecycle_cost_savings_inr: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    insulation_efficiency_ratio: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)  # actual/expected ratio, e.g. 0.89 — NOT a percentage
    payback_period_months: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)  # months, not years
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at / updated_at: standard pattern
```
All metric fields nullable — data arrives incrementally as the client provides it, per Meeting 1
("Sustainability metrics is like project sustainability... entered when the client figures out
the ID"). `reference_id` links loosely to a Project's display ID as free text, not a hard FK to
`document_references` or `tokens` — the sheet just stores the string.

### Frontend
Simple list + form scoped to a Project (mount as a tab on Project detail, matching how Compliance
is already mounted — check `src/frontend/src/components/projects/` for the existing tab pattern).

## Acceptance criteria
- [ ] `python3 -m pytest tests/wave-10/ -q` passes
- [ ] `ruff check src/backend/models/sustainability_metric.py` clean
- [ ] `npm run typecheck` clean
- [ ] Create a metric via UI against a running backend, appears in list

## How to deliver
1. Implement backend + frontend + tests
2. Run acceptance commands
3. Write report to `work/reports/wave-10/01-sustainability-metrics.report.md`
4. Stop

## Constraints
- Time budget: 75 min
- All metric fields optional — don't add required-field validation beyond project_id/recorded_date
- Allowed tools: file edit, pytest, ruff, npm
