"""API contract: every /api route is authenticated by default.

Sweeps all registered routes without credentials. Anything outside the
explicit public allowlist must answer 401/403/404/405/422 — never 200/201
(leak) or 500 (auth evaluated after crash-prone code). This pins the
wave-50 IDOR/metrics-auth fixes against regressions.
"""

import pytest

pytestmark = pytest.mark.asyncio

# No-auth public surface. Everything else must deny.
PUBLIC_PREFIXES = (
    "/api/auth/login",
    "/api/auth/refresh",
    "/healthz",
    "/readyz",
    "/metrics",  # auth-gated at runtime (403 unauthenticated), not public
    "/docs",
    "/redoc",
    "/openapi.json",
)

# Status codes that prove "denied safely" (auth, routing, or validation).
DENIED = {401, 403, 404, 405, 422}


async def test_all_api_routes_deny_anonymous(client_with_db):
    from src.backend.main import app

    failures = []
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", set()) or set()
        if not path.startswith("/api/"):
            continue
        if path.startswith(PUBLIC_PREFIXES):
            continue
        # Skip templated paths we cannot call without IDs here; those are
        # covered per-endpoint in wave suites. Exercise concrete paths.
        if "{" in path:
            continue
        for method in sorted(methods):
            if method == "GET":
                r = await client_with_db.get(path)
            elif method == "POST":
                r = await client_with_db.post(path, json={})
            elif method == "PATCH":
                r = await client_with_db.patch(path, json={})
            elif method == "PUT":
                r = await client_with_db.put(path, json={})
            elif method == "DELETE":
                r = await client_with_db.delete(path)
            else:
                continue
            if r.status_code not in DENIED:
                failures.append(f"{method} {path} -> {r.status_code}")
    assert not failures, "routes reachable without auth (or 500s):\n" + "\n".join(failures)


async def test_metrics_deny_anonymous(client_with_db):
    r = await client_with_db.get("/metrics")
    assert r.status_code == 403, r.text
