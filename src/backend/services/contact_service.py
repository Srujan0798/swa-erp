import uuid

from sqlalchemy.orm import Session

from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.contact_repo import (
    create as create_contact,
)
from src.backend.db.repositories.contact_repo import (
    delete as delete_contact,
)
from src.backend.db.repositories.contact_repo import (
    get_by_id as get_contact_by_id,
)
from src.backend.db.repositories.contact_repo import (
    list_by_client,
)
from src.backend.db.repositories.contact_repo import (
    update as update_contact,
)
from src.backend.models.contact import Contact
from src.backend.schemas.contact import ContactCreate, ContactUpdate


def list_contacts_service(db: Session, client_id: uuid.UUID) -> list[Contact]:
    return list_by_client(db, client_id)


def create_contact_service(
    db: Session,
    client_id: uuid.UUID,
    data: ContactCreate,
    actor_id: uuid.UUID | None,
) -> Contact:
    contact = create_contact(
        db,
        client_id=client_id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        designation=data.designation,
        is_primary=data.is_primary,
    )

    create_entry(
        db,
        action="contact.create",
        entity_type="contact",
        entity_id=contact.id,
        user_id=actor_id,
        after_json={
            "id": str(contact.id),
            "client_id": str(contact.client_id),
            "name": contact.name,
            "email": contact.email,
        },
    )

    return contact


def update_contact_service(
    db: Session,
    contact_id: uuid.UUID,
    data: ContactUpdate,
    actor_id: uuid.UUID | None,
) -> Contact | None:
    contact = get_contact_by_id(db, contact_id)
    if not contact:
        return None

    before_json = {
        "name": contact.name,
        "email": contact.email,
    }

    if data.name is not None:
        contact.name = data.name
    if data.email is not None:
        contact.email = data.email
    if data.phone is not None:
        contact.phone = data.phone
    if data.designation is not None:
        contact.designation = data.designation
    if data.is_primary is not None:
        contact.is_primary = data.is_primary

    update_contact(db, contact)

    after_json = {
        "name": contact.name,
        "email": contact.email,
    }

    create_entry(
        db,
        action="contact.update",
        entity_type="contact",
        entity_id=contact.id,
        user_id=actor_id,
        before_json=before_json,
        after_json=after_json,
    )

    return contact


def delete_contact_service(
    db: Session,
    contact_id: uuid.UUID,
    actor_id: uuid.UUID | None,
) -> bool:
    contact = get_contact_by_id(db, contact_id)
    if not contact:
        return False

    create_entry(
        db,
        action="contact.delete",
        entity_type="contact",
        entity_id=contact.id,
        user_id=actor_id,
        before_json={
            "name": contact.name,
            "email": contact.email,
        },
        after_json=None,
    )

    delete_contact(db, contact)
    return True
