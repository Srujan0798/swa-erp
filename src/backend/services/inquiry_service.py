import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.backend.db.repositories import audit_repo
from src.backend.db.repositories.client_repo import create as create_client
from src.backend.db.repositories.client_repo import get_by_id as get_client_by_id
from src.backend.db.repositories.inquiry_repo import create as create_inquiry
from src.backend.db.repositories.inquiry_repo import get_by_id as get_inquiry_by_id
from src.backend.db.repositories.inquiry_repo import list_inquiries
from src.backend.db.repositories.inquiry_repo import soft_delete as soft_delete_inquiry
from src.backend.db.repositories.inquiry_repo import update as update_inquiry
from src.backend.db.repositories.project_repo import create_project
from src.backend.models.client import Client
from src.backend.models.inquiry import Inquiry
from src.backend.schemas.inquiry import (
    InquiryConvertRequest,
    InquiryCreate,
    InquiryUpdate,
)
from src.backend.services.reference_id_service import generate_reference_id


class InquiryConversionError(Exception):
    def __init__(self, status_code: int, body: dict[str, Any]):
        self.status_code = status_code
        self.body = body
        super().__init__(body.get("detail", "Inquiry conversion error"))


def list_inquiries_service(
    db: Session,
    page: int,
    page_size: int,
    q: str | None,
    status: str | None,
) -> tuple[list[Inquiry], int, int, int]:
    items, total = list_inquiries(db, page=page, page_size=page_size, q=q, status=status)
    return items, total, page, page_size


def get_inquiry_service(db: Session, inquiry_id: uuid.UUID) -> Inquiry | None:
    return get_inquiry_by_id(db, inquiry_id)


def create_inquiry_service(
    db: Session,
    data: InquiryCreate,
    actor_id: uuid.UUID,
) -> Inquiry:
    reference_id = generate_reference_id(db, "INQ")
    payload = data.model_dump()
    payload["reference_id"] = reference_id
    payload["status"] = data.status or "New"
    inquiry = create_inquiry(db, payload)

    audit_repo.create_entry(
        db,
        action="inquiry.create",
        entity_type="inquiry",
        entity_id=inquiry.id,
        user_id=actor_id,
        after_json={
            "id": str(inquiry.id),
            "reference_id": inquiry.reference_id,
            "client_name": inquiry.client_name,
            "status": inquiry.status,
        },
    )
    return inquiry


def update_inquiry_service(
    db: Session,
    inquiry_id: uuid.UUID,
    data: InquiryUpdate,
    actor_id: uuid.UUID,
) -> Inquiry | None:
    inquiry = get_inquiry_by_id(db, inquiry_id)
    if not inquiry:
        return None
    before = {
        "status": inquiry.status,
        "client_name": inquiry.client_name,
        "priority": inquiry.priority,
    }
    update_inquiry(db, inquiry, data.model_dump(exclude_unset=True))
    audit_repo.create_entry(
        db,
        action="inquiry.update",
        entity_type="inquiry",
        entity_id=inquiry_id,
        user_id=actor_id,
        before_json=before,
        after_json={
            "status": inquiry.status,
            "client_name": inquiry.client_name,
            "priority": inquiry.priority,
        },
    )
    return inquiry


