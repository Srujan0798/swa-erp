import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_healthz(client: AsyncClient):
    r = await client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_readyz_db_ok(client_with_db: AsyncClient):
    r = await client_with_db.get("/readyz")
    assert r.status_code == 200
    assert r.json()["checks"]["db"] == "ok"


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
        "version",
    } <= cols
