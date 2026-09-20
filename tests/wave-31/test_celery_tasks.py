"""Wave-31 task 02: Celery background PDF jobs.

Tests run Celery in eager mode (``task_always_eager``) so no broker/worker
process is required. The worker module builds its own engine from
``settings.DATABASE_URL``; we point it at the test DB by patching
``_worker_db`` to use the same session factory as the rest of the suite.
"""

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.models.client import Client
from src.backend.models.project import Project
from src.backend.models.task import Task
from src.backend.models.user import User
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
    t = Task(
        project_id=project_id,
        title=title,
        status=status,
        reporter_id=created_by,
    )
    db_session.add(t)
    db_session.commit()


@pytest.fixture(scope="function")
def committed_project():
    """Seed client+owner+project via an independent COMMITTED session.

    Evidence (ValueError('Project not found') -> celery Retry in eager mode):
    eager tasks read through their own connection (_worker_db), which under
    READ COMMITTED cannot see the uncommitted rows of the transactional
    db_session fixture. Seeding committed rows mirrors production, where the
    worker only ever reads committed data. Cleans up after itself so the
    shared swa_erp_test DB is not polluted for later tests.
    """
    from src.backend.core.security import hash_password
    s = _test_session_factory()
    try:
        # Create a dedicated PM user for this test with known password
        u = User(
            email=f"celery-pm-{uuid.uuid4().hex[:6]}@test.com",
            name="Celery PM",
            password_hash=hash_password("pm123!"),
            role="pm",
        )
        s.add(u)
        s.commit()
        s.refresh(u)
        c = Client(
            name="Celery Test Client",
            code=f"CEL-{uuid.uuid4().hex[:6]}",
            primary_email="celery@test.com",
        )
        s.add(c)
        s.commit()
        s.refresh(c)
        p = Project(
            client_id=c.id,
            name="Celery Test Project",
            code=f"CELP-{uuid.uuid4().hex[:6]}",
            status="Design",
            pm_id=u.id,
            location="Mumbai",
        )
        s.add(p)
        s.commit()
        s.refresh(p)
        ids = {"project_id": p.id, "user_id": u.id, "user_email": u.email}
        yield ids
    finally:
        try:
            pid = ids["project_id"]
            s.query(Task).filter(Task.project_id == pid).delete()
            proj = s.get(Project, pid)
            cid = proj.client_id if proj else None
            uid = proj.pm_id if proj else None
            # Delete project BEFORE client to avoid FK violation
            if proj is not None:
                s.delete(proj)
                s.flush()  # Ensure project is deleted before client
            if cid is not None:
                cli = s.get(Client, cid)
                if cli is not None:
                    s.delete(cli)
            if uid is not None:
                usr = s.get(User, uid)
                if usr is not None:
                    s.delete(usr)
            s.commit()
        finally:
            s.close()


def _add_committed_task(project_id, title, status, created_by):
    s = _test_session_factory()
    try:
        s.add(Task(project_id=project_id, title=title, status=status, reporter_id=created_by))
        s.commit()
    finally:
        s.close()


@pytest.fixture(scope="function")
async def authed_committed_client(committed_project):
    """Authenticated client for the committed_project's PM user."""
    from src.backend.main import app
    from httpx import ASGITransport, AsyncClient
    
    email = committed_project["user_email"]
    password = "pm123!"
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        if r.status_code != 200:
            # Debug: check if user exists in database
            from src.backend.models.user import User
            s = _test_session_factory()
            try:
                u = s.query(User).filter(User.email == email).first()
                if u:
                    print(f"DEBUG: User {email} exists in DB, hash: {u.password_hash[:20]}...")
                else:
                    print(f"DEBUG: User {email} NOT FOUND in DB")
            finally:
                s.close()
            raise RuntimeError(f"Could not login as {email}: {r.status_code} {r.text}")
        token = r.json()["access_token"]
        ac.headers["Authorization"] = f"Bearer {token}"
        yield ac


def test_project_summary_task_produces_stored_pdf(committed_project):
    from src.backend.core.storage import get_storage

    pid = committed_project["project_id"]
    uid = committed_project["user_id"]
    _add_committed_task(pid, "T1", "done", uid)
    _add_committed_task(pid, "T2", "todo", uid)

    result = worker_tasks.generate_project_summary_pdf.apply(args=[str(pid)])
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
    authed_committed_client, committed_project
):
    pid = committed_project["project_id"]
    uid = committed_project["user_id"]
    _add_committed_task(pid, "Async Task", "done", uid)

    r = await authed_committed_client.get(
        f"/api/exports/projects/{pid}/summary.pdf",
        params={"async": "true"},
    )
    assert r.status_code == 202
    body = r.json()
    assert "job_id" in body

    job_id = body["job_id"]
    status_r = await authed_committed_client.get(f"/api/jobs/{job_id}")
    assert status_r.status_code == 200
    status_body = status_r.json()
    assert status_body["status"] == "success"
    assert "result_url" in status_body

    result_r = await authed_committed_client.get(f"/api/jobs/{job_id}/result")
    assert result_r.status_code == 200
    assert result_r.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_async_financial_report_endpoint_returns_job_id(
    authed_committed_client,
):
    r = await authed_committed_client.get(
        "/api/exports/reports/financial.pdf",
        params={"start_date": "2026-01-01", "end_date": "2026-06-30", "async": "true"},
    )
    assert r.status_code == 202
    assert "job_id" in r.json()


def test_project_slides_task_produces_stored_pdf(committed_project):
    from src.backend.core.storage import get_storage

    pid = committed_project["project_id"]
    uid = committed_project["user_id"]
    _add_committed_task(pid, "Slides Task", "done", uid)

    result = worker_tasks.generate_project_slides_pdf.apply(args=[str(pid)])
    assert result.successful()
    stored_key = result.result
    content = get_storage().read(stored_key)
    assert content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_async_slides_endpoint_returns_job_id(
    authed_committed_client, committed_project
):
    pid = committed_project["project_id"]
    uid = committed_project["user_id"]
    _add_committed_task(pid, "Async Slides", "done", uid)

    r = await authed_committed_client.get(
        f"/api/exports/projects/{pid}/slides.pdf",
        params={"async": "true"},
    )
    assert r.status_code == 202
    assert "job_id" in r.json()


@pytest.mark.asyncio
async def test_sync_path_unchanged(authed_committed_client, committed_project):
    pid = committed_project["project_id"]
    uid = committed_project["user_id"]
    _add_committed_task(pid, "Sync Task", "todo", uid)

    r = await authed_committed_client.get(
        f"/api/exports/projects/{pid}/summary.pdf"
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_job_status_unknown_job_returns_pending(authed_committed_client):
    import uuid

    r = await authed_committed_client.get(f"/api/jobs/{uuid.uuid4()}")
    assert r.status_code == 200
    assert r.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_async_endpoint_requires_pm(authed_designer_client, test_project_id):
    r = await authed_designer_client.get(
        f"/api/exports/projects/{test_project_id}/summary.pdf",
        params={"async": "true"},
    )
    assert r.status_code in (401, 403)