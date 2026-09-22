import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.backend.models.contact import Contact


def list_by_client(db: Session, client_id: uuid.UUID) -> list[Contact]:
    return (
        db.query(Contact)
        .filter(Contact.client_id == client_id, Contact.deleted_at.is_(None))
        .order_by(Contact.is_primary.desc())
        .all()
    )


def create(
    db: Session,
    client_id: uuid.UUID,
    name: str,
    email: str,
    phone: str | None = None,
    designation: str | None = None,
    is_primary: bool = False,
) -> Contact:
    contact = Contact(
        client_id=client_id,
        name=name,
        email=email,
        phone=phone,
        designation=designation,
        is_primary=is_primary,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update(db: Session, contact: Contact) -> Contact:
    db.commit()
    db.refresh(contact)
    return contact


def delete(db: Session, contact: Contact) -> None:
    contact.deleted_at = datetime.now(UTC)
    db.commit()


def get_by_id(db: Session, contact_id: uuid.UUID) -> Contact | None:
    return db.query(Contact).filter(Contact.id == contact_id, Contact.deleted_at.is_(None)).first()
