import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from src.backend.models.refresh_token import RefreshToken


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _verify_token(token: str, hashed: str) -> bool:
    return hashlib.sha256(token.encode("utf-8")).hexdigest() == hashed


def create(db: Session, user_id: uuid.UUID, token: str, ttl_days: int) -> RefreshToken:
    expires_at = datetime.now(UTC) + timedelta(days=ttl_days)
    rt = RefreshToken(
        user_id=user_id,
        token_hash=_hash_token(token),
        expires_at=expires_at,
    )
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


def find_valid(db: Session, token: str, user_id: uuid.UUID) -> RefreshToken | None:
    tokens = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.now(UTC),
        )
        .all()
    )
    for t in tokens:
        if _verify_token(token, t.token_hash):
            return t
    return None


def revoke_all_for_user(db: Session, user_id: uuid.UUID) -> None:
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None),
    ).update({RefreshToken.revoked_at: datetime.now(UTC)})
    db.commit()
