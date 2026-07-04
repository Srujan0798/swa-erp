# Wave-4 Task 3: Task Comments & Notifications

**Skill:** `tdd`, `code-review`, `email-notification`, `celery-worker`
**Estimated:** 45 min

---

## Goal
Threaded comments on tasks + in-app/email notifications for assignment, status change, due dates, mentions.

---

## Files to Create/Modify

### 1. Notification Model (`src/backend/models/notification.py`)
```python
from sqlalchemy import Column, UUID, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from src.backend.db.base import Base
from datetime import datetime
import enum

class NotificationType(str, enum.Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_DUE_SOON = "task_due_soon"
    TASK_OVERDUE = "task_overdue"
    TASK_COMMENT = "task_comment"
    TASK_MENTION = "task_mention"
    TASK_DEPENDENCY_BLOCKED = "task_dependency_blocked"
    TASK_DEPENDENCY_RESOLVED = "task_dependency_resolved"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    reference_type = Column(String(50))  # "task", "project", etc.
    reference_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)

    user = relationship("User", back_populates="notifications")
```

### 2. Notification Repository (`src/backend/db/repositories/notification_repo.py`)
```python
from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.models.notification import Notification, NotificationType

class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID, type: NotificationType, title: str, message: str,
                     reference_type: str = None, reference_id: UUID = None) -> Notification:
        notif = Notification(
            user_id=user_id, type=type, title=title, message=message,
            reference_type=reference_type, reference_id=reference_id
        )
        self.session.add(notif)
        await self.session.flush()
        return notif

    async def get_unread_count(self, user_id: UUID) -> int:
        stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id, Notification.is_read == False
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def list(self, user_id: UUID, unread_only: bool = False, skip: int = 0, limit: int = 50) -> List[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read == False)
        stmt = stmt.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> bool:
        stmt = update(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        ).values(is_read=True)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def mark_all_read(self, user_id: UUID) -> int:
        stmt = update(Notification).where(
            Notification.user_id == user_id, Notification.is_read == False
        ).values(is_read=True)
        result = await self.session.execute(stmt)
        return result.rowcount
```

### 3. Notification Service (`src/backend/services/notification_service.py`)
```python
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.db.repositories.notification_repo import NotificationRepository
from src.backend.db.repositories.user_repo import UserRepository
from src.backend.models.notification import NotificationType
from src.backend.schemas.notification import NotificationCreate
from src.backend.workers.notification_worker import send_notification_email

class NotificationService:
    def __init__(self, session: AsyncSession):
        self.repo = NotificationRepository(session)
        self.user_repo = UserRepository(session)

    async def create_notification(self, user_id: UUID, type: NotificationType, title: str, message: str,
                                  reference_type: str = None, reference_id: UUID = None) -> Notification:
        notif = await self.repo.create(user_id, type, title, message, "task", reference_id)
        # Queue email asynchronously
        user = await self.user_repo.get(user_id)
        if user and user.email:
            send_notification_email.delay(user.email, title, message, type.value)
        return notif

    async def notify_task_assigned(self, task_id: UUID, assignee_id: UUID, task_title: str, assigner_id: UUID):
        await self.create_notification(
            assignee_id, NotificationType.TASK_ASSIGNED,
            f"Task assigned: {task_title}",
            f"You have been assigned to task '{task_title}'",
            "task", task_id
        )

    async def notify_status_changed(self, task_id: UUID, old_status: str, new_status: str, task_title: str,
                                    assignee_id: UUID, changer_id: UUID):
        if assignee_id != changer_id:  # Don't notify self
            await self.create_notification(
                assignee_id, NotificationType.TASK_STATUS_CHANGED,
                f"Task status changed: {task_title}",
                f"Task '{task_title}' status changed from {old_status} to {new_status}",
                "task", task_id
            )

    async def notify_due_soon(self, task_id: UUID, assignee_id: UUID, task_title: str, days: int):
        await self.create_notification(
            assignee_id, NotificationType.TASK_DUE_SOON,
            f"Task due soon: {task_title}",
            f"Task '{task_title}' is due in {days} day(s)",
            "task", task_id
        )

    async def notify_overdue(self, task_id: UUID, assignee_id: UUID, task_title: str):
        await self.create_notification(
            assignee_id, NotificationType.TASK_OVERDUE,
            f"Task overdue: {task_title}",
            f"Task '{task_title}' is past due",
            "task", task_id
        )

    async def notify_comment(self, task_id: UUID, task_title: str, comment_author_id: UUID,
                             mentioned_user_ids: List[UUID], comment_content: str):
        # Notify assignee/reporter if not author
        # Notify mentioned users
        for user_id in mentioned_user_ids:
            await self.create_notification(
                user_id, NotificationType.TASK_MENTION,
                f"Mentioned in task: {task_title}",
                f"You were mentioned in a comment on '{task_title}'",
                "task", task_id
            )

    async def notify_dependency_blocked(self, task_id: UUID, assignee_id: UUID, task_title: str, blocker_title: str):
        await self.create_notification(
            assignee_id, NotificationType.TASK_DEPENDENCY_BLOCKED,
            f"Task blocked: {task_title}",
            f"Task '{task_title}' is blocked by '{blocker_title}'",
            "task", task_id
        )

    async def notify_dependency_resolved(self, task_id: UUID, assignee_id: UUID, task_title: str):
        await self.create_notification(
            assignee_id, NotificationType.TASK_DEPENDENCY_RESOLVED,
            f"Blocker resolved: {task_title}",
            f"Task '{task_title}' is no longer blocked",
            "task", task_id
        )

    # In-app notification API
    async def get_unread_count(self, user_id: UUID) -> int:
        return await self.repo.get_unread_count(user_id)

    async def list_notifications(self, user_id: UUID, unread_only: bool = False, skip: int = 0, limit: int = 50):
        return await self.repo.list(user_id, unread_only, skip, limit)

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> bool:
        return await self.repo.mark_read(notification_id, user_id)

    async def mark_all_read(self, user_id: UUID) -> int:
        return await self.repo.mark_all_read(user_id)
```

