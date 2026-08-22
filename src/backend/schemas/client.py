import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.backend.schemas.contact import ContactCreate, ContactRead


class ClientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    country: str = "India"
    gst_number: str | None = Field(default=None, max_length=50)
    primary_email: EmailStr
    primary_phone: str | None = Field(default=None, max_length=50)
    primary_contact: str | None = Field(default=None, max_length=255)
    date_onboarded: date | None = None
    notes: str | None = None
    industry: str | None = Field(default=None, max_length=100)
    client_status: str = Field(default="Active", max_length=50)
    contacts: list[ContactCreate] = Field(default_factory=list)


class ClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    country: str | None = None
    gst_number: str | None = Field(default=None, max_length=50)
    primary_email: EmailStr | None = None
    primary_phone: str | None = Field(default=None, max_length=50)
    primary_contact: str | None = Field(default=None, max_length=255)
    date_onboarded: date | None = None
    notes: str | None = None
    is_active: bool | None = None
    industry: str | None = Field(default=None, max_length=100)
    client_status: str | None = Field(default=None, max_length=50)


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    address: str | None
    city: str | None
    state: str | None
    pincode: str | None
    country: str
    gst_number: str | None
    primary_email: str
    primary_phone: str | None
    primary_contact: str | None = None
    date_onboarded: date | None = None
    notes: str | None
    is_active: bool
    industry: str | None = None
    client_status: str = "Active"
    first_inquiry_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    contacts: list[ContactRead] = []


class ClientListResponse(BaseModel):
    items: list[ClientRead]
    total: int
    page: int
    page_size: int
