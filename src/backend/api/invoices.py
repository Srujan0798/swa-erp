import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.invoice import (
    InvoiceCreate,
    InvoiceGenerateFromTime,
    InvoiceListResponse,
    InvoiceRead,
    InvoiceUpdateStatus,
)
from src.backend.services.invoice_service import (
    create_invoice_service,
    delete_invoice_service,
    generate_from_time_entries,
    get_invoice_service,
    list_invoices_service,
    update_invoice_status_service,
)

router = APIRouter(prefix="/api", tags=["invoices"])


@router.post(
    "/projects/{project_id}/invoices",
    response_model=InvoiceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_endpoint(
    project_id: uuid.UUID,
    body: InvoiceCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> InvoiceRead:
    try:
        items_data = [item.model_dump() for item in body.items]
        result = create_invoice_service(
            db,
            project_id=project_id,
            user_id=current_user.id,
            due_date=body.due_date,
            notes=body.notes,
            tax_rate=body.tax_rate,
            items_data=items_data,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return InvoiceRead.model_validate(result)


@router.post(
    "/projects/{project_id}/invoices/generate-from-time",
    response_model=InvoiceRead,
    status_code=status.HTTP_201_CREATED,
)
def generate_from_time_endpoint(
    project_id: uuid.UUID,
    body: InvoiceGenerateFromTime,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> InvoiceRead:
    try:
        result = generate_from_time_entries(
            db,
            project_id=project_id,
            user_id=current_user.id,
            start_date=body.start_date,
            end_date=body.end_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return InvoiceRead.model_validate(result)


@router.get(
    "/projects/{project_id}/invoices",
    response_model=InvoiceListResponse,
)
def list_invoices_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(
        require_role(Role.PM)
    ),  # noqa: B008  # Meeting: finance not VIEWER
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    invoice_status: str | None = Query(default=None, alias="status"),
) -> InvoiceListResponse:
    items, total, pg, ps = list_invoices_service(
        db, project_id, status=invoice_status, page=page, page_size=page_size
    )
    return InvoiceListResponse(
        items=[InvoiceRead.model_validate(i) for i in items],
        total=total,
        page=pg,
        page_size=ps,
    )


@router.get("/invoices/{invoice_id}", response_model=InvoiceRead)
def get_invoice_endpoint(
    invoice_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> InvoiceRead:
    result = get_invoice_service(db, invoice_id)
    if not result:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceRead.model_validate(result)


@router.patch("/invoices/{invoice_id}/status", response_model=InvoiceRead)
def update_invoice_status_endpoint(
    invoice_id: uuid.UUID,
    body: InvoiceUpdateStatus,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> InvoiceRead:
    try:
        result = update_invoice_status_service(db, invoice_id, body.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return InvoiceRead.model_validate(result)


@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice_endpoint(
    invoice_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    try:
        success = delete_invoice_service(db, invoice_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found")
