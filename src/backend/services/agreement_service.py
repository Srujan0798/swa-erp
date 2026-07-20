import uuid

from sqlalchemy.orm import Session

from src.backend.db.repositories import agreement_repo, audit_repo
from src.backend.models.agreement import ServiceAgreement
from src.backend.schemas.agreement import ServiceAgreementCreate, ServiceAgreementUpdate
from src.backend.services.reference_id_service import generate_reference_id


def list_agreements_service(
    db: Session,
    page: int,
    page_size: int,
    client_id: uuid.UUID | None,
    inquiry_id: uuid.UUID | None,
    status: str | None,
    q: str | None,
) -> tuple[list[ServiceAgreement], int, int, int]:
    items, total = agreement_repo.list_agreements(
        db,
        page=page,
        page_size=page_size,
        client_id=client_id,
        inquiry_id=inquiry_id,
        status=status,
        q=q,
    )
    return items, total, page, page_size


def get_agreement_service(db: Session, agreement_id: uuid.UUID) -> ServiceAgreement | None:
    return agreement_repo.get_by_id(db, agreement_id)


def create_agreement_service(
    db: Session,
    data: ServiceAgreementCreate,
    actor_id: uuid.UUID,
) -> ServiceAgreement:
    reference_id = generate_reference_id(db, "SA")
    payload = data.model_dump()
    payload["reference_id"] = reference_id
    payload["status"] = data.status or "Active"
    agreement = agreement_repo.create(db, payload)
    audit_repo.create_entry(
        db,
        action="service_agreement.create",
        entity_type="service_agreement",
        entity_id=agreement.id,
        user_id=actor_id,
        after_json={
            "id": str(agreement.id),
            "reference_id": agreement.reference_id,
            "client_id": str(agreement.client_id),
            "service_name": agreement.service_name,
            "status": agreement.status,
        },
    )
    return agreement


def update_agreement_service(
    db: Session,
    agreement_id: uuid.UUID,
    data: ServiceAgreementUpdate,
    actor_id: uuid.UUID,
) -> ServiceAgreement | None:
    agreement = agreement_repo.get_by_id(db, agreement_id)
    if not agreement:
        return None
    before = {
        "service_name": agreement.service_name,
        "start_date": str(agreement.start_date),
        "end_date": str(agreement.end_date) if agreement.end_date else None,
        "status": agreement.status,
    }
    update_data = data.model_dump(exclude_unset=True)
    if (
        "start_date" in update_data
        and "end_date" not in update_data
        and agreement.end_date is not None
        and update_data["start_date"] is not None
        and update_data["start_date"] > agreement.end_date
    ):
        raise ValueError("end_date must be on or after start_date")
    if (
        "end_date" in update_data
        and update_data["end_date"] is not None
        and update_data["end_date"] < agreement.start_date
    ):
        raise ValueError("end_date must be on or after start_date")
    agreement_repo.update(db, agreement, update_data)
    audit_repo.create_entry(
        db,
        action="service_agreement.update",
        entity_type="service_agreement",
        entity_id=agreement_id,
        user_id=actor_id,
        before_json=before,
        after_json={
            "service_name": agreement.service_name,
            "start_date": str(agreement.start_date),
            "end_date": str(agreement.end_date) if agreement.end_date else None,
            "status": agreement.status,
        },
    )
    return agreement


def soft_delete_agreement_service(
    db: Session,
    agreement_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> bool:
    agreement = agreement_repo.get_by_id(db, agreement_id)
    if not agreement:
        return False
    agreement_repo.soft_delete(db, agreement)
    audit_repo.create_entry(
        db,
        action="service_agreement.delete",
        entity_type="service_agreement",
        entity_id=agreement_id,
        user_id=actor_id,
        after_json={"deleted_at": str(agreement.deleted_at)},
    )
    return True
