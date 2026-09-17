import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy.orm import Session

from src.backend.db.repositories import audit_repo
from src.backend.db.repositories.client_repo import get_by_id as get_client_by_id
from src.backend.db.repositories.inquiry_repo import (
    create as create_inquiry,
)
from src.backend.db.repositories.inquiry_repo import (
    get_by_id as get_inquiry_by_id,
)
from src.backend.db.repositories.inquiry_repo import (
    list_inquiries,
)
from src.backend.db.repositories.inquiry_repo import (
    update as update_inquiry,
)
from src.backend.models.client import Client
from src.backend.models.inquiry import Inquiry
from src.backend.schemas.inquiry import (
    InquiryConvertRequest,
    InquiryCreate,
)
from src.backend.services.reference_id_service import generate_reference_id

logger = structlog.get_logger(__name__)


class InquiryConversionError(Exception):
    def __init__(self, status_code: int, body: dict[str, Any]):
        self.status_code = status_code
        self.body = body
        super().__init__(body.get("detail", "Inquiry conversion error"))


def convert_inquiry(
    db: Session,
    inquiry_id: uuid.UUID,
    body: InquiryConvertRequest,
    actor_id: uuid.UUID,
) -> dict[str, Any]:
    """Convert an inquiry into a client + project — the core SWA workflow.

    All DML runs in one transaction (roll back on any failure).
    The inquiry row is locked with SELECT FOR UPDATE so concurrent
    conversions cannot race, and a double-conversion guard rejects
    attempts on already-converted inquiries.
    """
    from src.backend.db.repositories.client_repo import create as _create_client
    from src.backend.db.repositories.project_repo import create_project as _create_project

    # Lock the inquiry row so concurrent conversions cannot race.
    inquiry = (
        db.query(Inquiry)
        .filter(Inquiry.id == inquiry_id, Inquiry.deleted_at.is_(None))
        .with_for_update()
        .first()
    )
    if not inquiry:
        raise InquiryConversionError(404, {"detail": "Inquiry not found"})

    if inquiry.status == "Converted":
        raise InquiryConversionError(409, {"detail": "Inquiry already converted"})

    if inquiry.status not in ("New", "In Progress", "Quoted", "Awarded"):
        raise InquiryConversionError(
            400,
            {
                "detail": f"Inquiry status '{inquiry.status}' cannot be converted. "
                f"Allowed: New, In Progress, Quoted, Awarded"
            },
        )

    try:
        # Resolve client: prefer explicit client_id, else match by name
        client: Client | None = None
        client_source: str | None = None
        if body.client_id:
            client = get_client_by_id(db, body.client_id)
            client_source = "explicit_id"
        if client is None:
            existing = (
                db.query(Client)
                .filter(
                    Client.name.ilike(body.project_name or inquiry.client_name),
                    Client.deleted_at.is_(None),
                )
                .first()
            )
            if existing:
                client = existing
                client_source = "name_match"

        if client is None:
            client = _create_client(
                db,
                name=body.project_name or inquiry.client_name,
                code=body.project_code or f"SWA-CLT-{inquiry.reference_id.split('-')[-1]}",
                primary_email=body.client_primary_email or "import@swa.internal",
                country=body.client_country or "India",
                primary_phone=body.client_primary_phone,
                client_status="Active",
            )
            client_source = "new"

        logger.info(
            "inquiry.convert.client_resolved",
            inquiry_id=str(inquiry_id),
            client_id=str(client.id),
            client_source=client_source,
        )

        # Create project under the client
        project_payload = {
            "client_id": client.id,
            "code": body.project_code or f"SWA-PRJ-{inquiry.reference_id.split('-')[-1]}",
            "name": body.project_name or f"{client.name} — {inquiry.reference_id}",
            "status": body.project_status or "Lead",
            "inquiry_id": inquiry.id,
            "notes": body.project_description,
        }
        project = _create_project(db, project_payload)
        logger.info(
            "inquiry.convert.project_created",
            inquiry_id=str(inquiry_id),
            project_id=str(project.id),
            project_code=project.code,
        )

        # Update inquiry status
        update_inquiry(
            db,
            inquiry,
            {
                "status": "Converted",
                "converted_project_id": project.id,
                "converted_client_id": client.id,
            },
        )

        audit_repo.create_entry(
            db,
            action="inquiry.convert",
            entity_type="inquiry",
            entity_id=inquiry.id,
            user_id=actor_id,
            before_json={"status": inquiry.status},
            after_json={
                "status": "Converted",
                "client_id": str(client.id),
                "project_id": str(project.id),
            },
        )

        logger.info(
            "inquiry.converted",
            inquiry_id=str(inquiry_id),
            client_id=str(client.id),
            project_id=str(project.id),
            actor_id=str(actor_id),
        )

        return {
            "inquiry": inquiry,
            "client": client,
            "project": project,
        }
    except Exception:
        db.rollback()
        raise


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
    data: dict[str, Any],
    actor_id: uuid.UUID,
) -> Inquiry | None:
    inquiry = get_inquiry_by_id(db, inquiry_id)
    if not inquiry:
        return None
    update_inquiry(db, inquiry, data)
    return inquiry


def soft_delete_inquiry_service(
    db: Session,
    inquiry_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> bool:
    inquiry = get_inquiry_by_id(db, inquiry_id)
    if not inquiry:
        return False
    inquiry.deleted_at = datetime.now(tz=UTC)
    audit_repo.create_entry(
        db,
        action="inquiry.delete",
        entity_type="inquiry",
        entity_id=inquiry.id,
        user_id=actor_id,
        before_json={"status": inquiry.status},
    )
    return True