### 4. Celery Worker (`src/backend/workers/notification_worker.py`)
```python
from celery import Celery
from src.backend.core.config import settings

celery_app = Celery("notifications", broker=settings.redis_url)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_email(self, to_email: str, title: str, message: str, type: str):
    try:
        # Use existing email service (Resend/SMTP)
        from src.backend.services.email_service import send_email
        send_email(
            to=to_email,
            subject=f"[SWA ERP] {title}",
            html=f"""
            <h3>{title}</h3>
            <p>{message}</p>
            <p><small>Type: {type}</small></p>
            <p><a href="{settings.frontend_url}">Open in ERP</a></p>
            """
        )
    except Exception as exc:
        raise self.retry(exc=exc)
```

### 5. Celery Beat Schedule (for due soon/overdue checks)
```python
# In src/backend/workers/__init__.py or config
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "check-due-soon-tasks": {
        "task": "src.backend.workers.task_notifications.check_due_soon",
        "schedule": crontab(hour=9, minute=0),  # Daily 9 AM
    },
    "check-overdue-tasks": {
        "task": "src.backend.workers.task_notifications.check_overdue",
        "schedule": crontab(hour=9, minute=30),
    },
}
```

### 6. Notification Worker (`src/backend/workers/task_notifications.py`)
```python
from celery import shared_task
from src.backend.db.session import async_session
from src.backend.services.notification_service import NotificationService
from src.backend.db.repositories.task_repo import TaskRepository
from datetime import datetime, timedelta

@shared_task
def check_due_soon():
    async def _inner():
        async with async_session() as session:
            task_repo = TaskRepository(session)
            notif_service = NotificationService(session)
            # Find tasks due in 1, 3, 7 days
            for days in [1, 3, 7]:
                target = datetime.utcnow() + timedelta(days=days)
                tasks = await task_repo.get_tasks_due_on(target.date())
                for task in tasks:
                    if task.assignee_id:
                        await notif_service.notify_due_soon(task.id, task.assignee_id, task.title, days)
    import asyncio
    asyncio.run(_inner())

@shared_task
def check_overdue():
    async def _inner():
        async with async_session() as session:
            task_repo = TaskRepository(session)
            notif_service = NotificationService(session)
            tasks = await task_repo.get_overdue_tasks()
            for task in tasks:
                if task.assignee_id:
                    await notif_service.notify_overdue(task.id, task.assignee_id, task.title)
    import asyncio
    asyncio.run(_inner())
```

---

## Acceptance Criteria
- [ ] In-app notifications: create, list, unread count, mark read
- [ ] Email sent for: assignment, status change, due soon (1/3/7 days), overdue, mentions
- [ ] Celery worker processes email queue with retries
- [ ] Daily beat checks due-soon (1/3/7 days) and overdue
- [ ] Mention parsing: `@username` in comments → notification
- [ ] Debounce: batch notifications within 5 min

---

## Test Command
```bash
pytest .specify/specs/wave-4/contracts/test_wave4_contracts.py::TestTaskComments -v
pytest .specify/specs/wave-4/contracts/test_wave4_contracts.py::TestTaskNotifications -v
```