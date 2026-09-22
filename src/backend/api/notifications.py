from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.services.notification_service import (
    list_notifications_service,
    mark_notification_read_service,
)

router = APIRouter()


@router.get("/api/tasks/notifications")
def list_notifications(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    unread_only: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
):
    notifications = list_notifications_service(
        db,
        user_id=current_user.id,
        unread_only=unread_only,
        page=page,
        page_size=page_size,
    )
    return [
        {
            "id": str(n.id),
            "user_id": str(n.user_id),
            "notification_type": n.type,
            "title": n.title,
            "message": n.message,
            "reference_type": n.reference_type,
            "reference_id": str(n.reference_id) if n.reference_id else None,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "read_at": None,
        }
        for n in notifications
    ]


@router.post("/api/tasks/notifications/{notification_id}/read")
def mark_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    success = mark_notification_read_service(db, notification_id, current_user.id)
    if not success:
        return {"updated": False}
    return {"updated": True}
