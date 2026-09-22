import fcntl
import os
import tempfile
import uuid

# Disable the auth rate limiter for the test suite BEFORE the app is imported.
os.environ.setdefault("DISABLE_AUTH_RATE_LIMIT", "1")

import pytest
import redis
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker

import src.backend.models  # noqa: F401 - registers all models with Base.metadata
from src.backend.core.security import hash_password
from src.backend.db.base import Base
from src.backend.db.session import get_db
from src.backend.main import app
from src.backend.models.client import Client
from src.backend.models.project import Project
from src.backend.models.user import User

# Allow SQLite for tests that want to run without PostgreSQL (e.g., CI without Docker)
USE_SQLITE = os.getenv("TEST_USE_SQLITE", "0") == "1"

if USE_SQLITE:
    TEST_DATABASE_URL = "sqlite://"
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=__import__("sqlalchemy.pool", fromlist=["StaticPool"]).StaticPool,
    )
else:
    TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://swa:swa@localhost:5432/swa_erp_test")
    # Add statement_timeout and lock_timeout to fail fast on deadlocks/hangs
    # These are set per-connection via connect_args
    engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
        future=True,
        pool_size=5,
        connect_args={
            "options": "-c statement_timeout=15000 -c lock_timeout=10000"
        },
    )

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


# Compute redis availability at import time for skipif conditions
try:
    _r = redis.Redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        socket_connect_timeout=1,
        socket_timeout=1,
    )
    _r.ping()
    redis_available = True
except Exception:
    redis_available = False


# Global lock for schema reset to prevent deadlocks across pytest-asyncio event loops
_schema_reset_lock_file = os.path.join(tempfile.gettempdir(), "swa_erp_schema_reset.lock")
_schema_reset_done = False


def _acquire_schema_lock():
    """Acquire a file-based lock for schema reset."""
    lock_fd = os.open(_schema_reset_lock_file, os.O_CREAT | os.O_RDWR, 0o644)
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    return lock_fd


def _release_schema_lock(lock_fd):
    """Release the file-based lock."""
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    os.close(lock_fd)
    try:
        os.unlink(_schema_reset_lock_file)
    except Exception:
        pass


def _reset_schema_once():
    """Reset database schema - creates all tables from metadata. Runs only once per process."""
    global _schema_reset_done
    if _schema_reset_done:
        return

    lock_fd = _acquire_schema_lock()
    try:
        # Double-check after acquiring lock
        if _schema_reset_done:
            return

        if USE_SQLITE:
            Base.metadata.create_all(bind=engine)
        else:
            with engine.connect() as conn:
                conn = conn.execution_options(isolation_level="AUTOCOMMIT")
                # Instead of DROP SCHEMA (which causes deadlocks), truncate all tables
                inspector = inspect(engine)
                tables = inspector.get_table_names(schema="public")
                if tables:
                    # Truncate tables in dependency order (roughly) - just try each one
                    for table in tables:
                        try:
                            conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                        except Exception:
                            pass  # Ignore truncate errors
                else:
                    # No tables exist, ensure schema exists
                    result = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'public'"))
                    if not result.fetchone():
                        conn.execute(text("CREATE SCHEMA public"))
            Base.metadata.create_all(bind=engine)
            _seed_alembic_version()

        _schema_reset_done = True
    finally:
        _release_schema_lock(lock_fd)


@pytest.fixture(scope="session")
def redis_available_fixture() -> bool:
    """Fixture for tests that need to check Redis availability at runtime."""
    return redis_available


def _alembic_head():
    """Return current alembic head revision string."""
    from alembic import script
    from alembic.config import Config
    cfg = Config("src/backend/alembic.ini")
    sd = script.ScriptDirectory.from_config(cfg)
    return sd.get_current_head()


def _seed_alembic_version(conn=None):
    """Create alembic_version table and seed with current head (autocommit mode)."""
    if USE_SQLITE:
        return  # SQLite doesn't need alembic_version
    if conn is None:
        with engine.connect() as conn:
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            head = _alembic_head()
            conn.execute(
                text("CREATE TABLE IF NOT EXISTS alembic_version "
                     "(version_num VARCHAR(32) NOT NULL PRIMARY KEY)")
            )
            conn.execute(text("DELETE FROM alembic_version"))
            conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head}')"))
    else:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        head = _alembic_head()
        conn.execute(
            text("CREATE TABLE IF NOT EXISTS alembic_version "
                 "(version_num VARCHAR(32) NOT NULL PRIMARY KEY)")
        )
        conn.execute(text("DELETE FROM alembic_version"))
        conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head}')"))


