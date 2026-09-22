"""Idempotency keys for retry-safe POSTs.

Send `Idempotency-Key: <unique string>` with a mutating POST. The first
request executes and its exact response is stored; retries with the same
key + same body replay the stored response instead of re-executing.
Same key + different body is rejected (422) to surface client bugs.
Keys expire after 24h (lazy expiry on lookup).
"""

import hashlib
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.backend.models.idempotency_key import IdempotencyKey

TTL = timedelta(hours=24)
MAX_KEY_LENGTH = 64


class IdempotencyError(ValueError):
    """Key misuse: malformed key, or reuse with a different body."""


def hash_request(method: str, path: str, body_json: str) -> str:
    return hashlib.sha256(f"{method}\n{path}\n{body_json}".encode()).hexdigest()


def _validate_key(key: str | None) -> str | None:
    if key is None:
        return None
    key = key.strip()
    if not key or len(key) > MAX_KEY_LENGTH:
        raise IdempotencyError("invalid_idempotency_key")
    return key


def replay_or_execute(
    db: Session,
    *,
    key: str | None,
    user_id: uuid.UUID,
    method: str,
    path: str,
    request_hash: str,
    execute: Callable[[], tuple[int, dict[str, Any]]],
) -> tuple[int, dict[str, Any], bool]:
    """Run execute() once per key. Returns (status_code, body, replayed)."""
    key = _validate_key(key)
    if key is None:
        status_code, body = execute()
        return status_code, body, False

    now = datetime.now(UTC)
    existing = (
        db.query(IdempotencyKey)
        .filter(IdempotencyKey.key == key, IdempotencyKey.user_id == user_id)
        .first()
    )
    if existing is not None:
        if existing.expires_at <= now:
            db.delete(existing)
            db.flush()
        elif existing.request_hash != request_hash:
            raise IdempotencyError("idempotency_key_reuse")
        else:
            return existing.status_code, dict(existing.response_body), True

    status_code, body = execute()
    try:
        with db.begin_nested():
            db.add(
                IdempotencyKey(
                    key=key,
                    user_id=user_id,
                    method=method,
                    path=path,
                    request_hash=request_hash,
                    status_code=status_code,
                    response_body=body,
                    expires_at=now + TTL,
                )
            )
            db.flush()
    except IntegrityError:
        stored = (
            db.query(IdempotencyKey)
            .filter(IdempotencyKey.key == key, IdempotencyKey.user_id == user_id)
            .first()
        )
        if stored is not None and stored.request_hash == request_hash and stored.expires_at > now:
            return stored.status_code, dict(stored.response_body), True
        raise IdempotencyError("idempotency_key_reuse") from None
    db.commit()
    return status_code, body, False
