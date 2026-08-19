import os
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.backend.core.config import settings


def _rate_limit_disabled() -> bool:
    """Bypass flag for the test suite (env var) and explicit dev toggles."""
    return os.environ.get("DISABLE_AUTH_RATE_LIMIT", "").lower() in ("1", "true", "yes")


@dataclass
class _Bucket:
    count: int = 0
    reset_at: float = field(default_factory=lambda: time.monotonic() + 60.0)


class IPRateLimiter:
    def __init__(self, max_requests: int, window_seconds: float = 60.0) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, _Bucket] = defaultdict(_Bucket)

    def _client_key(self, request: Request) -> str:
        if request.client and request.client.host:
            return request.client.host
        forwarded = request.headers.get("X-Forwarded-For", "unknown").split(",")[0].strip()
        return forwarded or "unknown"

    def check(self, request: Request) -> tuple[bool, int]:
        key = self._client_key(request)
        now = time.monotonic()
        bucket = self._buckets[key]
        if now >= bucket.reset_at:
            bucket.count = 0
            bucket.reset_at = now + self.window_seconds
        bucket.count += 1
        if bucket.count > self.max_requests:
            retry_after = max(1, int(bucket.reset_at - now))
            return False, retry_after
        return True, 0


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    _RATE_LIMITED_PATHS = ("/api/auth/login", "/api/auth/refresh")

    def __init__(self, app, limiter: IPRateLimiter) -> None:
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if _rate_limit_disabled():
            return await call_next(request)
        if any(request.url.path.startswith(p) for p in self._RATE_LIMITED_PATHS):
            allowed, retry_after = self.limiter.check(request)
            if not allowed:
                return Response(
                    content='{"detail":"Too many requests. Please try again later."}',
                    status_code=429,
                    media_type="application/json",
                    headers={"Retry-After": str(retry_after)},
                )
        return await call_next(request)


_auth_limiter = IPRateLimiter(max_requests=settings.AUTH_RATE_LIMIT_PER_MIN, window_seconds=60.0)


def auth_rate_limiter() -> IPRateLimiter:
    return _auth_limiter


def install_auth_rate_limiter(app) -> None:
    app.add_middleware(AuthRateLimitMiddleware, limiter=_auth_limiter)
