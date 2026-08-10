"""Wave-31 task 02: Celery background PDF jobs.

Tests run Celery in eager mode (``task_always_eager``) so no broker/worker
process is required. The worker module builds its own engine from
``settings.DATABASE_URL``; we point it at the test DB by patching
``_worker_db`` to use the same session factory as the rest of the suite.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.workers import tasks as worker_tasks
from src.backend.workers.celery_app import app
from tests.conftest import TEST_DATABASE_URL

_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, future=True)
_test_session_factory = sessionmaker(
    autoflush=False, autocommit=False, expire_on_commit=False, bind=_engine
)


@pytest.fixture(autouse=True)
def eager_celery(monkeypatch):
    app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        task_store_eager_result=True,
        result_backend="cache+memory://",
        broker_url="memory://",
    )
    monkeypatch.setattr(worker_tasks, "_worker_db", _test_session_factory)
    yield
    app.conf.update(
        task_always_eager=False,
        task_eager_propagates=False,
        result_backend=app.conf.get("result_backend"),
        broker_url=app.conf.get("broker_url"),
    )


@pytest.fixture(scope="function")
def test_client_id(db_session):
    import uuid

    from src.backend.models.client import Client

    c = Client(
        name="Celery Test Client",
        code=f"CEL-{uuid.uuid4().hex[:6]}",
        primary_email="celery@test.com",
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c.id


@pytest.fixture(scope="function")
def test_project_id(db_session, test_client_id, admin_user):
    import uuid

    from src.backend.models.project import Project

    p = Project(
        client_id=test_client_id,
        name="Celery Test Project",
        code=f"CELP-{uuid.uuid4().hex[:6]}",
        status="Design",
        pm_id=admin_user.id,
        location="Mumbai",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p.id


def _add_task(db_session, project_id, title, status, created_by):
    from src.backend.models.task import Task

    t = Task(
        project_id=project_id,
        title=title,
        status=status,
        reporter_id=created_by,
    )
    db_session.add(t)
    db_session.commit()


def test_project_summary_task_produces_stored_pdf(
    db_session, test_project_id, admin_user
):
    from src.backend.core.storage import get_storage

    _add_task(db_session, test_project_id, "T1", "done", admin_user.id)
    _add_task(db_session, test_project_id, "T2", "todo", admin_user.id)

    result = worker_tasks.generate_project_summary_pdf.apply(
        args=[str(test_project_id)]
    )
    assert result.successful()
    stored_key = result.result
    assert isinstance(stored_key, str)
    content = get_storage().read(stored_key)
    assert content[:4] == b"%PDF"


def test_financial_report_task_produces_stored_pdf():
    from src.backend.core.storage import get_storage

    result = worker_tasks.generate_financial_report_pdf.apply(
        args=["2026-01-01", "2026-06-30"]
    )
    assert result.successful()
    stored_key = result.result
    assert isinstance(stored_key, str)
    content = get_storage().read(stored_key)
    assert content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_async_summary_endpoint_returns_job_id_then_success(
    authed_pm_client, db_session, test_project_id, admin_user
):
    _add_task(db_session, test_project_id, "Async Task", "done", admin_user.id)

    r = await authed_pm_client.get(
        f"/api/exports/projects/{test_project_id}/summary.pdf",
        params={"async": "true"},
    )
    assert r.status_code == 202
    body = r.json()
    assert "job_id" in body

    job_id = body["job_id"]
    status_r = await authed_pm_client.get(f"/api/jobs/{job_id}")
    assert status_r.status_code == 200
    status_body = status_r.json()
    assert status_body["status"] == "success"
    assert "result_url" in status_body

    result_r = await authed_pm_client.get(f"/api/jobs/{job_id}/result")
    assert result_r.status_code == 200
    assert result_r.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_async_financial_report_endpoint_returns_job_id(
    authed_pm_client,
):
    r = await authed_pm_client.get(
        "/api/exports/reports/financial.pdf",
        params={"start_date": "2026-01-01", "end_date": "2026-06-30", "async": "true"},
    )
    assert r.status_code == 202
    assert "job_id" in r.json()


@pytest.mark.asyncio
async def test_sync_path_unchanged(authed_pm_client, db_session, test_project_id, admin_user):
    _add_task(db_session, test_project_id, "Sync Task", "todo", admin_user.id)

    r = await authed_pm_client.get(
        f"/api/exports/projects/{test_project_id}/summary.pdf"
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_job_status_unknown_job_returns_pending(authed_pm_client):
    import uuid

    r = await authed_pm_client.get(f"/api/jobs/{uuid.uuid4()}")
    assert r.status_code == 200
    assert r.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_async_endpoint_requires_pm(authed_designer_client, test_project_id):
    r = await authed_designer_client.get(
        f"/api/exports/projects/{test_project_id}/summary.pdf",
        params={"async": "true"},
    )
    assert r.status_code in (401, 403)
