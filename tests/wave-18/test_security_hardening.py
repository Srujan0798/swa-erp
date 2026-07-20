"""Wave-18 production security hardening tests.

Covers four areas:
  1. SECRET_KEY fail-fast on non-dev APP_ENV
  2. Auth rate limiting (5/min/IP, 6th request returns 429)
  3. CORS origins read from settings/env (no hardcoded host)
  4. Invoice GST breakdown
"""
import importlib
import os
from decimal import Decimal

# 1) SECRET_KEY fail-fast -----------------------------------------------------


def test_secret_key_insecure_in_dev_passes():
    """In dev mode (default), the insecure default is allowed."""
    os.environ["APP_ENV"] = "dev"
    os.environ["SECRET_KEY"] = "change-me"
    import src.backend.core.config as cfg

    importlib.reload(cfg)
    s = cfg.Settings()
    assert s.SECRET_KEY == "change-me"


def test_secret_key_insecure_in_prod_fails():
    """In prod (APP_ENV != dev), the default secret must reject at construction time.

    Uses subprocess because the failure should also fire on module import
    (`settings = Settings()` at module level), which is what we want in prod.
    """
    import subprocess
    import sys

    code = (
        "import os;"
        "os.environ['APP_ENV']='prod';"
        "os.environ['SECRET_KEY']='change-me';"
        "import src.backend.core.config as cfg;"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd="/Users/srujansai/Desktop/swa-erp",
        capture_output=True,
        text=True,
        env={**os.environ, "APP_ENV": "prod", "SECRET_KEY": "change-me"},
    )
    assert result.returncode != 0, (
        f"Expected import to fail in prod with default SECRET_KEY, but it succeeded.\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )
    assert "SECRET_KEY" in result.stderr or "SECRET_KEY" in result.stdout


def test_secret_key_strong_in_prod_passes():
    os.environ["APP_ENV"] = "prod"
    os.environ["SECRET_KEY"] = "a" * 64
    import src.backend.core.config as cfg

    importlib.reload(cfg)
    s = cfg.Settings()
    assert s.SECRET_KEY == "a" * 64
    os.environ["APP_ENV"] = "dev"
    os.environ["SECRET_KEY"] = "change-me"


def test_cors_origins_read_from_env():
    """CORS_ORIGINS must come from the env, not be hardcoded."""
    os.environ["CORS_ORIGINS"] = '["https://app.example.com"]'
    import src.backend.core.config as cfg

    importlib.reload(cfg)
    s = cfg.Settings()
    assert s.CORS_ORIGINS == ["https://app.example.com"]


# 2) Rate limiting ------------------------------------------------------------


def _rate_limit_middleware_active():
    """The rate-limit middleware can be bypassed via DISABLE_AUTH_RATE_LIMIT=1
    (set by the test runner so the broader suite isn't blocked). For these
    tests we need the middleware ACTIVE so we can prove 429 behavior."""
    import os

    return os.environ.get("DISABLE_AUTH_RATE_LIMIT", "").lower() not in ("1", "true", "yes")


async def test_login_rate_limit_triggers_on_6th_attempt(client_with_db, monkeypatch):
    """6 rapid login attempts from same client -> 6th returns 429.

    We force the rate limiter back on for this single test even when the
    broader suite has set DISABLE_AUTH_RATE_LIMIT=1.
    """
    if not _rate_limit_middleware_active():
        monkeypatch.setenv("DISABLE_AUTH_RATE_LIMIT", "0")
    from src.backend.core import rate_limit as rl_mod

    auth_rate_limiter_inst = rl_mod._auth_limiter
    auth_rate_limiter_inst._buckets.clear()
    statuses = []
    for _ in range(6):
        r = await client_with_db.post(
            "/api/auth/login",
            json={"email": "ratelimit@test.com", "password": "x"},
        )
        statuses.append(r.status_code)
    assert statuses[:5] == [401, 401, 401, 401, 401]
    assert statuses[5] == 429
    assert "Retry-After" in r.headers
    auth_rate_limiter_inst._buckets.clear()


async def test_login_rate_limit_retry_after_header_present(client_with_db, monkeypatch):
    if not _rate_limit_middleware_active():
        monkeypatch.setenv("DISABLE_AUTH_RATE_LIMIT", "0")
    from src.backend.core import rate_limit as rl_mod

    auth_rate_limiter_inst = rl_mod._auth_limiter
    auth_rate_limiter_inst._buckets.clear()
    last = None
    for _ in range(6):
        last = await client_with_db.post(
            "/api/auth/login",
            json={"email": "x@y.z", "password": "x"},
        )
    assert last.status_code == 429
    assert int(last.headers["Retry-After"]) >= 1
    auth_rate_limiter_inst._buckets.clear()


# 3) CORS env-driven (additional sanity check) -------------------------------


def test_cors_middleware_uses_settings_origins():
    """main.py's CORS middleware must use settings.CORS_ORIGINS, not a hardcoded list.

    Static check: confirm main.py wires CORS through settings, and that the
    default Settings().CORS_ORIGINS parses the env-driven JSON list.
    """
    import src.backend.main as main_mod

    src = open(main_mod.__file__).read()
    assert "allow_origins=settings.CORS_ORIGINS" in src
    assert "http://localhost:3000" not in src or "settings.CORS_ORIGINS" in src

    os.environ["CORS_ORIGINS"] = '["https://prod.example.com","https://app.example.com"]'
    import src.backend.core.config as cfg

    importlib.reload(cfg)
    assert cfg.settings.CORS_ORIGINS == [
        "https://prod.example.com",
        "https://app.example.com",
    ]


# 4) Invoice GST breakdown ---------------------------------------------------


async def _setup_project(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/clients",
        json={"name": "GST Client", "code": "GSTC-1", "primary_email": "gstc@test.com"},
    )
    assert r.status_code == 201
    client_id = r.json()["id"]
    r2 = await authed_admin_client.post(
        "/api/projects",
        json={
            "client_id": str(client_id),
            "name": "GST Project",
            "code": "GSTP-1",
            "status": "Lead",
        },
    )
    assert r2.status_code == 201
    return r2.json()["id"]


async def test_invoice_gst_default_18_percent(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Service A", "quantity": "10.00", "rate": "5000.00"},
                {"description": "Service B", "quantity": "5.00", "rate": "2000.00"},
            ],
        },
    )
    assert r.status_code == 201
    inv = r.json()
    assert Decimal(str(inv["subtotal"])) == Decimal("60000.00")
    assert Decimal(str(inv["gst_percent"])) == Decimal("18.00")
    assert Decimal(str(inv["gst_amount"])) == Decimal("10800.00")
    assert Decimal(str(inv["tax_amount"])) == Decimal("10800.00")
    assert Decimal(str(inv["total"])) == Decimal("70800.00")


