"""Wave-50 task 01 (SEC-07): export-job ownership.

User A (PM) enqueues an async export; user B (also a PM) must get 404 on
BOTH ``GET /api/jobs/{id}`` and ``GET /api/jobs/{id}/result``. User A reads
their own job fine; an admin bypasses the ownership check.

Like the wave-31 Celery tests, Celery runs in eager mode so no broker/worker
process is required; ``_worker_db`` is pointed at the test DB.
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.main import app
from src.backend.models.export_job import ExportJob
from src.backend.workers import tasks as worker_tasks
from src.backend.workers.celery_app import app as celery_app
from tests.conftest import TEST_DATABASE_URL

_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, future=True)
_test_session_factory = sessionmaker(
    autoflush=False, autocommit=False, expire_on_commit=False, bind=_engine
)


@pytest.fixture(autouse=True)
def eager_celery(monkeypatch):
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        task_store_eager_result=True,
        result_backend="cache+memory://",
        broker_url="memory://",
    )
    monkeypatch.setattr(worker_tasks, "_worker_db", _test_session_factory)
    yield
    celery_app.conf.update(
        task_always_eager=False,
        task_eager_propagates=False,
        result_backend=celery_app.conf.get("result_backend"),
        broker_url=celery_app.conf.get("broker_url"),
    )


@pytest.fixture(scope="function")
async def pm_b_client(client_with_db, test_pm_user):
    """Second PM's client sharing the same overridden test DB session."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/api/auth/login",
            json={"email": "test_pm@swa.co.in", "password": "test_pm123!"},
        )
        assert r.status_code == 200, f"PM-B login failed: {r.text}"
        ac.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
        yield ac


@pytest.fixture(scope="function")
async def enqueued_job_id(authed_pm_client, pm_user, db_session):
    """User A enqueues an async export; returns its job_id.

    Uses the financial-report endpoint: unlike the project-summary/slides
    endpoints it needs no project rows, so the eager worker (which runs on
    its own connection, outside the test's uncommitted transaction) can
    complete the task. (The wave-31 project-based eager tests cannot see
    uncommitted fixture rows cross-connection and fail for that reason —
    verified live; unrelated to ownership.)
    """
    r = await authed_pm_client.get(
        "/api/exports/reports/financial.pdf",
        params={"start_date": "2026-01-01", "end_date": "2026-06-30", "async": "true"},
    )
    assert r.status_code == 202, f"enqueue failed: {r.text}"
    job_id = r.json()["job_id"]
    # Ownership row must exist and point at user A.
    row = db_session.get(ExportJob, job_id)
    assert row is not None, "enqueue did not record an ExportJob ownership row"
    assert row.user_id == pm_user.id
    return job_id


@pytest.mark.asyncio
async def test_owner_reads_own_job_status(enqueued_job_id, authed_pm_client):
    r = await authed_pm_client.get(f"/api/jobs/{enqueued_job_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "success"


@pytest.mark.asyncio
async def test_owner_downloads_own_job_result(enqueued_job_id, authed_pm_client):
    r = await authed_pm_client.get(f"/api/jobs/{enqueued_job_id}/result")
    assert r.status_code == 200
    assert r.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_other_pm_gets_404_on_job_status(enqueued_job_id, pm_b_client):
    r = await pm_b_client.get(f"/api/jobs/{enqueued_job_id}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_other_pm_gets_404_on_job_result(enqueued_job_id, pm_b_client):
    r = await pm_b_client.get(f"/api/jobs/{enqueued_job_id}/result")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_admin_bypasses_ownership_check(enqueued_job_id, authed_admin_client):
    r = await authed_admin_client.get(f"/api/jobs/{enqueued_job_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "success"
    r2 = await authed_admin_client.get(f"/api/jobs/{enqueued_job_id}/result")
    assert r2.status_code == 200
    assert r2.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_unknown_job_id_still_returns_pending(authed_pm_client):
    """Jobs with no ownership row keep the legacy pending/404 handling."""
    r = await authed_pm_client.get(f"/api/jobs/{uuid.uuid4()}")
    assert r.status_code == 200
    assert r.json()["status"] == "pending"
