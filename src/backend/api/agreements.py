import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.agreement import (
    ServiceAgreementCreate,
    ServiceAgreementListResponse,
    ServiceAgreementRead,
    ServiceAgreementUpdate,
)
from src.backend.services.agreement_service import (
    create_agreement_service,
    get_agreement_service,
    list_agreements_service,
    soft_delete_agreement_service,
    update_agreement_service,
)

router = APIRouter(prefix="/api/service-agreements", tags=["service-agreements"])


@router.get("", response_model=ServiceAgreementListResponse)
def list_agreements(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    client_id: uuid.UUID | None = None,
    inquiry_id: uuid.UUID | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = None,
) -> ServiceAgreementListResponse:
    items, total, page, page_size = list_agreements_service(
        db,
        page=page,
        page_size=page_size,
        client_id=client_id,
        inquiry_id=inquiry_id,
        status=status_filter,
        q=q,
    )
    return ServiceAgreementListResponse(
        items=[ServiceAgreementRead.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ServiceAgreementRead, status_code=status.HTTP_201_CREATED)
def create_agreement(
    body: ServiceAgreementCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ServiceAgreementRead:
    agreement = create_agreement_service(db, body, current_user.id)
    return ServiceAgreementRead.model_validate(agreement)


@router.get("/{agreement_id}", response_model=ServiceAgreementRead)
def get_agreement(
    agreement_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ServiceAgreementRead:
    agreement = get_agreement_service(db, agreement_id)
    if not agreement:
        raise HTTPException(status_code=404, detail="Service agreement not found")
    return ServiceAgreementRead.model_validate(agreement)


@router.patch("/{agreement_id}", response_model=ServiceAgreementRead)
def update_agreement(
    agreement_id: uuid.UUID,
    body: ServiceAgreementUpdate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ServiceAgreementRead:
    try:
        agreement = update_agreement_service(db, agreement_id, body, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    if not agreement:
        raise HTTPException(status_code=404, detail="Service agreement not found")
    return ServiceAgreementRead.model_validate(agreement)


@router.delete("/{agreement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agreement(
    agreement_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = soft_delete_agreement_service(db, agreement_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Service agreement not found")
