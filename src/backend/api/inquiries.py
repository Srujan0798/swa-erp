import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.inquiry import (
    InquiryConvertRequest,
    InquiryCreate,
    InquiryListResponse,
    InquiryRead,
    InquiryUpdate,
)
from src.backend.services.inquiry_service import (
    InquiryConversionError,
    convert_inquiry,
    create_inquiry_service,
    get_inquiry_service,
    list_inquiries_service,
    soft_delete_inquiry_service,
    update_inquiry_service,
)

router = APIRouter(prefix="/api/inquiries", tags=["inquiries"])


@router.get("", response_model=InquiryListResponse)
def list_inquiries(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
) -> InquiryListResponse:
    items, total, page, page_size = list_inquiries_service(
        db, page=page, page_size=page_size, q=q, status=status_filter
    )
    return InquiryListResponse(
        items=[InquiryRead.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=InquiryRead, status_code=status.HTTP_201_CREATED)
def create_inquiry(
    body: InquiryCreate,
    current_user: User = Depends(require_role([Role.PM, Role.DESIGNER])),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> InquiryRead:
    inquiry = create_inquiry_service(db, body, current_user.id)
    return InquiryRead.model_validate(inquiry)


@router.get("/{inquiry_id}", response_model=InquiryRead)
def get_inquiry(
    inquiry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> InquiryRead:
    inquiry = get_inquiry_service(db, inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return InquiryRead.model_validate(inquiry)


@router.patch("/{inquiry_id}", response_model=InquiryRead)
def update_inquiry(
    inquiry_id: uuid.UUID,
    body: InquiryUpdate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> InquiryRead:
    inquiry = update_inquiry_service(db, inquiry_id, body, current_user.id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return InquiryRead.model_validate(inquiry)


@router.delete("/{inquiry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inquiry(
    inquiry_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = soft_delete_inquiry_service(db, inquiry_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Inquiry not found")


@router.post("/{inquiry_id}/convert")
def convert(
    inquiry_id: uuid.UUID,
    body: InquiryConvertRequest,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, Any]:
    try:
        result = convert_inquiry(db, inquiry_id, body, current_user.id)
    except InquiryConversionError as e:
        raise HTTPException(status_code=e.status_code, detail=e.body) from e
    return {
        "inquiry": InquiryRead.model_validate(result["inquiry"]),
        "client_id": str(result["client"].id),
        "project_id": str(result["project"].id),
    }
