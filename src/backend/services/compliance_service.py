import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.compliance_repo import (
    CHECKLIST_SEEDS,
    create_project_compliance_item,
    get_checklist_item_by_id,
    get_checklist_items_by_standard,
    get_compliance_summary,
    get_project_compliance_item,
    get_project_compliance_items,
    get_standards,
    review_project_compliance_item,
    seed_checklist_items,
    seed_standards,
    update_project_compliance_item,
)
from src.backend.schemas.compliance import (
    ComplianceDashboardResponse,
    ComplianceSummaryResponse,
)


def initialize_compliance(db: Session) -> int:
    standards = seed_standards(db)
    total_items = 0
    for std in standards:
        items = CHECKLIST_SEEDS.get(std.name, [])
        if items:
            created = seed_checklist_items(db, std.id, items)
            total_items += len(created)
    return total_items


def get_standards_list(db: Session) -> list:
    return get_standards(db)


def get_checklist_items_list(db: Session, standard_id: uuid.UUID) -> list:
    return get_checklist_items_by_standard(db, standard_id)


def create_project_compliance_item_service(
    db: Session,
    project_id: uuid.UUID,
    checklist_item_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> dict[str, Any]:
    checklist_item = get_checklist_item_by_id(db, checklist_item_id)
    if not checklist_item:
        raise ValueError("checklist_item_not_found")

    existing = get_project_compliance_item(db, project_id=project_id, checklist_item_id=checklist_item_id)
    if existing:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Already exists")

    item = create_project_compliance_item(db, project_id, checklist_item_id)

    create_entry(
        db,
        action="compliance.item_created",
        entity_type="project_compliance_item",
        user_id=actor_id,
        entity_id=item.id,
        after_json={"project_id": str(project_id), "checklist_item_id": str(checklist_item_id)},
    )

    return _pci_to_dict(item)


def update_compliance_item_status_service(
    db: Session,
    item_id: uuid.UUID,
    status: str,
    evidence_document_id: uuid.UUID | None,
    notes: str | None,
    actor_id: uuid.UUID,
) -> dict[str, Any]:
    existing = get_project_compliance_item(db, item_id)
    if not existing:
        raise ValueError("item_not_found")

    before = _pci_to_dict(existing)

    update_data: dict[str, Any] = {}
    if status is not None:
        update_data["status"] = status
    if evidence_document_id is not None:
        update_data["evidence_document_id"] = evidence_document_id
    if notes is not None:
        update_data["notes"] = notes

    item = update_project_compliance_item(db, item_id, **update_data)
    if not item:
        raise ValueError("item_not_found")

    after = _pci_to_dict(item)

    create_entry(
        db,
        action="compliance.status_changed",
        entity_type="project_compliance_item",
        user_id=actor_id,
        entity_id=item_id,
        before_json=before,
        after_json=after,
    )

    return after


def review_compliance_item_service(
    db: Session,
    item_id: uuid.UUID,
    reviewed_by: uuid.UUID,
    notes: str | None = None,
) -> dict[str, Any]:
    existing = get_project_compliance_item(db, item_id)
    if not existing:
        raise ValueError("item_not_found")

    before = _pci_to_dict(existing)

    if notes:
        update_project_compliance_item(db, item_id, notes=notes)

    item = review_project_compliance_item(db, item_id, reviewed_by)
    if not item:
        raise ValueError("item_not_found")

    after = _pci_to_dict(item)

    create_entry(
        db,
        action="compliance.reviewed",
        entity_type="project_compliance_item",
        user_id=reviewed_by,
        entity_id=item_id,
        before_json=before,
        after_json=after,
    )

    return after


def get_compliance_summary_service(db: Session, project_id: uuid.UUID) -> ComplianceSummaryResponse:
    summaries = get_compliance_summary(db, project_id)
    dashboard = [ComplianceDashboardResponse(**s) for s in summaries]

    total_applicable = sum(s.total_items - s.na_count for s in dashboard)
    total_compliant = sum(s.compliant_count for s in dashboard)
    overall = (total_compliant / total_applicable * 100) if total_applicable > 0 else 0.0

    return ComplianceSummaryResponse(
        project_id=project_id,
        standards=dashboard,
        overall_percentage=round(overall, 2),
    )


def get_project_items_list(
    db: Session, project_id: uuid.UUID, standard_id: uuid.UUID | None = None
) -> list[dict]:
    return get_project_compliance_items(db, project_id, standard_id)


def _pci_to_dict(item) -> dict[str, Any]:
    return {
        "id": str(item.id),
        "project_id": str(item.project_id),
        "checklist_item_id": str(item.checklist_item_id),
        "status": item.status,
        "evidence_document_id": str(item.evidence_document_id) if item.evidence_document_id else None,
        "notes": item.notes,
        "reviewed_by": str(item.reviewed_by) if item.reviewed_by else None,
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }
