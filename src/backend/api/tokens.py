import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.repositories.agreement_repo import get_by_id as get_agreement_by_id
from src.backend.db.session import get_db
from src.backend.models.token import Token
from src.backend.models.user import User
from src.backend.schemas.token import (
    TokenCreate,
    TokenListResponse,
    TokenRead,
    TokenUpdate,
)
from src.backend.services.token_service import (
    create_token_service,
    get_token_service,
    list_tokens_service,
    soft_delete_token_service,
    update_token_service,
)

router = APIRouter(prefix="/api/tokens", tags=["tokens"])


def _to_read(db: Session, token: Token) -> TokenRead:
    read = TokenRead.model_validate(token)
    agreement = get_agreement_by_id(db, token.agreement_id)
    if agreement is not None:
        read.agreement_reference_id = agreement.reference_id
    return read


@router.get("", response_model=TokenListResponse)
def list_tokens(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    agreement_id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = None,
) -> TokenListResponse:
    items, total, page, page_size = list_tokens_service(
        db,
        page=page,
        page_size=page_size,
        agreement_id=agreement_id,
        project_id=project_id,
        token_status=status_filter,
        q=q,
    )
    return TokenListResponse(
        items=[_to_read(db, t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=TokenRead, status_code=status.HTTP_201_CREATED)
def create_token(
    body: TokenCreate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TokenRead:
    token = create_token_service(db, body, current_user.id)
    return _to_read(db, token)


@router.get("/{token_id}", response_model=TokenRead)
def get_token(
    token_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TokenRead:
    token = get_token_service(db, token_id)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return _to_read(db, token)


@router.patch("/{token_id}", response_model=TokenRead)
def update_token(
    token_id: uuid.UUID,
    body: TokenUpdate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TokenRead:
    token = update_token_service(db, token_id, body, current_user.id)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return _to_read(db, token)


@router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_token(
    token_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = soft_delete_token_service(db, token_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Token not found")
