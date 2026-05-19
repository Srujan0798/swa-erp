import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = Response(status_code=200)
        response.headers["X-Request-ID"] = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        logger.info("request_start", method=request.method, path=request.url.path)

        try:
            result = await call_next(request)
            response = result
            response.headers["X-Request-ID"] = request_id
            logger.info(
                "request_end",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
            )
        except Exception as e:
            logger.error(
                "request_error", method=request.method, path=request.url.path, error=str(e)
            )
            raise

        return response
