import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy.orm import Session

from src.backend.db.repositories import audit_repo
from src.backend.db.repositories.client_repo import (
    create as create_client,
)
from src.backend.db.repositories.client_repo import (
    get_by_id as get_client_by_id,
)
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
from src.backend.db.repositories.project_repo import create_project
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
    locked = (
        db.query(Inquiry)
        .filter(Inquiry.id == inquiry_id, Inquiry.deleted_at.is_(None))
        .with_for_update()
        .first()
    )
    if not locked:
        raise InquiryConversionError(404, {"detail": "Inquiry not found"})

    if locked.status == "Converted":
        raise InquiryConversionError(409, {"detail": "Inquiry already converted"})

    if locked.status not in ("New", "Contacted", "In Progress", "Quoted", "Awarded"):
        raise InquiryConversionError(
            400,
            {
                "detail": f"Inquiry status '{locked.status}' cannot be converted. "
                "Allowed: New, Contacted, In Progress, Quoted, Awarded"
            },
        )

    # Resolve client: prefer explicit client_id, else match by inquiry.client_name
    client: Client | None = None
    client_source: str | None = None
    if body.client_id:
        client = get_client_by_id(db, body.client_id)
        client_source = "explicit_id"

    if client is None:
        # Search for existing clients by the inquiry's client_name (not the project name)
        candidates = (
            db.query(Client)
            .filter(Client.name.ilike(locked.client_name), Client.deleted_at.is_(None))
            .all()
        )
        if len(candidates) == 1:
            client = candidates[0]
            client_source = "name_match"
        elif len(candidates) > 1:
            raise InquiryConversionError(
                300,
                {
                    "detail": "Ambiguous client match",
                    "inquiry_client_name": locked.client_name,
                    "candidates": [
                        {"id": str(c.id), "name": c.name, "code": c.code} for c in candidates
                    ],
                },
            )

    if client is None:
        client = create_client(
            db,
            name=locked.client_name,
            code=generate_reference_id(db, "CLT"),
            primary_email=body.client_primary_email or "import@swa.internal",
            country=body.client_country or "India",
            primary_phone=body.client_primary_phone,
            client_status="Active",
            industry=body.client_industry,
            first_inquiry_id=locked.id,
        )
        client_source = "new"

    logger.info(
        "inquiry.convert.client_resolved",
        inquiry_id=str(inquiry_id),
        client_id=str(client.id),
        client_source=client_source,
    )

    # Create project under the client
    project = create_project(
        db,
        {
            "client_id": client.id,
            "code": generate_reference_id(db, "PRJ"),
            "name": body.project_name or f"{client.name} — {locked.reference_id}",
            "status": body.project_status or "Awarded",
            "inquiry_id": locked.id,
            "notes": body.project_description,
            "estimated_value": locked.estimated_value,
        },
    )
    logger.info(
        "inquiry.convert.project_created",
        inquiry_id=str(inquiry_id),
        project_id=str(project.id),
        project_code=project.code,
    )

    # Update inquiry status (capture pre-convert status first — update mutates `locked`)
    before_status = locked.status
    update_inquiry(
        db,
        locked,
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
        entity_id=locked.id,
        user_id=actor_id,
        before_json={"status": before_status},
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
        "inquiry": locked,
        "client": client,
        "project": project,
    }


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
    data: dict[str, Any] | object,
    actor_id: uuid.UUID,
) -> Inquiry | None:
    inquiry = get_inquiry_by_id(db, inquiry_id)
    if not inquiry:
        return None
    if hasattr(data, "model_dump"):
        data = data.model_dump()  # type: ignore[assignment]
    update_inquiry(db, inquiry, data)  # type: ignore[arg-type]
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
