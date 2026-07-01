import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.quote import (
    QuoteCreate,
    QuoteListResponse,
    QuoteRead,
    QuoteRespondRequest,
    QuoteUpdate,
)
from src.backend.services.pdf_service import generate_quote_pdf
from src.backend.services.quote_service import (
    approve_quote,
    clone_to_draft,
    delete_quote_service,
    generate_quote,
    get_quote,
    list_quotes,
    respond_quote,
    send_quote,
    submit_quote,
    update_quote_service,
)

router = APIRouter(prefix="/api", tags=["quotes"])


def _quote_response(data: dict[str, Any]) -> QuoteRead:
    return QuoteRead.model_validate(data)


@router.post(
    "/projects/{project_id}/quotes",
    response_model=QuoteRead,
    status_code=status.HTTP_201_CREATED,
)
def create_quote_endpoint(
    project_id: uuid.UUID,
    body: QuoteCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> QuoteRead:
    try:
        data = generate_quote(
            db,
            project_id=project_id,
            boq_id=body.boq_id,
            markup_percent=body.markup_percent,
            tax_percent=body.tax_percent,
            terms=body.terms,
            validity_days=body.validity_days,
            created_by=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return _quote_response(data)


@router.get(
    "/projects/{project_id}/quotes",
    response_model=QuoteListResponse,
)
def list_quotes_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> QuoteListResponse:
    items, total, pg, ps = list_quotes(db, project_id, page=page, page_size=page_size)
    return QuoteListResponse(
        items=[_quote_response(i) for i in items],
        total=total,
        page=pg,
        page_size=ps,
    )


@router.get("/quotes/{quote_id}", response_model=QuoteRead)
def get_quote_endpoint(
    quote_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> QuoteRead:
    data = get_quote(db, quote_id)
    if not data:
        raise HTTPException(status_code=404, detail="Quote not found")
    return _quote_response(data)


@router.patch("/quotes/{quote_id}", response_model=QuoteRead)
def update_quote_endpoint(
    quote_id: uuid.UUID,
    body: QuoteUpdate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> QuoteRead:
    try:
        data = update_quote_service(
            db, quote_id, body.model_dump(exclude_unset=True), current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return _quote_response(data)


@router.delete("/quotes/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote_endpoint(
    quote_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = delete_quote_service(db, quote_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Quote not found")


@router.post("/quotes/{quote_id}/submit", response_model=QuoteRead)
def submit_quote_endpoint(
    quote_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> QuoteRead:
    try:
        data = submit_quote(db, quote_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return _quote_response(data)


@router.post("/quotes/{quote_id}/approve", response_model=QuoteRead)
def approve_quote_endpoint(
    quote_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> QuoteRead:
    try:
        data = approve_quote(db, quote_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return _quote_response(data)


@router.post("/quotes/{quote_id}/send", response_model=QuoteRead)
def send_quote_endpoint(
    quote_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> QuoteRead:
    try:
        data = send_quote(db, quote_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return _quote_response(data)


@router.post("/quotes/{quote_id}/respond", response_model=QuoteRead)
def respond_quote_endpoint(
    quote_id: uuid.UUID,
    body: QuoteRespondRequest,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> QuoteRead:
    try:
        data = respond_quote(db, quote_id, body.response, body.notes, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return _quote_response(data)


@router.post(
    "/quotes/{quote_id}/clone",
    response_model=QuoteRead,
    status_code=status.HTTP_201_CREATED,
)
def clone_quote_endpoint(
    quote_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> QuoteRead:
    try:
        data = clone_to_draft(db, quote_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return _quote_response(data)


@router.get("/quotes/{quote_id}/pdf")
def download_quote_pdf_endpoint(
    quote_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Response:
    data = get_quote(db, quote_id)
    if not data:
        raise HTTPException(status_code=404, detail="Quote not found")

    pdf_bytes = generate_quote_pdf(data)
    filename = f"quote-{quote_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
