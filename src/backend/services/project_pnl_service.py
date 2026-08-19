import uuid
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from src.backend.db.repositories.project_cost_repo import (
    create_project_cost,
    get_costs_by_category,
    get_costs_count_by_category,
    get_total_costs,
    list_project_costs,
    soft_delete_cost,
)
from src.backend.db.repositories.user_repo import get_by_id as get_user_by_id
from src.backend.schemas.pnl import (
    CostBreakdownItem,
    ProjectCostCreate,
    ProjectCostListResponse,
    ProjectCostRead,
    ProjectPnLSummary,
)

DEFAULT_HOURLY_RATE = Decimal("5000.00")

COST_CATEGORIES = ["time", "material", "vendor", "overhead", "other"]


def _get_revenue(db: Session, project_id: uuid.UUID) -> Decimal:
    from src.backend.models.invoice import Invoice

    result = (
        db.query(Invoice.total)
        .filter(
            Invoice.project_id == project_id,
            Invoice.status == "paid",
            Invoice.deleted_at.is_(None),
        )
        .all()
    )
    return sum(row[0] for row in result) if result else Decimal("0.00")


def _get_time_cost(db: Session, project_id: uuid.UUID) -> tuple[Decimal, int]:
    from src.backend.models.time_tracking import TimeEntry

    entries = (
        db.query(TimeEntry)
        .filter(
            TimeEntry.project_id == project_id,
            TimeEntry.is_billable.is_(True),
            TimeEntry.deleted_at.is_(None),
        )
        .all()
    )
    total_hours = sum(e.hours for e in entries)
    cost = total_hours * DEFAULT_HOURLY_RATE
    return cost, len(entries)


def get_cost_breakdown(
    db: Session,
    project_id: uuid.UUID,
) -> list[CostBreakdownItem]:
    time_cost, time_count = _get_time_cost(db, project_id)
    costs_by_cat = get_costs_by_category(db, project_id)
    counts_by_cat = get_costs_count_by_category(db, project_id)

    items: list[CostBreakdownItem] = []

    if time_cost > 0:
        items.append(
            CostBreakdownItem(
                category="time",
                amount=time_cost,
                count=time_count,
                percentage=Decimal("0"),
            )
        )

    for cat in COST_CATEGORIES:
        if cat == "time":
            continue
        amount = costs_by_cat.get(cat, Decimal("0"))
        count = counts_by_cat.get(cat, 0)
        if amount > 0:
            items.append(
                CostBreakdownItem(
                    category=cat,
                    amount=amount,
                    count=count,
                    percentage=Decimal("0"),
                )
            )

    total = sum(item.amount for item in items)
    if total > 0:
        for item in items:
            item.percentage = (item.amount / total * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

    return items


def get_project_pnl(db: Session, project_id: uuid.UUID) -> ProjectPnLSummary:
    from src.backend.db.repositories.project_repo import get_by_id as get_project_by_id

    project = get_project_by_id(db, project_id)
    project_name = project.name if project else None

    revenue = _get_revenue(db, project_id)
    time_cost, _ = _get_time_cost(db, project_id)
    manual_costs = get_total_costs(db, project_id)
    total_costs = time_cost + manual_costs
    net_profit = revenue - total_costs
    margin = (
        (net_profit / revenue * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if revenue > 0
        else Decimal("0.00")
    )

    breakdown = get_cost_breakdown(db, project_id)

    return ProjectPnLSummary(
        project_id=project_id,
        project_name=project_name,
        total_revenue=revenue,
        total_costs=total_costs,
        net_profit=net_profit,
        margin_pct=margin,
        cost_breakdown=breakdown,
    )


def add_project_cost(
    db: Session,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    data: ProjectCostCreate,
) -> ProjectCostRead:
    cost_data = data.model_dump(exclude={"project_id"})
    cost_data["project_id"] = project_id
    cost_data["created_by"] = user_id
    cost = create_project_cost(db, cost_data)
    user = get_user_by_id(db, user_id)
    return ProjectCostRead(
        **ProjectCostRead.model_validate(cost).model_dump(exclude={"created_by_name"}),
        created_by_name=user.name if user else None,
    )


def delete_project_cost(db: Session, cost_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    return soft_delete_cost(db, cost_id)


def list_project_costs_service(
    db: Session,
    project_id: uuid.UUID,
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> ProjectCostListResponse:
    items, total, pg, ps = list_project_costs(db, project_id, category, page, page_size)
    reads = []
    for cost in items:
        user = get_user_by_id(db, cost.created_by)
        reads.append(
            ProjectCostRead(
                **ProjectCostRead.model_validate(cost).model_dump(exclude={"created_by_name"}),
                created_by_name=user.name if user else None,
            )
        )
    return ProjectCostListResponse(items=reads, total=total, page=pg, page_size=ps)
