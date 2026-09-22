from collections.abc import Callable, Iterable
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.backend.core.roles import Role, role_includes
from src.backend.core.security import decode_token
from src.backend.db.repositories.user_repo import get_by_id
from src.backend.db.session import get_db
from src.backend.models.user import User

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security_scheme),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> User:
    if creds is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = decode_token(creds.credentials)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from e
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Wrong token type")

    user_id = UUID(payload["sub"])
    user = get_by_id(db, user_id)
    if not user or not user.is_active or user.deleted_at:
        raise HTTPException(status_code=401, detail="User not active")

    # Verify token_version: reject access tokens minted before a logout/rotation.
    # The `v` claim is required (fail closed): tokens minted without it cannot
    # be version-checked and are treated as revoked, never trusted until expiry.
    if "v" not in payload:
        raise HTTPException(status_code=401, detail="Token revoked — please log in again")
    if user.token_version != int(payload["v"]):
        raise HTTPException(status_code=401, detail="Token revoked — please log in again")

    return user


def require_role(required: Role | Iterable[Role]) -> Callable[[User], User]:
    def _checker(user: User = Depends(get_current_user)) -> User:  # noqa: B008
        roles = {required} if isinstance(required, Role) else set(required)
        if not any(role_includes(Role(user.role), r) for r in roles):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return _checker
