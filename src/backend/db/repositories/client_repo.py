import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from src.backend.models.client import Client


def list_clients(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
) -> tuple[list[Client], int]:
    query = db.query(Client).filter(Client.deleted_at.is_(None))

    if q:
        search = f"%{q}%"
        query = query.filter(
            Client.name.ilike(search) | Client.code.ilike(search) | Client.primary_email.ilike(search)
        )

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Client.created_at.desc()).offset(offset).limit(page_size).all()

    return list(items), total


def get_by_id(db: Session, client_id: uuid.UUID) -> Client | None:
    return db.query(Client).filter(Client.id == client_id, Client.deleted_at.is_(None)).first()


def create(
    db: Session,
    name: str,
    code: str,
    primary_email: str,
    address: str | None = None,
    city: str | None = None,
    state: str | None = None,
    pincode: str | None = None,
    country: str = "India",
    gst_number: str | None = None,
    primary_phone: str | None = None,
    notes: str | None = None,
) -> Client:
    client = Client(
        name=name,
        code=code,
        primary_email=primary_email,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        country=country,
        gst_number=gst_number,
        primary_phone=primary_phone,
        notes=notes,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def update(db: Session, client: Client) -> Client:
    db.commit()
    db.refresh(client)
    return client


def soft_delete(db: Session, client: Client) -> Client:
    client.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(client)
    return client
