import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from src.backend.models.vendor import Vendor, VendorContact


def create_vendor(
    db: Session,
    name: str,
    code: str,
    email: str | None = None,
    phone: str | None = None,
    address: str | None = None,
    city: str | None = None,
    state: str | None = None,
    gst_number: str | None = None,
    pan_number: str | None = None,
) -> Vendor:
    vendor = Vendor(
        name=name,
        code=code,
        email=email,
        phone=phone,
        address=address,
        city=city,
        state=state,
        gst_number=gst_number,
        pan_number=pan_number,
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


def get_by_id(db: Session, vendor_id: uuid.UUID) -> Vendor | None:
    return (
        db.query(Vendor)
        .filter(Vendor.id == vendor_id, Vendor.deleted_at.is_(None))
        .first()
    )


def get_by_code(db: Session, code: str) -> Vendor | None:
    return db.query(Vendor).filter(Vendor.code == code).first()


def list_vendors(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[Vendor], int]:
    query = db.query(Vendor).filter(Vendor.deleted_at.is_(None))

    if search:
        s = f"%{search}%"
        query = query.filter(
            Vendor.name.ilike(s)
            | Vendor.code.ilike(s)
            | Vendor.city.ilike(s)
            | Vendor.gst_number.ilike(s)
        )

    if is_active is not None:
        query = query.filter(Vendor.is_active == is_active)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Vendor.created_at.desc()).offset(offset).limit(page_size).all()

    return list(items), total


def update_vendor(db: Session, vendor: Vendor) -> Vendor:
    db.commit()
    db.refresh(vendor)
    return vendor


def soft_delete(db: Session, vendor: Vendor) -> Vendor:
    vendor.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(vendor)
    return vendor


def create_contact(
    db: Session,
    vendor_id: uuid.UUID,
    name: str,
    designation: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    is_primary: bool = False,
) -> VendorContact:
    contact = VendorContact(
        vendor_id=vendor_id,
        name=name,
        designation=designation,
        email=email,
        phone=phone,
        is_primary=is_primary,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def list_contacts(db: Session, vendor_id: uuid.UUID) -> list[VendorContact]:
    return (
        db.query(VendorContact)
        .filter(VendorContact.vendor_id == vendor_id)
        .order_by(VendorContact.is_primary.desc())
        .all()
    )


def get_contact_by_id(db: Session, contact_id: uuid.UUID) -> VendorContact | None:
    return db.query(VendorContact).filter(VendorContact.id == contact_id).first()


def update_contact(db: Session, contact: VendorContact) -> VendorContact:
    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact: VendorContact) -> None:
    db.delete(contact)
    db.commit()
