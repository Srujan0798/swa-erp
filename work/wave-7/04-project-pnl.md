# Task 04 — Project P&L Tracking

## Goal
Build cost and revenue tracking for projects. Calculate project-level Profit & Loss by aggregating time costs (hours × rate), material costs, vendor costs, and invoiced revenue. Expose a dashboard endpoint with cost breakdown by category.

Reference spec: `.specify/specs/wave-7/spec.md` section Project P&L.

## Files to Create / Modify

### CREATE: `src/backend/models/project_cost.py`
```python
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.db.base import Base


class ProjectCost(Base):
    __tablename__ = "project_costs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # "time", "material", "vendor", "overhead", "other"
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=True)
    reference_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)  # FK to time_entry, invoice_item, etc.
    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "time_entry", "invoice_item", "manual"
    date: Mapped[date] = mapped_column(Date, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

### MODIFY: `src/backend/models/__init__.py`
Add import for `ProjectCost`.

### CREATE: `src/backend/schemas/project_pnl.py`
- `ProjectCostCreate` — project_id, category, description, amount, quantity (optional), rate (optional), reference_id (optional), reference_type (optional), date
- `ProjectCostRead` — full model with created_by_name
- `ProjectCostListResponse` — paginated list
- `ProjectPnLSummary` — project_id, project_name, total_revenue, total_costs, net_profit, margin_pct, cost_breakdown (by category), revenue_items (invoices)
- `CostBreakdownItem` — category, amount, count, percentage

### CREATE: `src/backend/db/repositories/project_cost_repo.py`
- `create_project_cost(db, data) -> ProjectCost`
- `get_cost_by_id(db, cost_id) -> ProjectCost | None`
- `list_project_costs(db, project_id, category, page, page_size) -> tuple[list, int, int, int]`
- `soft_delete_cost(db, cost_id) -> bool`
- `get_costs_by_category(db, project_id) -> dict[str, Decimal]` — aggregate by category
- `get_time_costs(db, project_id) -> Decimal` — sum of time entry costs (hours × default rate)
- `get_total_costs(db, project_id) -> Decimal` — sum of all project_costs

### CREATE: `src/backend/services/project_pnl_service.py`
- `get_project_pnl(db, project_id) -> ProjectPnLSummary`
  1. Compute revenue: sum of all paid invoice totals for the project
  2. Compute costs:
     - Time costs: sum of billable time entry hours × default rate (5000 INR/hr)
     - Material costs: sum of project_costs where category = "material"
     - Vendor costs: sum of project_costs where category = "vendor"
     - Overhead: sum of project_costs where category = "overhead"
  3. Net profit = revenue - total costs
  4. Margin % = (net profit / revenue) × 100 if revenue > 0 else 0
  5. Cost breakdown by category
- `add_project_cost(db, project_id, user_id, data) -> ProjectCostRead`
- `delete_project_cost(db, cost_id, user_id) -> bool`
- `list_project_costs(db, project_id, category, page, page_size) -> ProjectCostListResponse`
- `get_cost_breakdown(db, project_id) -> list[CostBreakdownItem]`

### CREATE: `src/backend/api/project_pnl.py`
- `GET /api/projects/{project_id}/pnl` — get P&L summary
- `POST /api/projects/{project_id}/costs` — add manual cost entry
- `GET /api/projects/{project_id}/costs` — list costs (filter by category)
- `DELETE /api/projects/{project_id}/costs/{cost_id}` — soft delete cost
- `GET /api/projects/{project_id}/costs/breakdown` — cost breakdown by category

### MODIFY: `src/backend/main.py`
Register project_pnl router.

### CREATE: `src/backend/alembic/versions/0014_add_project_costs.py`
- Create `project_costs` table

## Files you must NOT touch
- `src/backend/models/user.py`
- `src/backend/models/project.py`
- `src/backend/models/invoice.py`
- `src/backend/models/time_entry.py`
- `src/backend/api/auth.py`
- `src/backend/core/security.py`

## Skills to use
- `tdd` — red → green → refactor
- `code-review` — self-review before declaring done

## The core problem (inline)

### Default hourly rate
Use 5000 INR/hour as the default billing rate. This will be configurable per project in a future wave. Store as a constant in the service:
```python
DEFAULT_HOURLY_RATE = Decimal("5000.00")
```

### Cost aggregation logic
```python
def get_project_pnl(db, project_id):
    # Revenue from paid invoices
    revenue = db.query(func.coalesce(func.sum(Invoice.total), 0)).filter(
        Invoice.project_id == project_id,
        Invoice.status == "paid",
        Invoice.deleted_at.is_(None),
    ).scalar()

    # Time costs (billable hours × rate)
    time_entries = db.query(TimeEntry).filter(
        TimeEntry.project_id == project_id,
        TimeEntry.is_billable == True,
        TimeEntry.deleted_at.is_(None),
    ).all()
    time_cost = sum(e.hours for e in time_entries) * DEFAULT_HOURLY_RATE

    # Manual costs by category
    costs_by_cat = get_costs_by_category(db, project_id)

    total_costs = time_cost + sum(costs_by_cat.values())
    net_profit = revenue - total_costs
    margin = (net_profit / revenue * 100) if revenue > 0 else Decimal("0.00")

    return {
        "project_id": project_id,
        "total_revenue": revenue,
        "total_costs": total_costs,
        "net_profit": net_profit,
        "margin_pct": margin,
        "cost_breakdown": [
            {"category": "time", "amount": time_cost, "count": len(time_entries)},
            *[{"category": k, "amount": v, "count": ...} for k, v in costs_by_cat.items()],
        ],
    }
