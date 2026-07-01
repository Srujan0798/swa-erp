import uuid
from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: uuid.UUID | None = None
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str | None
    status: str
    priority: str
    assignee_id: uuid.UUID | None
    assignee_name: str | None = None
    created_by: uuid.UUID
    created_by_name: str | None = None
    due_date: date | None
    sort_order: int
    comment_count: int = 0
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    items: list[TaskRead]
    total: int
    page: int
    page_size: int


class TaskCommentCreate(BaseModel):
    content: str = Field(min_length=1)


class TaskCommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    user_name: str | None = None
    content: str
    created_at: datetime


class TaskTransition(BaseModel):
    to_status: TaskStatus


class TaskReorder(BaseModel):
    status: TaskStatus
    sort_order: int


class TaskBulkStatusUpdate(BaseModel):
    task_ids: list[uuid.UUID]
    new_status: TaskStatus


class TaskAssign(BaseModel):
    assignee_id: uuid.UUID


class TaskAssignResponse(BaseModel):
    task_id: uuid.UUID
    assignee_id: uuid.UUID | None
    assignee_name: str | None


class TaskStatsResponse(BaseModel):
    todo: int = 0
    in_progress: int = 0
    done: int = 0
    total: int = 0


class MyTasksResponse(BaseModel):
    items: list[TaskRead]
    total: int
    stats: TaskStatsResponse
