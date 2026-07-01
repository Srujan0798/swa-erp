import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from src.backend.models.project_cost import ProjectCost


def create_project_cost(db: Session, data: dict[str, Any]) -> ProjectCost:
    cost = ProjectCost(**data)
    db.add(cost)
    db.commit()
    db.refresh(cost)
    return cost


def get_cost_by_id(db: Session, cost_id: uuid.UUID) -> ProjectCost | None:
    return db.query(ProjectCost).filter(
        ProjectCost.id == cost_id,
        ProjectCost.deleted_at.is_(None),
    ).first()


def list_project_costs(
    db: Session,
    project_id: uuid.UUID,
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ProjectCost], int, int, int]:
    query = db.query(ProjectCost).filter(
        ProjectCost.project_id == project_id,
        ProjectCost.deleted_at.is_(None),
    )

    if category:
        query = query.filter(ProjectCost.category == category)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(ProjectCost.date.desc()).offset(offset).limit(page_size).all()

    return items, total, page, page_size


def soft_delete_cost(db: Session, cost_id: uuid.UUID) -> bool:
    cost = get_cost_by_id(db, cost_id)
    if not cost:
        return False
    cost.deleted_at = datetime.utcnow()
    db.commit()
    return True


def get_costs_by_category(db: Session, project_id: uuid.UUID) -> dict[str, Decimal]:
    results = (
        db.query(
            ProjectCost.category,
            sa_func.coalesce(sa_func.sum(ProjectCost.amount), 0),
            sa_func.count(ProjectCost.id),
        )
        .filter(
            ProjectCost.project_id == project_id,
            ProjectCost.deleted_at.is_(None),
        )
        .group_by(ProjectCost.category)
        .all()
    )
    return {row[0]: row[1] for row in results}


def get_costs_count_by_category(db: Session, project_id: uuid.UUID) -> dict[str, int]:
    results = (
        db.query(
            ProjectCost.category,
            sa_func.count(ProjectCost.id),
        )
        .filter(
            ProjectCost.project_id == project_id,
            ProjectCost.deleted_at.is_(None),
        )
        .group_by(ProjectCost.category)
        .all()
    )
    return {row[0]: row[1] for row in results}


def get_total_costs(db: Session, project_id: uuid.UUID) -> Decimal:
    result = (
        db.query(sa_func.coalesce(sa_func.sum(ProjectCost.amount), 0))
        .filter(
            ProjectCost.project_id == project_id,
            ProjectCost.deleted_at.is_(None),
        )
        .scalar()
    )
    return result
