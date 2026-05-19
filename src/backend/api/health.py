from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.backend.db.session import get_db

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
def readyz(
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, str] | tuple[dict[str, str], int]:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        return {"status": "error", "db": "error"}, status.HTTP_503_SERVICE_UNAVAILABLE
