import uuid

from sqlalchemy.orm import Session

from src.backend.db.repositories.notification_repo import NotificationRepository
from src.backend.models.notification import Notification
from src.backend.models.task import Task
from src.backend.models.user import User
from src.backend.schemas.notification import NotificationType


def list_notifications_service(
    db: Session,
    user_id: uuid.UUID,
    unread_only: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> list[Notification]:
    """List a user's notifications. Owns the commit so routers stay DB-free."""
    repo = NotificationRepository(db)
    skip = (page - 1) * page_size
    notifications = repo.list(
        user_id=user_id,
        unread_only=unread_only,
        skip=skip,
        limit=page_size,
    )
    db.commit()
    return list(notifications)


def mark_notification_read_service(
    db: Session, notification_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    """Mark one notification read. Owns the commit so routers stay DB-free."""
    repo = NotificationRepository(db)
    success = repo.mark_read(notification_id=notification_id, user_id=user_id)
    db.commit()
    return bool(success)


class NotificationService:
    def __init__(self, db):
        self.db = db

    def emit(
        self, user_id, notification_type, title, message, reference_type=None, reference_id=None
    ):
        repo = NotificationRepository(self.db)
        return repo.create(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            reference_type=reference_type,
            reference_id=reference_id,
        )

    def task_assigned(self, task: Task, assignee: User, actor: User):
        self.emit(
            assignee.id,
            NotificationType.TASK_ASSIGNED,
            "Task assigned",
            f"{actor.name} assigned you to {task.title}",
            reference_type="task",
            reference_id=task.id,
        )

    def status_changed(self, task: Task, actor: User):
        for uid in {task.assignee_id, task.reporter_id}:
            if uid:
                self.emit(
                    uid,
                    NotificationType.TASK_STATUS_CHANGED,
                    "Task status updated",
                    f"{task.title} is now {task.status}",
                    reference_type="task",
                    reference_id=task.id,
                )

    def task_commented(self, task: Task, actor: User):
        for uid in {task.assignee_id, task.reporter_id}:
            if uid:
                self.emit(
                    uid,
                    NotificationType.TASK_COMMENT,
                    "New comment",
                    f"{actor.name} commented on {task.title}",
                    reference_type="task",
                    reference_id=task.id,
                )
