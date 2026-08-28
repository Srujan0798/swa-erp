"""
Prometheus metrics for SWA ERP.

Exposes /metrics endpoint with:
- HTTP request metrics (count, duration, in-flight) by endpoint + status class
- Database connection pool utilization
- Celery queue depth and task success/failure counts
- Business counters (failed logins, 5xx rate)
"""

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator, metrics

# Custom metrics registry
registry = CollectorRegistry()

# HTTP request metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_class"],
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    registry=registry,
)

http_requests_in_flight = Gauge(
    "http_requests_in_flight",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"],
    registry=registry,
)

# Database connection pool metrics
db_pool_size = Gauge(
    "db_pool_size",
    "Database connection pool size",
    registry=registry,
)

db_pool_checked_out = Gauge(
    "db_pool_checked_out",
    "Database connections currently checked out",
    registry=registry,
)

db_pool_overflow = Gauge(
    "db_pool_overflow",
    "Database connection pool overflow",
    registry=registry,
)

# Celery metrics
celery_queue_depth = Gauge(
    "celery_queue_depth",
    "Number of tasks waiting in Celery queue",
    ["queue"],
    registry=registry,
)

celery_tasks_total = Counter(
    "celery_tasks_total",
    "Total Celery tasks processed",
    ["queue", "status"],  # status: success, failure, retry
    registry=registry,
)

# Business metrics
failed_logins_total = Counter(
    "failed_logins_total",
    "Total failed login attempts",
    registry=registry,
)

http_5xx_total = Counter(
    "http_5xx_total",
    "Total HTTP 5xx responses",
    ["endpoint"],
    registry=registry,
)


def setup_metrics(app) -> Instrumentator:
    """
    Configure and install Prometheus metrics instrumentation.

    Two-phase setup:
    - Phase 1 (app=None): Create instrumentator and add middleware (must be before app starts)
    - Phase 2 (app=FastAPI): Expose /metrics endpoint (after app is created)

    Returns the Instrumentator instance for further customization.
    """
    instrumentator = Instrumentator(
        registry=registry,
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=False,
        excluded_handlers=["/metrics", "/healthz", "/readyz"],
    )

    # Add default metrics (request count, duration, in-flight by endpoint + status)
    instrumentator.add(
        metrics.requests(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )
    instrumentator.add(
        metrics.latency(
            should_include_handler=True,
            should_include_method=True,
        )
    )
    instrumentator.add(
        metrics.request_size(
            should_include_handler=True,
            should_include_method=True,
        )
    )
    instrumentator.add(
        metrics.response_size(
            should_include_handler=True,
            should_include_method=True,
        )
    )

    # Phase 1: Install middleware (must be done before app starts)
    if app is not None:
        instrumentator.instrument(app)

    return instrumentator


def update_db_pool_metrics(pool):
    """Update database connection pool metrics from SQLAlchemy pool."""
    try:
        db_pool_size.set(pool.size())
        db_pool_checked_out.set(pool.checkedout())
        db_pool_overflow.set(pool.overflow())
    except Exception:
        # Silently ignore if pool doesn't support these methods
        pass


def record_celery_task(queue: str, status: str):
    """Record a Celery task completion."""
    celery_tasks_total.labels(queue=queue, status=status).inc()


def record_failed_login():
    """Record a failed login attempt."""
    failed_logins_total.inc()


def record_5xx(endpoint: str):
    """Record an HTTP 5xx response."""
    http_5xx_total.labels(endpoint=endpoint).inc()