def soft_delete_inquiry_service(
    db: Session,
    inquiry_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> bool:
    inquiry = get_inquiry_by_id(db, inquiry_id)
    if not inquiry:
        return False
    soft_delete_inquiry(db, inquiry)
    audit_repo.create_entry(
        db,
        action="inquiry.delete",
        entity_type="inquiry",
        entity_id=inquiry_id,
        user_id=actor_id,
        after_json={"deleted_at": str(inquiry.deleted_at)},
    )
    return True


def _find_clients_exact(db: Session, name: str) -> list[Client]:
    return (
        db.query(Client)
        .filter(Client.name == name, Client.deleted_at.is_(None))
        .all()
    )


def _build_default_client_code(db: Session) -> str:
    return generate_reference_id(db, "CLT")


def _generate_project_code(db: Session) -> str:
    from src.backend.models.project import Project

    year = datetime.now(UTC).year
    seq = 1
    while True:
        code = f"PRJ-{year}-{seq:03d}"
        exists = db.query(Project).filter_by(code=code).first()
        if not exists:
            return code
        seq += 1


def convert_inquiry(
    db: Session,
    inquiry_id: uuid.UUID,
    req: InquiryConvertRequest,
    actor_id: uuid.UUID,
) -> dict[str, Any]:
    inquiry = get_inquiry_by_id(db, inquiry_id)
    if not inquiry:
        raise InquiryConversionError(404, {"detail": "Inquiry not found"})
    if inquiry.status == "Converted":
        raise InquiryConversionError(409, {"detail": "Inquiry already converted"})

    client: Client | None = None
    if req.client_id is not None:
        client = get_client_by_id(db, req.client_id)
        if not client:
            raise InquiryConversionError(404, {"detail": "Specified client not found"})
    else:
        candidates = _find_clients_exact(db, inquiry.client_name)
        if len(candidates) == 1:
            client = candidates[0]
        elif len(candidates) > 1:
            raise InquiryConversionError(
                300,
                {
                    "detail": "Ambiguous client match",
                    "inquiry_client_name": inquiry.client_name,
                    "candidates": [
                        {"id": str(c.id), "name": c.name, "code": c.code} for c in candidates
                    ],
                },
            )
        else:
            client = _create_client_from_inquiry(db, inquiry, req, actor_id)
            client.first_inquiry_id = inquiry.id
            db.commit()
            db.refresh(client)

    project = _create_project_from_inquiry(db, client, inquiry, req, actor_id)

    inquiry.status = "Converted"
    inquiry.converted_client_id = client.id
    inquiry.converted_project_id = project.id
    db.commit()
    db.refresh(inquiry)

    audit_repo.create_entry(
        db,
        action="inquiry.convert",
        entity_type="inquiry",
        entity_id=inquiry.id,
        user_id=actor_id,
        after_json={
            "inquiry_id": str(inquiry.id),
            "client_id": str(client.id),
            "project_id": str(project.id),
        },
    )

    return {
        "inquiry": inquiry,
        "client": client,
        "project": project,
    }


def _create_client_from_inquiry(
    db: Session,
    inquiry: Inquiry,
    req: InquiryConvertRequest,
    actor_id: uuid.UUID,
) -> Client:
    primary_email = (
        req.client_primary_email
        or f"inquiry+{inquiry.reference_id.lower().replace(' ', '-')}@swa.internal"
    )
    code = _build_default_client_code(db)
    client = create_client(
        db,
        name=inquiry.client_name,
        code=code,
        primary_email=primary_email,
        address=req.client_address,
        city=req.client_city,
        state=req.client_state,
        pincode=req.client_pincode,
        country=req.client_country or "India",
        gst_number=req.client_gst_number,
        primary_phone=req.client_primary_phone,
    )
    if req.client_industry:
        client.industry = req.client_industry
        db.commit()
        db.refresh(client)
    audit_repo.create_entry(
        db,
        action="client.create",
        entity_type="client",
        entity_id=client.id,
        user_id=actor_id,
        after_json={
            "id": str(client.id),
            "name": client.name,
            "code": client.code,
            "primary_email": client.primary_email,
            "from_inquiry": str(inquiry.id),
        },
    )
    return client


def _create_project_from_inquiry(
    db: Session,
    client: Client,
    inquiry: Inquiry,
    req: InquiryConvertRequest,
    actor_id: uuid.UUID,
) -> Any:
    project_code = req.project_code or _generate_project_code(db)
    payload = {
        "client_id": client.id,
        "name": req.project_name,
        "code": project_code,
        "description": req.project_description,
        "status": req.project_status or "Awarded",
        "pm_id": req.pm_id,
        "designer_id": req.designer_id,
        "auditor_id": req.auditor_id,
        "location": req.location,
        "estimated_value": req.estimated_value
        if req.estimated_value is not None
        else inquiry.estimated_value,
        "start_date": req.start_date,
        "target_end_date": req.target_end_date,
    }
    project = create_project(db, payload)
    audit_repo.create_entry(
        db,
        action="project.create",
        entity_type="project",
        entity_id=project.id,
        user_id=actor_id,
        after_json={
            "id": str(project.id),
            "client_id": str(client.id),
            "name": project.name,
            "code": project.code,
            "from_inquiry": str(inquiry.id),
        },
    )
    return project
