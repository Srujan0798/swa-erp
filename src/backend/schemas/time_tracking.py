import uuid
from datetime import date as _date
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TimesheetStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class TimeEntryCreate(BaseModel):
    project_id: uuid.UUID
    task_id: uuid.UUID | None = None
    date: _date
    hours: Decimal = Field(gt=0, le=24)
    description: str = Field(min_length=1, max_length=2000)
    is_billable: bool = True


class TimeEntryUpdate(BaseModel):
    date: _date | None = None
    hours: Decimal | None = Field(default=None, gt=0, le=24)
    description: str | None = Field(default=None, min_length=1, max_length=2000)
    is_billable: bool | None = None


class TimeEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    task_id: uuid.UUID | None
    user_id: uuid.UUID
    date: date
    hours: Decimal
    description: str
    is_billable: bool
    created_at: datetime
    user_name: str | None = None
    project_name: str | None = None


class TimeEntryListResponse(BaseModel):
    items: list[TimeEntryRead]
    total: int
    page: int
    page_size: int


class TimesheetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    week_start: date
    week_end: date
    status: TimesheetStatus
    total_hours: Decimal
    billable_hours: Decimal
    approved_by: uuid.UUID | None
    approved_at: datetime | None
    created_at: datetime
    user_name: str | None = None
    approved_by_name: str | None = None
    entries: list[TimeEntryRead] = []


class TimesheetListResponse(BaseModel):
    items: list[TimesheetRead]
    total: int
    page: int
    page_size: int
