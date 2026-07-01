import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.vendor import (
    VendorContactCreate,
    VendorContactRead,
    VendorContactUpdate,
    VendorCreate,
    VendorListResponse,
    VendorRead,
    VendorUpdate,
)
from src.backend.services.vendor_service import (
    add_contact_service,
    create_vendor_service,
    delete_vendor_service,
    get_vendor_service,
    list_contacts_service,
    list_vendors_service,
    remove_contact_service,
    update_contact_service,
    update_vendor_service,
)

router = APIRouter(prefix="/api/vendors", tags=["vendors"])


@router.get("", response_model=VendorListResponse)
def list_vendors(
    _: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = None,
    is_active: bool | None = None,
) -> VendorListResponse:
    items, total, page, page_size = list_vendors_service(
        db, page=page, page_size=page_size, search=search, is_active=is_active
    )
    return VendorListResponse(
        items=[VendorRead.model_validate(v) for v in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=VendorRead, status_code=status.HTTP_201_CREATED)
def create_vendor(
    body: VendorCreate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> VendorRead:
    try:
        vendor = create_vendor_service(db, body, current_user.id)
        return VendorRead.model_validate(vendor)
    except IntegrityError as e:
        db.rollback()
        if "vendors_code_key" in str(e) or "unique" in str(e).lower():
            raise HTTPException(status_code=409, detail="Vendor code already exists") from e
        raise HTTPException(status_code=409, detail="Vendor with duplicate GST/PAN") from e


@router.get("/{vendor_id}", response_model=VendorRead)
def get_vendor(
    vendor_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> VendorRead:
    vendor = get_vendor_service(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return VendorRead.model_validate(vendor)


@router.patch("/{vendor_id}", response_model=VendorRead)
def update_vendor(
    vendor_id: uuid.UUID,
    body: VendorUpdate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> VendorRead:
    try:
        vendor = update_vendor_service(db, vendor_id, body, current_user.id)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Vendor with duplicate code/GST/PAN") from e
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return VendorRead.model_validate(vendor)


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendor(
    vendor_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = delete_vendor_service(db, vendor_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Vendor not found")


@router.post("/{vendor_id}/contacts", response_model=VendorContactRead, status_code=status.HTTP_201_CREATED)
def add_contact(
    vendor_id: uuid.UUID,
    body: VendorContactCreate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> VendorContactRead:
    vendor = get_vendor_service(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    contact = add_contact_service(db, vendor_id, body, current_user.id)
    return VendorContactRead.model_validate(contact)


@router.get("/{vendor_id}/contacts", response_model=list[VendorContactRead])
def list_contacts(
    vendor_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> list[VendorContactRead]:
    vendor = get_vendor_service(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    contacts = list_contacts_service(db, vendor_id)
    return [VendorContactRead.model_validate(c) for c in contacts]


@router.patch("/{vendor_id}/contacts/{contact_id}", response_model=VendorContactRead)
def update_contact(
    vendor_id: uuid.UUID,
    contact_id: uuid.UUID,
    body: VendorContactUpdate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> VendorContactRead:
    contact = update_contact_service(db, contact_id, body, current_user.id)
    if not contact or contact.vendor_id != vendor_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return VendorContactRead.model_validate(contact)


@router.delete("/{vendor_id}/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    vendor_id: uuid.UUID,
    contact_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = remove_contact_service(db, contact_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
