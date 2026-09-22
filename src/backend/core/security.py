import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt  # pyjwt replaces python-jose (CVE-2024-33663, CVE-2024-33664)

from src.backend.core.config import settings


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    user_id: uuid.UUID | str,
    role: str | None = None,
    token_version: int | None = None,
) -> str:
    if isinstance(user_id, dict):
        payload_in = user_id
        user_id = uuid.UUID(payload_in["sub"]) if "sub" in payload_in else uuid.uuid4()
        role = role or payload_in.get("role", "viewer")
        token_version = payload_in.get("token_version", token_version)
    if token_version is None:
        raise ValueError("token_version is required for access tokens (revocation check)")
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_ACCESS_TTL_MIN)).timestamp()),
        "type": "access",
        "v": int(token_version),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: uuid.UUID) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)).timestamp()),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def verify_token_version(token_version_from_payload: int, user_id: uuid.UUID, db) -> bool:
    """Return True when the token's embedded version matches the DB current version."""
    from src.backend.db.repositories.user_repo import get_by_id

    user = get_by_id(db, user_id)
    if user is None:
        return False
    return user.token_version == token_version_from_payload
