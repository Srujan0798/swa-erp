from typing import List, Optional
from uuid import UUID
from sqlalchemy import update, select, delete as sqlalchemy_delete
from src.backend.models.notification import Notification


class NotificationRepository:
    def __init__(self, session):
        self.session = session

    def create(self, user_id, notification_type, title, message, reference_type=None, reference_id=None):
        notification = Notification(
            user_id=user_id,
            type=notification_type.value if hasattr(notification_type, "value") else notification_type,
            title=title,
            message=message,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        self.session.add(notification)
        self.session.flush()
        return notification

    def get_unread_count(self, user_id):
        stmt = select(Notification.id).where(Notification.user_id == user_id, Notification.is_read.is_(False))
        result = self.session.execute(stmt)
        return len(result.scalars().all())

    def list(self, user_id, unread_only=False, skip=0, limit=50):
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        stmt = stmt.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def mark_read(self, notification_id, user_id):
        stmt = update(Notification).where(Notification.id == notification_id, Notification.user_id == user_id).values(is_read=True)
        result = self.session.execute(stmt)
        return result.rowcount > 0

    def mark_all_read(self, user_id):
        stmt = update(Notification).where(Notification.user_id == user_id, Notification.is_read.is_(False)).values(is_read=True)
        result = self.session.execute(stmt)
        return result.rowcount or 0

    def delete(self, notification_id, user_id):
        stmt = sqlalchemy_delete(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        result = self.session.execute(stmt)
        return result.rowcount > 0
