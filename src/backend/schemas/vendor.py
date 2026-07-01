import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class VendorContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    designation: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    is_primary: bool = False


class VendorContactUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    designation: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    is_primary: bool | None = None


class VendorContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    name: str
    designation: str | None
    email: str | None
    phone: str | None
    is_primary: bool


class VendorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = None
    city: str | None = None
    state: str | None = None
    gst_number: str | None = Field(default=None, max_length=20)
    pan_number: str | None = Field(default=None, max_length=10)
    contacts: list[VendorContactCreate] = Field(default_factory=list)


class VendorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = None
    city: str | None = None
    state: str | None = None
    gst_number: str | None = Field(default=None, max_length=20)
    pan_number: str | None = Field(default=None, max_length=10)
    is_active: bool | None = None


class VendorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    email: str | None
    phone: str | None
    address: str | None
    city: str | None
    state: str | None
    gst_number: str | None
    pan_number: str | None
    is_active: bool
    created_at: datetime
    contacts: list[VendorContactRead] = []


class VendorListResponse(BaseModel):
    items: list[VendorRead]
    total: int
    page: int
    page_size: int
