"""
Idempotency-Key storage layer.

Uses Redis when available (REDIS_URL in config), otherwise falls back to an
in-process dict. The dict fallback is per-process / per-worker — NOT shared
across Gunicorn worker processes, meaning idempotency is only enforced within
a single worker. For production Redis is required for full cross-process
guarantee. See docs/idempotency.md for details.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any

from src.backend.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Redis backend (preferred)
# ---------------------------------------------------------------------------

_redis_client: Any | None = None
_use_redis: bool | None = None

# ---------------------------------------------------------------------------
# In-process fallback (NOT shared across worker processes)
# ---------------------------------------------------------------------------

_fallback_store: dict[str, tuple[dict, float]] = {}
_fallback_lock = threading.Lock()


def _get_redis() -> Any | None:
    """Return the Redis client, or None if unavailable."""
    global _redis_client, _use_redis

    if _use_redis is not None:
        return _redis_client

    try:
        import redis  # type: ignore

        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2, socket_timeout=2)
        r.ping()
        _redis_client = r
        _use_redis = True
        logger.info("Idempotency storage: using Redis at %s", settings.REDIS_URL)
        return _redis_client
    except Exception as e:
        _redis_client = None
        _use_redis = False
        logger.warning(
            "Idempotency storage: Redis unavailable (%s); falling back to in-process dict. "
            "Idempotency will NOT be enforced across worker processes.",
            e,
        )
        return None


def check_idempotency_key(key: str) -> dict | None:
    """
    Return the cached response for *key* if it has been seen before, else None.

    The returned dict must include ``status_code`` and ``body`` keys so the
    caller can reconstruct the original response (FastAPI/Starlette JSONResponse).
    """
    if not key:
        return None

    redis_client = _get_redis()

    if redis_client is not None:
        try:
            raw = redis_client.get(f"idempotency:{key}")
            if raw is None:
                return None
            if isinstance(raw, bytes):
                raw = raw.decode()
            return json.loads(raw)
        except Exception as e:
            logger.warning("Redis idempotency get failed (%s); falling back to dict", e)

    # In-process fallback
    with _fallback_lock:
        entry = _fallback_store.get(key)
        if entry is None:
            return None
        response, expiry = entry
        if time.time() > expiry:
            del _fallback_store[key]
            return None
        return response


def store_idempotency_key(key: str, response: dict, ttl_seconds: int = 86400) -> None:
    """Store *response* under *key* for ``ttl_seconds`` (default 24h)."""
    if not key:
        return

    redis_client = _get_redis()

    if redis_client is not None:
        try:
            redis_client.set(
                f"idempotency:{key}",
                json.dumps(response),
                ex=ttl_seconds,
            )
            return
        except Exception as e:
            logger.warning("Redis idempotency set failed (%s); falling back to dict", e)

    # In-process fallback
    with _fallback_lock:
        _fallback_store[key] = (response, time.time() + ttl_seconds)


def clear_idempotency_key(key: str) -> None:
    """Remove a stored idempotency key (useful in tests)."""
    if not key:
        return

    redis_client = _get_redis()
    if redis_client is not None:
        try:
            redis_client.delete(f"idempotency:{key}")
        except Exception:
            pass

    with _fallback_lock:
        _fallback_store.pop(key, None)