import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.backend.core.security import hash_password
from src.backend.db.base import Base
from src.backend.db.session import get_db
from src.backend.main import app
from src.backend.models.user import User

TEST_DATABASE_URL = "postgresql://swa:swa@localhost:5432/swa_erp_test"

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, future=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


def _reset_tables():
    with engine.connect() as conn:
        conn.execute(
            text("TRUNCATE TABLE audit_log, refresh_tokens, users RESTART IDENTITY CASCADE")
        )
        conn.commit()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


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
