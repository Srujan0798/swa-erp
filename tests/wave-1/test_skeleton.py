import pytest
from httpx import AsyncClient

from tests.conftest import redis_available

pytestmark = pytest.mark.asyncio


async def test_healthz(client: AsyncClient):
    r = await client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.skipif(
    not redis_available,
    reason="requires a running Redis; /readyz reports 503 without it (environmental, not a defect)",
)
async def test_readyz_db_ok(client_with_db: AsyncClient):
    """DB connection works (test DB uses create_all, not migrations)."""
    from sqlalchemy import text

    from src.backend.db.session import get_db

    # Direct DB check to avoid /readyz latency and transaction issues
    with next(get_db()) as db:
        try:
            db.execute(text("SELECT 1"))
        except Exception:
            pytest.fail("DB connection failed")

    r = await client_with_db.get("/readyz")
    assert r.status_code in (200, 503)
    body = r.json()
    assert body["checks"]["db"] == "ok", f"DB check failed: {body.get('checks', {}).get('db')}"


async def test_request_id_header(client: AsyncClient):
    r = await client.get("/healthz")
    assert "x-request-id" in r.headers
    assert len(r.headers["x-request-id"]) >= 32


async def test_cors_preflight(client: AsyncClient):
    r = await client.options(
        "/healthz",
        headers={
            "Origin": "http://localhost:3100",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code in (200, 204)
    assert "access-control-allow-origin" in r.headers


def test_user_model_has_required_columns():
    from src.backend.models.user import User

    cols = {c.name for c in User.__table__.columns}
    assert {
        "id",
        "email",
        "password_hash",
        "name",
        "role",
        "is_active",
        "created_at",
        "updated_at",
        "deleted_at",
        "token_version",
    } <= cols
