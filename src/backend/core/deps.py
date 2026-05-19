from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.backend.core.roles import Role, role_includes
from src.backend.core.security import decode_token
from src.backend.db.repositories.user_repo import get_by_id
from src.backend.db.session import get_db
from src.backend.models.user import User

security_scheme = HTTPBearer()


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security_scheme),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> User:
    try:
        payload = decode_token(creds.credentials)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from e
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Wrong token type")
    user = get_by_id(db, UUID(payload["sub"]))
    if not user or not user.is_active or user.deleted_at:
        raise HTTPException(status_code=401, detail="User not active")
    return user


def require_role(required: Role) -> Callable[[User], User]:
    def _checker(user: User = Depends(get_current_user)) -> User:  # noqa: B008
        if not role_includes(Role(user.role), required):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return _checker