async def test_invoice_gst_with_custom_rate(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "tax_rate": "12.00",
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    assert r.status_code == 201
    inv = r.json()
    assert Decimal(str(inv["gst_percent"])) == Decimal("12.00")
    assert Decimal(str(inv["gst_amount"])) == Decimal("120.00")
    assert Decimal(str(inv["total"])) == Decimal("1120.00")


async def test_invoice_gst_rounding(authed_admin_client, db_session):
    """0.7% cases: subtotal=333.33, gst=18% -> 60.00 (rounded to .01)."""
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "tax_rate": "18.00",
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "333.33"},
            ],
        },
    )
    assert r.status_code == 201
    inv = r.json()
    assert Decimal(str(inv["subtotal"])) == Decimal("333.33")
    assert Decimal(str(inv["gst_amount"])) == Decimal("60.00")
    assert Decimal(str(inv["total"])) == Decimal("393.33")


async def test_invoice_gst_visible_on_get(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "X", "quantity": "2.00", "rate": "1000.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    r2 = await authed_admin_client.get(f"/api/invoices/{inv_id}")
    assert r2.status_code == 200
    body = r2.json()
    assert Decimal(str(body["gst_amount"])) == Decimal("360.00")
    assert Decimal(str(body["total"])) == Decimal("2360.00")
