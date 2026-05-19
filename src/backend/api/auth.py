from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    TokenResponse,
    UserPublic,
)
from src.backend.services.auth_service import login, logout, refresh_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_client_info(request: Request) -> tuple[str | None, str | None]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


@router.post("/login", response_model=TokenResponse)
def auth_login(
    request: Request,
    body: LoginRequest,
    db: Session = Depends(get_db),  # noqa: B008
) -> TokenResponse:
    ip_address, user_agent = get_client_info(request)
    result = login(db, body.email, body.password, ip_address, user_agent)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return result


@router.post("/refresh", response_model=AccessTokenResponse)
def auth_refresh(
    body: RefreshRequest,
    db: Session = Depends(get_db),  # noqa: B008
) -> AccessTokenResponse:
    result = refresh_access_token(db, body.refresh_token)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return result


@router.post("/logout", response_model=MessageResponse)
def auth_logout(
    request: Request,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> MessageResponse:
    ip_address, user_agent = get_client_info(request)
    success = logout(db, current_user.id, ip_address, user_agent)
    if not success:
        raise HTTPException(status_code=401, detail="Could not revoke session")
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserPublic)
def auth_me(
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> UserPublic:
    return UserPublic.model_validate(current_user)
