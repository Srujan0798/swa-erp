import uuid

from sqlalchemy.orm import Session

from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.vendor_repo import (
    create_contact as repo_create_contact,
)
from src.backend.db.repositories.vendor_repo import (
    create_vendor,
    get_by_code,
    get_by_id,
    get_contact_by_id,
    list_contacts,
    list_vendors,
    soft_delete,
    update_vendor,
)
from src.backend.db.repositories.vendor_repo import (
    delete_contact as repo_delete_contact,
)
from src.backend.db.repositories.vendor_repo import (
    update_contact as repo_update_contact,
)
from src.backend.models.vendor import Vendor, VendorContact
from src.backend.schemas.vendor import (
    VendorContactCreate,
    VendorContactUpdate,
    VendorCreate,
    VendorUpdate,
)


def create_vendor_service(
    db: Session,
    data: VendorCreate,
    actor_id: uuid.UUID | None,
) -> Vendor:
    vendor = create_vendor(
        db,
        name=data.name,
        code=data.code,
        email=data.email,
        phone=data.phone,
        address=data.address,
        city=data.city,
        state=data.state,
        gst_number=data.gst_number,
        pan_number=data.pan_number,
    )

    for c in data.contacts:
        repo_create_contact(
            db,
            vendor_id=vendor.id,
            name=c.name,
            designation=c.designation,
            email=c.email,
            phone=c.phone,
            is_primary=c.is_primary,
        )

    create_entry(
        db,
        action="vendor.create",
        entity_type="vendor",
        entity_id=vendor.id,
        user_id=actor_id,
        after_json={
            "id": str(vendor.id),
            "name": vendor.name,
            "code": vendor.code,
        },
    )

    return vendor


def get_vendor_service(db: Session, vendor_id: uuid.UUID) -> Vendor | None:
    return get_by_id(db, vendor_id)


def get_vendor_by_code(db: Session, code: str) -> Vendor | None:
    return get_by_code(db, code)


def list_vendors_service(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[Vendor], int, int, int]:
    items, total = list_vendors(db, page, page_size, search, is_active)
    return items, total, page, page_size


def update_vendor_service(
    db: Session,
    vendor_id: uuid.UUID,
    data: VendorUpdate,
    actor_id: uuid.UUID | None,
) -> Vendor | None:
    vendor = get_by_id(db, vendor_id)
    if not vendor:
        return None

    before_json = {"name": vendor.name, "code": vendor.code}

    if data.name is not None:
        vendor.name = data.name
    if data.code is not None:
        vendor.code = data.code
    if data.email is not None:
        vendor.email = data.email
    if data.phone is not None:
        vendor.phone = data.phone
    if data.address is not None:
        vendor.address = data.address
    if data.city is not None:
        vendor.city = data.city
    if data.state is not None:
        vendor.state = data.state
    if data.gst_number is not None:
        vendor.gst_number = data.gst_number
    if data.pan_number is not None:
        vendor.pan_number = data.pan_number
    if data.is_active is not None:
        vendor.is_active = data.is_active

    update_vendor(db, vendor)

    after_json = {"name": vendor.name, "code": vendor.code}

    create_entry(
        db,
        action="vendor.update",
        entity_type="vendor",
        entity_id=vendor.id,
        user_id=actor_id,
        before_json=before_json,
        after_json=after_json,
    )

    return vendor


def delete_vendor_service(
    db: Session,
    vendor_id: uuid.UUID,
    actor_id: uuid.UUID | None,
) -> bool:
    vendor = get_by_id(db, vendor_id)
    if not vendor:
        return False

    before_json = {"deleted_at": None}

    soft_delete(db, vendor)

    after_json = {"deleted_at": str(vendor.deleted_at)}

    create_entry(
        db,
        action="vendor.delete",
        entity_type="vendor",
        entity_id=vendor.id,
        user_id=actor_id,
        before_json=before_json,
        after_json=after_json,
    )

    return True


def add_contact_service(
    db: Session,
    vendor_id: uuid.UUID,
    data: VendorContactCreate,
    actor_id: uuid.UUID | None,
) -> VendorContact:
    contact = repo_create_contact(
        db,
        vendor_id=vendor_id,
        name=data.name,
        designation=data.designation,
        email=data.email,
        phone=data.phone,
        is_primary=data.is_primary,
    )

    create_entry(
        db,
        action="vendor_contact.create",
        entity_type="vendor_contact",
        entity_id=contact.id,
        user_id=actor_id,
        after_json={
            "id": str(contact.id),
            "vendor_id": str(contact.vendor_id),
            "name": contact.name,
        },
    )

    return contact


def list_contacts_service(db: Session, vendor_id: uuid.UUID) -> list[VendorContact]:
    return list_contacts(db, vendor_id)


def update_contact_service(
    db: Session,
    contact_id: uuid.UUID,
    data: VendorContactUpdate,
    actor_id: uuid.UUID | None,
) -> VendorContact | None:
    contact = get_contact_by_id(db, contact_id)
    if not contact:
        return None

    before_json = {"name": contact.name}

    if data.name is not None:
        contact.name = data.name
    if data.designation is not None:
        contact.designation = data.designation
    if data.email is not None:
        contact.email = data.email
    if data.phone is not None:
        contact.phone = data.phone
    if data.is_primary is not None:
        contact.is_primary = data.is_primary

    repo_update_contact(db, contact)

    after_json = {"name": contact.name}

    create_entry(
        db,
        action="vendor_contact.update",
        entity_type="vendor_contact",
        entity_id=contact.id,
        user_id=actor_id,
        before_json=before_json,
        after_json=after_json,
    )

    return contact


def remove_contact_service(
    db: Session,
    contact_id: uuid.UUID,
    actor_id: uuid.UUID | None,
) -> bool:
    contact = get_contact_by_id(db, contact_id)
    if not contact:
        return False

    create_entry(
        db,
        action="vendor_contact.delete",
        entity_type="vendor_contact",
        entity_id=contact.id,
        user_id=actor_id,
        before_json={"name": contact.name},
        after_json=None,
    )

    repo_delete_contact(db, contact)
    return True
