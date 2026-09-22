import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.backend.core.lifecycle import ProjectStatus, can_transition
from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.project_repo import get_by_id as get_project_by_id
from src.backend.models.project import Project


def get_project_stats(db: Session) -> dict[str, Any]:
    """Dashboard aggregates over active, non-deleted projects.

    Lives here (not in the router) so query logic stays in the service layer.
    """
    query = (
        db.query(Project.status, func.count(Project.id))
        .filter(Project.deleted_at.is_(None), Project.is_active.is_(True))
        .group_by(Project.status)
    )

    status_counts = {status.value: 0 for status in ProjectStatus}
    for status_val, count in query.all():
        status_counts[status_val] = count

    total_active = sum(status_counts.values())

    total_estimated = (
        db.query(func.sum(Project.estimated_value))
        .filter(Project.deleted_at.is_(None), Project.is_active.is_(True))
        .scalar()
    )
    return {
        "total_active": total_active,
        "by_status": status_counts,
        "total_estimated_value": (
            Decimal(total_estimated) if total_estimated is not None else Decimal("0")
        ),
    }


def transition_project(
    db: Session,
    project_id: uuid.UUID,
    to_status: ProjectStatus,
    actor_id: uuid.UUID,
    reason: str | None = None,
):
    project = get_project_by_id(db, project_id)
    if not project:
        return None
    if project.deleted_at:
        return None

    current = ProjectStatus(project.status)
    if not can_transition(current, to_status):
        raise ValueError(f"Cannot transition from {current.value} to {to_status.value}")

    before_json = {"status": project.status}
    project.status = to_status.value
    project.version += 1

    if to_status == ProjectStatus.CLOSED:
        project.actual_end_date = date.today()
    if to_status == ProjectStatus.EXECUTION and not project.start_date:
        project.start_date = date.today()

    db.commit()
    db.refresh(project)

    after_json = {"status": project.status}
    if project.actual_end_date:
        after_json["actual_end_date"] = str(project.actual_end_date)
    if project.start_date:
        after_json["start_date"] = str(project.start_date)

    create_entry(
        db,
        action="project.transition",
        entity_type="project",
        entity_id=project.id,
        user_id=actor_id,
        before_json=before_json,
        after_json=after_json,
    )

    return project
