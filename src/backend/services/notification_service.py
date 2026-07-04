from src.backend.db.repositories.notification_repo import NotificationRepository
from src.backend.models.task import Task
from src.backend.models.user import User
from src.backend.schemas.notification import NotificationType


class NotificationService:
    def __init__(self, db):
        self.db = db

    def emit(self, user_id, notification_type, title, message, reference_type=None, reference_id=None):
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
