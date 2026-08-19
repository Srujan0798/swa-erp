from fastapi import APIRouter, Depends, status, Response
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Annotated

from src.backend.core.config import settings
from src.backend.db.session import get_db, engine
from src.backend.db.base import Base

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness probe - cheap, always returns ok if process is alive."""
    return {"status": "ok"}


@router.get("/readyz")
def readyz(
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> dict:
    """
    Readiness probe - checks DB, Redis, and migrations.
    
    Returns 200 if all dependencies are healthy, 503 otherwise.
    """
    checks = {}
    overall_healthy = True
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception as e:
        checks["db"] = f"error: {str(e)[:100]}"
        overall_healthy = False
    
    # Check Redis
    try:
        import redis
        redis_url = settings.REDIS_URL
        r = redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)[:100]}"
        overall_healthy = False
    
    # Check migrations at head
    try:
        from alembic.config import Config
        from alembic import script
        from alembic.runtime.migration import MigrationContext
        
        alembic_cfg = Config("src/backend/alembic.ini")
        script_dir = script.ScriptDirectory.from_config(alembic_cfg)
        
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()
            head_rev = script_dir.get_current_head()
            
            if current_rev == head_rev:
                checks["migrations"] = "ok"
            else:
                checks["migrations"] = f"pending: current={current_rev}, head={head_rev}"
                overall_healthy = False
    except Exception as e:
        checks["migrations"] = f"error: {str(e)[:100]}"
        overall_healthy = False
    
    response_data = {
        "status": "ok" if overall_healthy else "error",
        "checks": checks,
    }
    
    if not overall_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return response_data