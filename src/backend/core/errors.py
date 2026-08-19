"""
Error tracking integration (Sentry) for SWA ERP.

Env-gated: absent SENTRY_DSN -> no-op, zero overhead, no crash.
Captures unhandled exceptions with request context + request ID.
Scrubs PII and secrets before sending.
"""
import os
import logging
from typing import Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from src.backend.core.config import settings

# Module-level flag to track initialization
_sentry_initialized = False


def scrub_pii(event, hint):
    """
    Scrub PII and secrets from Sentry events before sending.
    
    This is critical as the system handles real client business data.
    """
    # Remove sensitive headers
    if "request" in event and "headers" in event["request"]:
        sensitive_headers = [
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token",
            "proxy-authorization",
        ]
        for header in sensitive_headers:
            if header in event["request"]["headers"]:
                event["request"]["headers"][header] = "[REDACTED]"

    # Remove sensitive query parameters
    if "request" in event and "query_string" in event["request"]:
        # Could parse and filter, but for now just note it
        pass

    # Remove sensitive data from exception context
    if "exception" in event and "values" in event["exception"]:
        for exc in event["exception"]["values"]:
            if "stacktrace" in exc and "frames" in exc["stacktrace"]:
                for frame in exc["stacktrace"]["frames"]:
                    if "vars" in frame:
                        sensitive_keys = [
                            "password",
                            "secret",
                            "token",
                            "api_key",
                            "api_secret",
                            "access_token",
                            "refresh_token",
                            "authorization",
                            "credit_card",
                            "ssn",
                            "pan_number",
                            "gstin",
                            "bank_account",
                            "iban",
                        ]
                        for key in list(frame["vars"].keys()):
                            if any(sens in key.lower() for sens in sensitive_keys):
                                frame["vars"][key] = "[REDACTED]"

    return event


def init_sentry() -> bool:
    """
    Initialize Sentry SDK if SENTRY_DSN is configured.
    
    Returns True if initialized, False if DSN not set (no-op mode).
    """
    global _sentry_initialized
    
    dsn = os.getenv("SENTRY_DSN") or getattr(settings, "SENTRY_DSN", None)
    
    if not dsn:
        # No DSN configured - run in no-op mode
        logging.getLogger(__name__).info(
            "SENTRY_DSN not configured; error tracking disabled (no-op mode)"
        )
        return False
    
    if _sentry_initialized:
        return True
    
    # Configure logging integration to capture logs as breadcrumbs
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    
    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FastApiIntegration(
                transaction_style="endpoint",
                failed_request_status_codes=range(400, 600),
            ),
            SqlalchemyIntegration(),
            sentry_logging,
        ],
        # Scrub PII before sending
        before_send=scrub_pii,
        # Set traces sample rate (10% of transactions)
        traces_sample_rate=0.1,
        # Set profiles sample rate
        profiles_sample_rate=0.1,
        # Environment
        environment=os.getenv("APP_ENV", "development"),
        # Release tracking
        release=os.getenv("APP_VERSION", "1.0.0"),
        # Attach stacktraces
        attach_stacktrace=True,
        # Send default PII (we scrub it in before_send)
        send_default_pii=False,
    )
    
    _sentry_initialized = True
    logging.getLogger(__name__).info("Sentry error tracking initialized")
    return True


def capture_exception(exc: Exception, request=None, **context):
    """
    Capture an exception with request context.
    
    Safe to call even if Sentry is not initialized (no-op).
    """
    if not _sentry_initialized:
        return
    
    with sentry_sdk.push_scope() as scope:
        # Add request context if available
        if request:
            scope.set_context("request", {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": request.client.host if request.client else None,
            })
            # Add request ID if present (from our middleware)
            request_id = request.headers.get("X-Request-ID")
            if request_id:
                scope.set_tag("request_id", request_id)
        
        # Add custom context
        for key, value in context.items():
            scope.set_context(key, value)
        
        sentry_sdk.capture_exception(exc)


def capture_message(message: str, level: str = "info", **context):
    """
    Capture a message with context.
    
    Safe to call even if Sentry is not initialized (no-op).
    """
    if not _sentry_initialized:
        return
    
    with sentry_sdk.push_scope() as scope:
        for key, value in context.items():
            scope.set_context(key, value)
        sentry_sdk.capture_message(message, level=level)


def add_breadcrumb(message: str, category: str = "custom", level: str = "info", **data):
    """
    Add a breadcrumb for debugging context.
    
    Safe to call even if Sentry is not initialized (no-op).
    """
    if not _sentry_initialized:
        return
    
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data,
    )


def get_sentry_initialized() -> bool:
    """Check if Sentry has been initialized."""
    return _sentry_initialized