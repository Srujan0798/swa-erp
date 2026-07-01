import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.repositories.project_repo import get_by_id as get_project_by_id
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.rfq import (
    RFQCompareMaterial,
    RFQCreate,
    RFQListResponse,
    RFQRead,
    RFQResponseItem,
)
from src.backend.services.rfq_service import (
    award_rfq,
    cancel_rfq,
    close_rfq,
    compare_rfq,
    create_rfq_with_items,
    get_rfq,
    list_project_rfqs,
    receive_response,
    send_rfq,
)

router = APIRouter(tags=["rfqs"])


@router.post(
    "/api/projects/{project_id}/rfqs",
    response_model=RFQRead,
    status_code=status.HTTP_201_CREATED,
)
def create_rfq_endpoint(
    project_id: uuid.UUID,
    body: RFQCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        items_data = [
            {"material_id": i.material_id, "quantity": i.quantity, "notes": i.notes}
            for i in body.items
        ]
        return create_rfq_with_items(
            db,
            project_id=project_id,
            vendor_id=body.vendor_id,
            notes=body.notes,
            items_data=items_data,
            created_by=current_user.id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/api/projects/{project_id}/rfqs",
    response_model=RFQListResponse,
)
def list_rfqs_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    rfq_status: str | None = Query(default=None, alias="status"),
) -> RFQListResponse:
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return list_project_rfqs(
        db, project_id, page=page, page_size=page_size, status=rfq_status
    )


@router.get(
    "/api/rfqs/{rfq_id}",
    response_model=RFQRead,
)
def get_rfq_endpoint(
    rfq_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    result = get_rfq(db, rfq_id)
    if not result:
        raise HTTPException(status_code=404, detail="RFQ not found")
    return result


@router.post(
    "/api/rfqs/{rfq_id}/send",
    response_model=RFQRead,
)
def send_rfq_endpoint(
    rfq_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    try:
        return send_rfq(db, rfq_id, sent_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/api/rfqs/{rfq_id}/respond",
    response_model=RFQRead,
)
def respond_rfq_endpoint(
    rfq_id: uuid.UUID,
    body: list[RFQResponseItem],
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    try:
        items_data = [
            {"item_id": i.item_id, "vendor_rate": i.vendor_rate} for i in body
        ]
        return receive_response(db, rfq_id, items_data, responded_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/api/rfqs/{rfq_id}/award",
    response_model=RFQRead,
)
def award_rfq_endpoint(
    rfq_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    try:
        return award_rfq(db, rfq_id, awarded_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/api/rfqs/{rfq_id}/close",
    response_model=RFQRead,
)
def close_rfq_endpoint(
    rfq_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    try:
        return close_rfq(db, rfq_id, closed_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/api/rfqs/{rfq_id}/cancel",
    response_model=RFQRead,
)
def cancel_rfq_endpoint(
    rfq_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    try:
        return cancel_rfq(db, rfq_id, cancelled_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/api/projects/{project_id}/rfqs/compare",
    response_model=list[RFQCompareMaterial],
)
def compare_rfqs_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    material_ids: str | None = Query(default=None),
) -> list[RFQCompareMaterial]:
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    mat_ids = None
    if material_ids:
        try:
            mat_ids = [uuid.UUID(m.strip()) for m in material_ids.split(",")]
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail="Invalid material_ids format"
            ) from e
    return compare_rfq(db, project_id, mat_ids)
