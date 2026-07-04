from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class NotificationType(str, Enum):
    task_assigned = "task_assigned"
    task_status_changed = "task_status_changed"
    task_due_soon = "task_due_soon"
    task_overdue = "task_overdue"
    task_comment = "task_comment"


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    reference_type: str | None = None
    reference_id: str | None = None
    is_read: bool = False
    created_at: datetime
    read_at: datetime | None = None
