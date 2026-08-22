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
    employee_name: str | None = Field(default=None, max_length=255)
    employee_role: str | None = Field(default=None, max_length=50)
    work_type: str | None = Field(default=None, max_length=50)
    sheet_reference_id: str | None = Field(default=None, max_length=50)
    revision: str | None = Field(default=None, max_length=20)
    activity_type: str | None = Field(default=None, max_length=50)
    software_used: str | None = Field(default=None, max_length=100)
    work_mode: str | None = Field(default=None, max_length=50)
    billable_hours: Decimal | None = Field(default=None, ge=0, le=24)


class TimeEntryUpdate(BaseModel):
    date: _date | None = None
    hours: Decimal | None = Field(default=None, gt=0, le=24)
    description: str | None = Field(default=None, min_length=1, max_length=2000)
    is_billable: bool | None = None
    employee_name: str | None = Field(default=None, max_length=255)
    employee_role: str | None = Field(default=None, max_length=50)
    work_type: str | None = Field(default=None, max_length=50)
    sheet_reference_id: str | None = Field(default=None, max_length=50)
    revision: str | None = Field(default=None, max_length=20)
    activity_type: str | None = Field(default=None, max_length=50)
    software_used: str | None = Field(default=None, max_length=100)
    work_mode: str | None = Field(default=None, max_length=50)
    billable_hours: Decimal | None = Field(default=None, ge=0, le=24)


class TimeEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    task_id: uuid.UUID | None
    user_id: uuid.UUID
    date: _date
    hours: Decimal
    description: str
    is_billable: bool
    employee_name: str | None = None
    employee_role: str | None = None
    work_type: str | None = None
    sheet_reference_id: str | None = None
    revision: str | None = None
    activity_type: str | None = None
    software_used: str | None = None
    work_mode: str | None = None
    billable_hours: Decimal | None = None
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
    week_start: _date
    week_end: _date
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
