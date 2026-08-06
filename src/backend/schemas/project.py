import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ProjectStatus(StrEnum):
    LEAD = "Lead"
    QUOTE = "Quote"
    AWARDED = "Awarded"
    DESIGN = "Design"
    VENDOR = "Vendor"
    EXECUTION = "Execution"
    VALIDATION = "Validation"
    CLOSED = "Closed"


class ProjectCreate(BaseModel):
    client_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    description: str | None = None
    status: ProjectStatus = ProjectStatus.LEAD
    pm_id: uuid.UUID | None = None
    designer_id: uuid.UUID | None = None
    auditor_id: uuid.UUID | None = None
    location: str | None = Field(default=None, max_length=255)
    estimated_value: Decimal | None = None
    start_date: date | None = None
    target_end_date: date | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    status: ProjectStatus | None = None
    pm_id: uuid.UUID | None = None
    designer_id: uuid.UUID | None = None
    auditor_id: uuid.UUID | None = None
    location: str | None = Field(default=None, max_length=255)
    estimated_value: Decimal | None = None
    actual_value: Decimal | None = None
    start_date: date | None = None
    target_end_date: date | None = None
    actual_end_date: date | None = None
    is_active: bool | None = None
    expected_version: int | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    code: str
    description: str | None
    status: ProjectStatus
    pm_id: uuid.UUID | None
    designer_id: uuid.UUID | None
    auditor_id: uuid.UUID | None
    location: str | None
    estimated_value: Decimal | None
    actual_value: Decimal | None
    start_date: date | None
    target_end_date: date | None
    actual_end_date: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    version: int = 1
    client_name: str | None = None
    pm_name: str | None = None
    designer_name: str | None = None
    auditor_name: str | None = None


class ProjectListResponse(BaseModel):
    items: list[ProjectRead]
    total: int
    page: int
    page_size: int
