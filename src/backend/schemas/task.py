import uuid
from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskFilter(BaseModel):
    status: str | None = None
    assignee_id: uuid.UUID | None = None
    priority: str | None = None
    due_before: date | None = None
    due_after: date | None = None
    search: str | None = None


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

    @field_validator("priority", mode="before")
    @classmethod
    def coerce_priority(cls, v):
        _priority_names = {0: "low", 1: "low", 2: "medium", 3: "high", 4: "critical"}
        if isinstance(v, int):
            return _priority_names.get(v, "medium")
        return v

    @model_validator(mode="before")
    @classmethod
    def map_orm_fields(cls, data):
        if hasattr(data, "_sa_instance_state"):
            mapped = {}
            for col in data.__table__.columns:
                mapped[col.name] = getattr(data, col.name)
            if "reporter_id" in mapped:
                mapped["created_by"] = mapped.pop("reporter_id")
            if "position" in mapped:
                mapped["sort_order"] = mapped.pop("position")
            assignee = getattr(data, "assignee", None)
            reporter = getattr(data, "reporter", None)
            comments = getattr(data, "comments", None)
            if assignee and hasattr(assignee, "name"):
                mapped["assignee_name"] = assignee.name
            if reporter and hasattr(reporter, "name"):
                mapped["created_by_name"] = reporter.name
            if comments is not None:
                mapped["comment_count"] = len(comments)
            return mapped
        return data


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
