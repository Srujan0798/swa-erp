import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class TokenCreate(BaseModel):
    agreement_id: uuid.UUID
    token_date: date
    token_type: str | None = Field(default=None, max_length=50)
    description: str | None = None
    token_status: str = Field(default="In Progress", max_length=50)
    tokens_used: int = Field(default=1, ge=1)
    swa_employee_id: uuid.UUID | None = None
    project_owner_id: uuid.UUID | None = None
    swa_employee_name: str | None = Field(default=None, max_length=255)
    project_owner_name: str | None = Field(default=None, max_length=255)
    client_employee_name: str | None = Field(default=None, max_length=255)
    project_id: uuid.UUID | None = None


class TokenUpdate(BaseModel):
    token_date: date | None = None
    token_type: str | None = Field(default=None, max_length=50)
    description: str | None = None
    token_status: str | None = Field(default=None, max_length=50)
    tokens_used: int | None = Field(default=None, ge=1)
    swa_employee_id: uuid.UUID | None = None
    project_owner_id: uuid.UUID | None = None
    swa_employee_name: str | None = Field(default=None, max_length=255)
    project_owner_name: str | None = Field(default=None, max_length=255)
    client_employee_name: str | None = Field(default=None, max_length=255)
    project_id: uuid.UUID | None = None


class TokenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reference_id: str
    agreement_id: uuid.UUID
    # Excel Tokens Sheet "Agreement ID" (SWA-YYYY-SA-…)
    agreement_reference_id: str | None = None
    token_date: date
    token_type: str | None
    description: str | None
    token_status: str
    tokens_used: int
    swa_employee_id: uuid.UUID | None
    project_owner_id: uuid.UUID | None
    swa_employee_name: str | None = None
    project_owner_name: str | None = None
    client_employee_name: str | None
    project_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class TokenListResponse(BaseModel):
    items: list[TokenRead]
    total: int
    page: int
    page_size: int
