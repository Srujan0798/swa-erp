"""API versioning contract.

Strategy (see docs/ARCHITECTURE.md): the API is versioned by major in the
X-API-Version response header; changes within a major are additive-only.
"""

import tomllib
from pathlib import Path

import pytest

from src.backend.core.config import settings

pytestmark = pytest.mark.asyncio


def test_openapi_version_matches_package():
    pyproject = tomllib.loads((Path(__file__).parents[2] / "pyproject.toml").read_text())
    assert settings.APP_VERSION == pyproject["project"]["version"]
    assert settings.API_MAJOR_VERSION == settings.APP_VERSION.split(".")[0]


async def test_api_version_header_present(client):
    r = await client.get("/api/projects", headers={"Authorization": "Bearer invalid"})
    # 401 (no valid credentials) still carries the version + request headers.
    assert r.headers.get("X-API-Version") == settings.API_MAJOR_VERSION
    assert r.headers.get("X-Request-ID") is not None


async def test_healthz_has_no_api_version_header(client):
    r = await client.get("/healthz")
    assert r.status_code == 200
    assert "X-API-Version" not in r.headers
