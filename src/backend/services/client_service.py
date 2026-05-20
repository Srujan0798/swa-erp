import uuid

from sqlalchemy.orm import Session

from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.client_repo import (
    create as create_client,
)
from src.backend.db.repositories.client_repo import (
    get_by_id as get_client_by_id,
)
from src.backend.db.repositories.client_repo import (
    list_clients,
)
from src.backend.db.repositories.client_repo import (
    soft_delete as soft_delete_client,
)
from src.backend.db.repositories.client_repo import (
    update as update_client,
)
from src.backend.models.client import Client
from src.backend.schemas.client import ClientCreate, ClientUpdate


def list_clients_service(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
) -> tuple[list[Client], int, int, int]:
    items, total = list_clients(db, page, page_size, q)
    return items, total, page, page_size


def create_client_service(
    db: Session,
    data: ClientCreate,
    actor_id: uuid.UUID | None,
) -> Client:
    client = create_client(
        db,
        name=data.name,
        code=data.code,
        primary_email=data.primary_email,
        address=data.address,
        city=data.city,
        state=data.state,
        pincode=data.pincode,
        country=data.country,
        gst_number=data.gst_number,
        primary_phone=data.primary_phone,
        notes=data.notes,
    )

    create_entry(
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
        },
    )

    return client


def get_client_service(db: Session, client_id: uuid.UUID) -> Client | None:
    return get_client_by_id(db, client_id)


def update_client_service(
    db: Session,
    client_id: uuid.UUID,
    data: ClientUpdate,
    actor_id: uuid.UUID | None,
) -> Client | None:
    client = get_client_by_id(db, client_id)
    if not client:
        return None

    before_json = {
        "name": client.name,
        "code": client.code,
        "primary_email": client.primary_email,
    }

    if data.name is not None:
        client.name = data.name
    if data.code is not None:
        client.code = data.code
    if data.address is not None:
        client.address = data.address
    if data.city is not None:
        client.city = data.city
    if data.state is not None:
        client.state = data.state
    if data.pincode is not None:
        client.pincode = data.pincode
    if data.country is not None:
        client.country = data.country
    if data.gst_number is not None:
        client.gst_number = data.gst_number
    if data.primary_email is not None:
        client.primary_email = data.primary_email
    if data.primary_phone is not None:
        client.primary_phone = data.primary_phone
    if data.notes is not None:
        client.notes = data.notes
    if data.is_active is not None:
        client.is_active = data.is_active

    update_client(db, client)

    after_json = {
        "name": client.name,
        "code": client.code,
        "primary_email": client.primary_email,
    }

    create_entry(
        db,
        action="client.update",
        entity_type="client",
        entity_id=client.id,
        user_id=actor_id,
        before_json=before_json,
        after_json=after_json,
    )

    return client


def soft_delete_client_service(
    db: Session,
    client_id: uuid.UUID,
    actor_id: uuid.UUID | None,
) -> bool:
    client = get_client_by_id(db, client_id)
    if not client:
        return False

    before_json = {"deleted_at": None}

    soft_delete_client(db, client)

    after_json = {"deleted_at": str(client.deleted_at)}

    create_entry(
        db,
        action="client.delete",
        entity_type="client",
        entity_id=client.id,
        user_id=actor_id,
        before_json=before_json,
        after_json=after_json,
    )

    return True
