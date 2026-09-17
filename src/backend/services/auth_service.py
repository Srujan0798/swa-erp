import uuid

from sqlalchemy.orm import Session

from src.backend.core.config import settings
from src.backend.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from src.backend.db.repositories.refresh_token_repo import create as create_refresh_token_record
from src.backend.db.repositories.refresh_token_repo import find_valid as find_valid_refresh_token
from src.backend.db.repositories.refresh_token_repo import revoke_all_for_user, revoke_single
from src.backend.db.repositories.user_repo import get_by_email
from src.backend.schemas.auth import AccessTokenResponse, TokenResponse, UserPublic
from src.backend.services.audit_service import record_event


def login(
    db: Session,
    email: str,
    password: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> TokenResponse | None:
    user = get_by_email(db, email)
    # is_active/deleted_at were enforced on refresh and in core.deps but not here,
    # so a disabled account could still mint a token pair at login.
    if (
        not user
        or not user.is_active
        or user.deleted_at
        or not verify_password(password, user.password_hash)
    ):
        from src.backend.core.metrics import record_failed_login

        record_failed_login()
        record_event(
            db, "auth.login_fail", user_id=None, ip_address=ip_address, user_agent=user_agent
        )
        return None

    access_token = create_access_token(str(user.id), user.role, user.token_version)
    refresh_token = create_refresh_token(user.id)

    create_refresh_token_record(db, user.id, refresh_token, settings.JWT_REFRESH_TTL_DAYS)

    record_event(
        db, "auth.login_success", user_id=user.id, ip_address=ip_address, user_agent=user_agent
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserPublic.model_validate(user),
    )


def refresh_access_token(db: Session, refresh_token: str) -> AccessTokenResponse | None:
    try:
        payload = decode_token(refresh_token)
    except Exception:
        return None

    if payload.get("type") != "refresh":
        return None

    user_id = uuid.UUID(payload["sub"])
    valid_token = find_valid_refresh_token(db, refresh_token, user_id)
    if not valid_token:
        return None

    from src.backend.db.repositories.user_repo import get_by_id

    user = get_by_id(db, user_id)
    if not user or not user.is_active or user.deleted_at:
        return None

    new_access_token = create_access_token(str(user.id), user.role, user.token_version)
    new_refresh_token = create_refresh_token(user.id)

    create_refresh_token_record(db, user.id, new_refresh_token, settings.JWT_REFRESH_TTL_DAYS)
    revoke_single(db, valid_token.id)

    record_event(db, "auth.token_refresh", user_id=user.id)

    return AccessTokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


def logout(
    db: Session,
    user_id: uuid.UUID,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    from src.backend.db.repositories.user_repo import get_by_id

    # Increment token_version so all existing access tokens become invalid.
    user = get_by_id(db, user_id)
    if user is not None:
        user.token_version += 1
        db.commit()
    return True

    revoke_all_for_user(db, user_id)
    record_event(db, "auth.logout", user_id=user_id, ip_address=ip_address, user_agent=user_agent)
    return True
