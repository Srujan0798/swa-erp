from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user
from src.backend.db.session import get_db
from src.backend.models.user import User

router = APIRouter()


@router.get("/api/tasks/notifications")
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: str | None = Query(default=None),
    types: str | None = Query(default=None),
    unread_only: bool = Query(default=False),
):
    return []


@router.post("/api/tasks/notifications/{notification_id}/read")
def mark_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {}
