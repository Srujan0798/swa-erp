import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.repositories.contact_repo import get_by_id as get_contact_by_id
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.client import ClientCreate, ClientListResponse, ClientRead, ClientUpdate
from src.backend.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from src.backend.services.client_service import (
    create_client_service,
    get_client_service,
    list_clients_service,
    soft_delete_client_service,
    update_client_service,
)
from src.backend.services.contact_service import (
    create_contact_service,
    delete_contact_service,
    update_contact_service,
)

router = APIRouter(prefix="/api/clients", tags=["clients"])


def _require_pm_or_admin(user: User) -> None:
    if user.role not in (Role.ADMIN.value, Role.PM.value):
        raise HTTPException(status_code=403, detail="Not authorized")


@router.get("", response_model=ClientListResponse)
def list_clients(
    _: User = Depends(require_role(Role.VIEWER)),  # noqa: B008  # all roles can list
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = None,
) -> ClientListResponse:
    items, total, page, page_size = list_clients_service(db, page=page, page_size=page_size, q=q)
    return ClientListResponse(
        items=[ClientRead.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    body: ClientCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008  # admin+pm
    db: Session = Depends(get_db),  # noqa: B008
) -> ClientRead:
    from sqlalchemy.exc import IntegrityError

    try:
        client = create_client_service(db, body, current_user.id)
        return ClientRead.model_validate(client)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Client code already exists") from e


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ClientRead:
    client = get_client_service(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientRead.model_validate(client)


@router.patch("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: uuid.UUID,
    body: ClientUpdate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ClientRead:
    client = update_client_service(db, client_id, body, current_user.id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientRead.model_validate(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = soft_delete_client_service(db, client_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")


@router.post(
    "/{client_id}/contacts", response_model=ContactRead, status_code=status.HTTP_201_CREATED
)
def add_contact(
    client_id: uuid.UUID,
    body: ContactCreate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ContactRead:
    client = get_client_service(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    contact = create_contact_service(db, client_id, body, current_user.id)
    return ContactRead.model_validate(contact)


@router.patch("/{client_id}/contacts/{contact_id}", response_model=ContactRead)
def update_contact(
    client_id: uuid.UUID,
    contact_id: uuid.UUID,
    body: ContactUpdate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ContactRead:
    contact = get_contact_by_id(db, contact_id)
    if not contact or contact.client_id != client_id:
        raise HTTPException(status_code=404, detail="Contact not found")

    result = update_contact_service(db, contact_id, body, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ContactRead.model_validate(result)


@router.delete("/{client_id}/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    client_id: uuid.UUID,
    contact_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    contact = get_contact_by_id(db, contact_id)
    if not contact or contact.client_id != client_id:
        raise HTTPException(status_code=404, detail="Contact not found")

    success = delete_contact_service(db, contact_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
