import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.user import (
    UserAssigneeListResponse,
    UserAssigneeRead,
    UserCreate,
    UserListResponse,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=UserListResponse)
def list_users(
    _: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
) -> UserListResponse:
    from src.backend.services.user_service import list_users_service

    items, total, page, page_size = list_users_service(
        db, page=page, page_size=page_size, q=q, role=role, is_active=is_active
    )
    return UserListResponse(
        items=[UserRead.model_validate(u) for u in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/assignees", response_model=UserAssigneeListResponse)
def list_assignees(
    _: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    q: str | None = None,
    role: str | None = None,
    page_size: int = Query(default=100, ge=1, le=200),
) -> UserAssigneeListResponse:
    """Active, non-deleted users for task/project assignee pickers (all auth roles)."""
    from src.backend.services.user_service import list_users_service

    items, _total, _page, _ps = list_users_service(
        db, page=1, page_size=page_size, q=q, role=role, is_active=True
    )
    # Attribution-only import identity must never appear in pickers
    items = [u for u in items if u.email != "import@swa.local"]
    return UserAssigneeListResponse(
        items=[UserAssigneeRead.model_validate(u) for u in items],
        total=len(items),
    )


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> UserRead:
    from sqlalchemy.exc import IntegrityError

    from src.backend.services.user_service import create_user_service

    try:
        user = create_user_service(db, body, current_user.id)
        return UserRead.model_validate(user)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists") from e


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> UserRead:
    from src.backend.services.user_service import get_user_service

    if current_user.role != Role.ADMIN.value and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = get_user_service(db, user_id)
    if not user or user.deleted_at:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> UserRead:
    from src.backend.services.user_service import update_user_service

    is_self = current_user.id == user_id

    if is_self and (body.role is not None or body.is_active is not None):
        raise HTTPException(status_code=403, detail="Cannot modify own role or active status")

    if current_user.role != Role.ADMIN.value and not is_self:
        raise HTTPException(status_code=403, detail="Not authorized")

    result = update_user_service(db, user_id, body, current_user.id, is_self=is_self)
    if not result:
        raise HTTPException(status_code=403, detail="Cannot modify own role or active status")
    return UserRead.model_validate(result)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    from src.backend.services.user_service import soft_delete_user_service

    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="Cannot delete self")

    success = soft_delete_user_service(db, user_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
