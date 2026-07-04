import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.backend.core.security import hash_password
from src.backend.db.base import Base
from src.backend.db.session import get_db
from src.backend.main import app
import src.backend.models  # noqa: F401 - registers all models with Base.metadata
from src.backend.models.client import Client
from src.backend.models.project import Project
from src.backend.models.user import User

TEST_DATABASE_URL = "postgresql://swa:swa@localhost:5432/swa_erp_test"

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, future=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


def _reset_tables():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        existing = {r[0] for r in result}
        tables = [t for t in Base.metadata.tables.keys() if t in existing]
        if tables:
            try:
                conn.execute(text(f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE"))
            except Exception:
                conn.rollback()
                for t in tables:
                    conn.execute(text(f"DROP TABLE IF EXISTS {t} CASCADE"))
        conn.commit()
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        created = [r[0] for r in result]
        print(f"[setup_test_db] Created tables: {created}")
    yield
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))


@pytest.fixture(scope="function")
def db_session():
    _reset_tables()
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def client_with_db(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


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
def client_factory(db_session):
    created = []

    def _create(name="Test Client", code="TC-1"):
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


@pytest.fixture(scope="function")
async def authed_admin_client(client_with_db, admin_user):
    r = await client_with_db.post(
        "/api/auth/login",
        json={"email": "admin@swa.co.in", "password": "admin123!"},
    )
    token = r.json()["access_token"]
    client_with_db.headers["Authorization"] = f"Bearer {token}"
    return client_with_db


@pytest.fixture(scope="function")
async def authed_pm_client(client_with_db, pm_user):
    r = await client_with_db.post(
        "/api/auth/login",
        json={"email": "pm@swa.co.in", "password": "pm123!"},
    )
    token = r.json()["access_token"]
    client_with_db.headers["Authorization"] = f"Bearer {token}"
    return client_with_db


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
async def authed_viewer_client(client_with_db, viewer_user):
    r = await client_with_db.post(
        "/api/auth/login",
        json={"email": "viewer@swa.co.in", "password": "viewer123!"},
    )
    token = r.json()["access_token"]
    client_with_db.headers["Authorization"] = f"Bearer {token}"
    return client_with_db


@pytest.fixture(scope="function")
async def authed_designer_client(client_with_db, designer_user):
    r = await client_with_db.post(
        "/api/auth/login",
        json={"email": "designer@swa.co.in", "password": "designer123!"},
    )
    token = r.json()["access_token"]
    client_with_db.headers["Authorization"] = f"Bearer {token}"
    return client_with_db
