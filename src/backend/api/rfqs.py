import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role, role_includes
from src.backend.db.repositories.project_repo import user_has_project_access
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
    mark_compared,
    receive_response,
    send_rfq,
)

router = APIRouter(tags=["rfqs"])


def _require_project_access(
    db: Session, project_id: uuid.UUID, user: User, *, read_only: bool = False
) -> None:
    """Raise 403 when user is not a member of project_id. Admins bypass. Viewers allowed for read_only."""
    if role_includes(Role(user.role), Role.ADMIN):
        return
    if role_includes(Role(user.role), Role.VIEWER) and read_only:
        return
    if not user_has_project_access(db, user.id, project_id):
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this project",
        )


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
    _require_project_access(db, project_id, current_user)
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
    _require_project_access(db, project_id, current_user, read_only=True)
    return list_project_rfqs(db, project_id, page=page, page_size=page_size, status=rfq_status)


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
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    try:
        result = send_rfq(db, rfq_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return result


@router.post(
    "/api/rfqs/{rfq_id}/receive",
    response_model=RFQRead,
)
def receive_response_endpoint(
    rfq_id: uuid.UUID,
    body: list[RFQResponseItem],
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    result = receive_response(db, rfq_id, [item.model_dump() for item in body], current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="RFQ not found or cannot receive response")
    return result


@router.post(
    "/api/rfqs/{rfq_id}/respond",
    response_model=RFQRead,
    include_in_schema=True,
)
def respond_rfq_endpoint(
    rfq_id: uuid.UUID,
    body: list[RFQResponseItem],
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    """Alias of /receive — the frontend and RBAC contract call it /respond."""
    return receive_response_endpoint(rfq_id, body, current_user, db)


@router.post(
    "/api/rfqs/{rfq_id}/compare",
    response_model=list[RFQCompareMaterial],
)
def compare_rfqs_endpoint(
    rfq_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    material_ids: str | None = Query(default=None),
) -> list[RFQCompareMaterial]:
    rfq = get_rfq(db, rfq_id)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    _require_project_access(db, rfq.project_id, current_user, read_only=True)
    mat_ids = None
    if material_ids:
        try:
            mat_ids = [uuid.UUID(m.strip()) for m in material_ids.split(",")]
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid material_ids format") from e
    return compare_rfq(db, rfq.project_id, mat_ids)


@router.get(
    "/api/projects/{project_id}/rfqs/compare",
    response_model=list[RFQCompareMaterial],
)
def compare_project_rfqs_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    material_ids: str | None = Query(default=None),
) -> list[RFQCompareMaterial]:
    _require_project_access(db, project_id, current_user, read_only=True)
    mat_ids = None
    if material_ids:
        try:
            mat_ids = [uuid.UUID(m.strip()) for m in material_ids.split(",")]
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid material_ids format") from e
    return compare_rfq(db, project_id, mat_ids)


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
        result = award_rfq(db, rfq_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not result:
        raise HTTPException(status_code=404, detail="RFQ not found")
    return result


@router.post(
    "/api/rfqs/{rfq_id}/close",
    response_model=RFQRead,
)
def close_rfq_endpoint(
    rfq_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    try:
        result = close_rfq(db, rfq_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not result:
        raise HTTPException(status_code=404, detail="RFQ not found")
    return result


@router.post(
    "/api/rfqs/{rfq_id}/cancel",
    response_model=RFQRead,
)
def cancel_rfq_endpoint(
    rfq_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    try:
        result = cancel_rfq(db, rfq_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not result:
        raise HTTPException(status_code=404, detail="RFQ not found")
    return result


@router.post(
    "/api/rfqs/{rfq_id}/mark-compared",
    response_model=RFQRead,
)
def mark_compared_endpoint(
    rfq_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> RFQRead:
    result = mark_compared(db, rfq_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="RFQ not found")
    return result
