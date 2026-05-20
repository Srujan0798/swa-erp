import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)
    designation: str | None = Field(default=None, max_length=100)
    is_primary: bool = False


class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    designation: str | None = Field(default=None, max_length=100)
    is_primary: bool | None = None


class ContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    email: str
    phone: str | None
    designation: str | None
    is_primary: bool
    created_at: datetime
    updated_at: datetime
