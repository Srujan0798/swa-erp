from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class NotificationType(Enum):
    # Uppercase member names (wave-32): notification_service referenced
    # TASK_ASSIGNED etc.; values stay lowercase for storage.
    TASK_ASSIGNED = "task_assigned"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_DUE_SOON = "task_due_soon"
    TASK_OVERDUE = "task_overdue"
    TASK_COMMENT = "task_comment"


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
