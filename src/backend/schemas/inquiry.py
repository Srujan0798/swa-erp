import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InquiryCreate(BaseModel):
    inquiry_date: date
    inquiry_type: str | None = Field(default=None, max_length=50)
    inquiry_source: str | None = Field(default=None, max_length=100)
    client_name: str = Field(min_length=1, max_length=255)
    requirement_summary: str | None = None
    estimated_value: Decimal | None = None
    priority: str | None = Field(default=None, max_length=20)
    status: str = Field(default="New", max_length=50)
    owner_id: uuid.UUID | None = None
    notes: str | None = None


class InquiryUpdate(BaseModel):
    inquiry_date: date | None = None
    inquiry_type: str | None = Field(default=None, max_length=50)
    inquiry_source: str | None = Field(default=None, max_length=100)
    client_name: str | None = Field(default=None, min_length=1, max_length=255)
    requirement_summary: str | None = None
    estimated_value: Decimal | None = None
    priority: str | None = Field(default=None, max_length=20)
    status: str | None = Field(default=None, max_length=50)
    owner_id: uuid.UUID | None = None
    notes: str | None = None


class InquiryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reference_id: str
    inquiry_date: date
    inquiry_type: str | None
    inquiry_source: str | None
    client_name: str
    requirement_summary: str | None
    estimated_value: Decimal | None
    priority: str | None
    status: str
    owner_id: uuid.UUID | None
    notes: str | None
    converted_client_id: uuid.UUID | None
    converted_project_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class InquiryListResponse(BaseModel):
    items: list[InquiryRead]
    total: int
    page: int
    page_size: int


class InquiryConvertRequest(BaseModel):
    project_name: str = Field(min_length=1, max_length=255)
    project_code: str | None = Field(default=None, max_length=50)
    project_description: str | None = None
    project_status: str | None = None
    pm_id: uuid.UUID | None = None
    designer_id: uuid.UUID | None = None
    auditor_id: uuid.UUID | None = None
    location: str | None = None
    estimated_value: Decimal | None = None
    start_date: date | None = None
    target_end_date: date | None = None
    client_id: uuid.UUID | None = None
    client_address: str | None = None
    client_city: str | None = None
    client_state: str | None = None
    client_pincode: str | None = None
    client_country: str | None = None
    client_industry: str | None = None
    client_gst_number: str | None = None
    client_primary_email: str | None = None
    client_primary_phone: str | None = None


class InquiryCandidateClient(BaseModel):
    id: uuid.UUID
    name: str
    code: str


class InquiryAmbiguousClientResponse(BaseModel):
    detail: str
    inquiry_client_name: str
    candidates: list[InquiryCandidateClient]