def _truncate_all_tables():
    """Truncate all tables in the public schema (PostgreSQL only)."""
    if USE_SQLITE:
        return
    inspector = inspect(engine)
    tables = inspector.get_table_names(schema="public")
    if not tables:
        return
    with engine.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        # Use TRUNCATE without disabling FK checks - just truncate in dependency order
        # Get tables sorted by foreign key dependencies (roughly)
        for table in tables:
            try:
                conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
            except Exception:
                pass  # Ignore truncate errors in teardown


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test DB schema ONCE per session. Autouse ensures it runs before any test."""
    print(f"\n[SETUP_TEST_DB] Starting session-scoped setup (PID={os.getpid()})")
    _reset_schema_once()
    print("[SETUP_TEST_DB] Schema reset complete")
    yield
    print(f"[SETUP_TEST_DB] Teardown (PID={os.getpid()})")
    # Teardown: clean up for next session
    if not USE_SQLITE:
        _truncate_all_tables()


@pytest.fixture(scope="function")
def db_session():
    """Function-scoped DB session with transaction rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    # Start a nested transaction (SAVEPOINT)
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        try:
            nested.rollback()
        except Exception:
            pass
        try:
            transaction.rollback()
        except Exception:
            pass
        try:
            connection.close()
        except Exception:
            pass


@pytest.fixture(scope="function")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def client_with_db(db_session):
    """Async client with DB session override for tests that need direct DB access."""
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# User fixtures
@pytest.fixture(scope="function")
def admin_user(db_session):
    u = User(
        email="admin@swa.co.in",
        name="Admin",
        password_hash=hash_password("admin123!"),
        role="admin",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture(scope="function")
def pm_user(db_session):
    u = User(
        email="pm@swa.co.in",
        name="PM",
        password_hash=hash_password("pm123!"),
        role="pm",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture(scope="function")
def viewer_user(db_session):
    u = User(
        email="viewer@swa.co.in",
        name="Viewer",
        password_hash=hash_password("viewer123!"),
        role="viewer",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture(scope="function")
def designer_user(db_session):
    u = User(
        email="designer@swa.co.in",
        name="Designer",
        password_hash=hash_password("designer123!"),
        role="designer",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture(scope="function")
def auditor_user(db_session):
    u = User(
        email="auditor@swa.co.in",
        name="Auditor",
        password_hash=hash_password("auditor123!"),
        role="auditor",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture(scope="function")
def client_factory(db_session):
    created = []

    def _create(name="Test Client", code=None):
        if code is None:
            code = f"TC-{uuid.uuid4().hex[:6]}"
        c = Client(name=name, code=code, primary_email=f"{code}@test.com")
        db_session.add(c)
        db_session.commit()
        db_session.refresh(c)
        created.append(c)
        return c

    return _create


@pytest.fixture(scope="function")
def test_project(db_session, client_factory):
    client = client_factory()
    p = Project(client_id=client.id, name="Test Project", code="TP-1")
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture(scope="function")
def test_project_with_pm(db_session, client_factory, pm_user):
    """Project with pm_user assigned as PM."""
    client = client_factory()
    p = Project(client_id=client.id, name="Test Project", code="TP-1", pm_id=pm_user.id)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture(scope="function")
def test_pm_user(db_session):
    u = User(
        email="test_pm@swa.co.in",
        name="Test PM",
        password_hash=hash_password("test_pm123!"),
        role="pm",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture(scope="function")
def test_designer_user(db_session):
    u = User(
        email="test_designer@swa.co.in",
        name="Test Designer",
        password_hash=hash_password("test_designer123!"),
        role="designer",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


# Authenticated client fixtures
@pytest.fixture(scope="function")
async def authed_admin_client(db_session, admin_user):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/api/auth/login",
            json={"email": "admin@swa.co.in", "password": "admin123!"},
        )
        token = r.json()["access_token"]
        ac.headers["Authorization"] = f"Bearer {token}"
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def authed_pm_client(db_session, pm_user):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/api/auth/login",
            json={"email": "pm@swa.co.in", "password": "pm123!"},
        )
        token = r.json()["access_token"]
        ac.headers["Authorization"] = f"Bearer {token}"
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def authed_viewer_client(db_session, viewer_user):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/api/auth/login",
            json={"email": "viewer@swa.co.in", "password": "viewer123!"},
        )
        token = r.json()["access_token"]
        ac.headers["Authorization"] = f"Bearer {token}"
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def authed_designer_client(db_session, designer_user):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/api/auth/login",
            json={"email": "designer@swa.co.in", "password": "designer123!"},
        )
        token = r.json()["access_token"]
        ac.headers["Authorization"] = f"Bearer {token}"
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def authed_auditor_client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/api/auth/login",
            json={"email": "auditor@swa.co.in", "password": "auditor123!"},
        )
        token = r.json()["access_token"]
        ac.headers["Authorization"] = f"Bearer {token}"
        yield ac
    app.dependency_overrides.clear()
