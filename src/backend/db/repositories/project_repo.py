import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.backend.models.project import Project


def list_projects(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
    status: str | None = None,
    client_id: uuid.UUID | None = None,
) -> tuple[list[Project], int, int, int]:
    query = db.query(Project).filter(Project.deleted_at.is_(None))

    if client_id is not None:
        query = query.filter(Project.client_id == client_id)

    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Project.name.ilike(search_term),
                Project.code.ilike(search_term),
                Project.location.ilike(search_term),
            )
        )

    if status:
        query = query.filter(Project.status == status)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Project.created_at.desc()).offset(offset).limit(page_size).all()

    return items, total, page, page_size


def get_by_id(db: Session, project_id: uuid.UUID) -> Project | None:
    return (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.deleted_at.is_(None),
        )
        .first()
    )


class ProjectVersionConflictError(Exception):
    """Raised when an update carries a stale expected_version (optimistic lock miss)."""


def _get_by_id_locked(db: Session, project_id: uuid.UUID) -> Project | None:
    return (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.deleted_at.is_(None),
        )
        .with_for_update()
        .first()
    )


def create_project(db: Session, data: dict[str, Any]) -> Project:
    project = Project(**data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(
    db: Session,
    project_id: uuid.UUID,
    data: dict[str, Any],
    expected_version: int | None = None,
) -> Project | None:
    project = _get_by_id_locked(db, project_id)
    if not project:
        return None

    if expected_version is not None and expected_version != project.version:
        raise ProjectVersionConflictError(
            f"Project {project_id} was modified by another user; expected version "
            f"{expected_version}, current version {project.version}"
        )

    for key, value in data.items():
        if value is not None:
            setattr(project, key, value)

    project.version += 1
    db.commit()
    db.refresh(project)
    return project


def soft_delete_project(db: Session, project_id: uuid.UUID) -> bool:
    project = get_by_id(db, project_id)
    if not project:
        return False
    project.deleted_at = datetime.now(tz=UTC)
    db.commit()
    return True


def get_project_with_names(db: Session, project_id: uuid.UUID) -> dict | None:
    from src.backend.db.repositories.client_repo import get_by_id as get_client_by_id
    from src.backend.db.repositories.user_repo import get_by_id as get_user_by_id

    project = get_by_id(db, project_id)
    if not project:
        return None

    client = get_client_by_id(db, project.client_id) if project.client_id else None
    pm = get_user_by_id(db, project.pm_id) if project.pm_id else None
    designer = get_user_by_id(db, project.designer_id) if project.designer_id else None
    auditor = get_user_by_id(db, project.auditor_id) if project.auditor_id else None
    inquiry_ref = None
    if project.inquiry_id:
        from src.backend.db.repositories.inquiry_repo import get_by_id as get_inquiry_by_id

        inquiry = get_inquiry_by_id(db, project.inquiry_id)
        inquiry_ref = inquiry.reference_id if inquiry else None

    return {
        "id": project.id,
        "client_id": project.client_id,
        "name": project.name,
        "code": project.code,
        "description": project.description,
        "status": project.status,
        "pm_id": project.pm_id,
        "designer_id": project.designer_id,
        "auditor_id": project.auditor_id,
        "location": project.location,
        "estimated_value": project.estimated_value,
        "actual_value": project.actual_value,
        "start_date": project.start_date,
        "target_end_date": project.target_end_date,
        "actual_end_date": project.actual_end_date,
        "inquiry_id": project.inquiry_id,
        "milestone": project.milestone,
        "progress_indicators": project.progress_indicators,
        "team_leader_name": project.team_leader_name,
        "project_owner_name": project.project_owner_name,
        "notes": project.notes,
        "is_active": project.is_active,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "version": project.version,
        "client_name": client.name if client else None,
        "pm_name": pm.name if pm else None,
        "designer_name": designer.name if designer else None,
        "auditor_name": auditor.name if auditor else None,
        "inquiry_reference_id": inquiry_ref,
    }


def list_projects_with_names(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
    status: str | None = None,
    client_id: uuid.UUID | None = None,
) -> tuple[list[dict[str, Any]], int, int, int]:
    projects, total, page, page_size = list_projects(
        db, page, page_size, q, status, client_id=client_id
    )

    from src.backend.db.repositories.client_repo import get_by_id as get_client_by_id
    from src.backend.db.repositories.user_repo import get_by_id as get_user_by_id

    from src.backend.db.repositories.inquiry_repo import get_by_id as get_inquiry_by_id

    result = []
    for p in projects:
        client = get_client_by_id(db, p.client_id) if p.client_id else None
        pm = get_user_by_id(db, p.pm_id) if p.pm_id else None
        designer = get_user_by_id(db, p.designer_id) if p.designer_id else None
        auditor = get_user_by_id(db, p.auditor_id) if p.auditor_id else None
        inquiry_ref = None
        if p.inquiry_id:
            inquiry = get_inquiry_by_id(db, p.inquiry_id)
            inquiry_ref = inquiry.reference_id if inquiry else None

        item = {
            "id": p.id,
            "client_id": p.client_id,
            "name": p.name,
            "code": p.code,
            "description": p.description,
            "status": p.status,
            "pm_id": p.pm_id,
            "designer_id": p.designer_id,
            "auditor_id": p.auditor_id,
            "location": p.location,
            "estimated_value": p.estimated_value,
            "actual_value": p.actual_value,
            "start_date": p.start_date,
            "target_end_date": p.target_end_date,
            "actual_end_date": p.actual_end_date,
            "inquiry_id": p.inquiry_id,
            "milestone": p.milestone,
            "progress_indicators": p.progress_indicators,
            "team_leader_name": p.team_leader_name,
            "project_owner_name": p.project_owner_name,
            "notes": p.notes,
            "is_active": p.is_active,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "version": p.version,
            "client_name": client.name if client else None,
            "pm_name": pm.name if pm else None,
            "designer_name": designer.name if designer else None,
            "auditor_name": auditor.name if auditor else None,
            "inquiry_reference_id": inquiry_ref,
        }
        result.append(item)

    return result, total, page, page_size
