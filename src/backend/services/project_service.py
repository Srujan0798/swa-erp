import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.project_repo import (
    ProjectVersionConflictError,
    create_project,
    get_project_with_names,
    list_projects_with_names,
    soft_delete_project,
    update_project,
)
from src.backend.db.repositories.project_repo import (
    get_by_id as get_project_by_id,
)
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectCreate, ProjectUpdate


def create_project_service(
    db: Session,
    data: ProjectCreate,
    actor_id: uuid.UUID,
) -> dict[str, Any]:
    project = create_project(db, data.model_dump())

    result = get_project_with_names(db, project.id)
    if result:
        record_event(
            db,
            action="project.create",
            entity_type="project",
            user_id=actor_id,
            entity_id=project.id,
            after_json=_project_to_dict(project),
        )

    return result


def get_project_service(db: Session, project_id: uuid.UUID) -> dict[str, Any] | None:
    return get_project_with_names(db, project_id)


def list_projects_service(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
    status: str | None = None,
    client_id: uuid.UUID | None = None,
) -> tuple[list[dict[str, Any]], int, int, int]:
    return list_projects_with_names(
        db,
        page=page,
        page_size=page_size,
        q=q,
        status=status,
        client_id=client_id,
    )


def update_project_service(
    db: Session,
    project_id: uuid.UUID,
    data: ProjectUpdate,
    actor_id: uuid.UUID,
) -> dict[str, Any] | None:
    project = get_project_by_id(db, project_id)
    if not project:
        return None

    before_json = _project_to_dict(project)

    update_data = data.model_dump(exclude_unset=True)
    expected_version = update_data.pop("expected_version", None)
    try:
        update_project(db, project_id, update_data, expected_version)
    except ProjectVersionConflictError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e)) from e

    project = get_project_by_id(db, project_id)
    after_json = _project_to_dict(project)

    record_event(
        db,
        action="project.update",
        entity_type="project",
        user_id=actor_id,
        entity_id=project_id,
        before_json=before_json,
        after_json=after_json,
    )

    return get_project_with_names(db, project_id)


def soft_delete_project_service(
    db: Session,
    project_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> bool:
    project = get_project_by_id(db, project_id)
    if not project:
        return False

    before_json = _project_to_dict(project)

    success = soft_delete_project(db, project_id)

    if success:
        record_event(
            db,
            action="project.delete",
            entity_type="project",
            user_id=actor_id,
            entity_id=project_id,
            before_json=before_json,
        )

    return success


def record_event(
    db: Session,
    action: str,
    entity_type: str,
    user_id: uuid.UUID | None = None,
    entity_id: uuid.UUID | None = None,
    before_json: dict | None = None,
    after_json: dict | None = None,
) -> None:
    create_entry(
        db,
        action=action,
        entity_type=entity_type,
        user_id=user_id,
        entity_id=entity_id,
        before_json=before_json,
        after_json=after_json,
    )


def _project_to_dict(project: Project) -> dict[str, Any]:
    return {
        "id": str(project.id),
        "client_id": str(project.client_id),
        "name": project.name,
        "code": project.code,
        "description": project.description,
        "status": project.status,
        "pm_id": str(project.pm_id) if project.pm_id else None,
        "designer_id": str(project.designer_id) if project.designer_id else None,
        "auditor_id": str(project.auditor_id) if project.auditor_id else None,
        "location": project.location,
        "estimated_value": str(project.estimated_value) if project.estimated_value else None,
        "actual_value": str(project.actual_value) if project.actual_value else None,
        "start_date": str(project.start_date) if project.start_date else None,
        "target_end_date": str(project.target_end_date) if project.target_end_date else None,
        "actual_end_date": str(project.actual_end_date) if project.actual_end_date else None,
        "is_active": project.is_active,
        "version": project.version,
    }