```

### Cost categories
- `time` — computed from time entries (not stored in project_costs, computed on-the-fly)
- `material` — manual or from inventory
- `vendor` — manual or from vendor invoices
- `overhead` — manual
- `other` — manual

### Edge cases
- Project with zero revenue → margin = 0%, display N/A
- Project with zero costs → 0% cost, 100% margin
- Delete a cost → P&L recalculates
- Multiple currencies → always convert to INR for P&L (future concern, store currency for now)

## Acceptance criteria (executable, not prose)
- [ ] `pytest tests/wave-7/test_project_pnl.py` passes
- [ ] `make lint` clean
- [ ] P&L endpoint returns correct totals (revenue, costs, profit, margin)
- [ ] Cost breakdown groups by category with correct amounts
- [ ] Adding a manual cost updates P&L
- [ ] Deleting a cost updates P&L
- [ ] Time costs computed from billable entries only
- [ ] Non-billable entries excluded from time costs

## Test File
Create `tests/wave-7/test_project_pnl.py` with at least:
- `test_pnl_empty_project` — zero revenue, zero costs
- `test_pnl_with_time_costs` — correct calculation
- `test_pnl_with_manual_costs` — material/vendor/overhead
- `test_pnl_revenue_from_invoices` — paid invoices count
- `test_pnl_excludes_unpaid_invoices` — draft/sent don't count
- `test_cost_breakdown_by_category` — correct grouping
- `test_add_manual_cost` — appears in breakdown
- `test_delete_cost` — removed from breakdown
- `test_margin_calculation` — (revenue - costs) / revenue × 100
- `test_pnl_non_billable_excluded` — is_billable=False entries not in time costs

## How to deliver
1. Implement model, schemas, repo, service, API, migration + tests
2. Run `pytest tests/wave-7/test_project_pnl.py` — all pass
3. Run `make lint` — clean
4. Write report to `work/reports/wave-7/04-project-pnl.report.md`
5. Stop

## Constraints
- Time budget: 40 min
- No new dependencies without flagging
- Match existing patterns (see `src/backend/db/repositories/project_repo.py`, `src/backend/services/project_service.py`)
- Allowed tools: `ruff`, `black`, `pytest`, `alembic`
