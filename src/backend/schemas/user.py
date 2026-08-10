import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.backend.core.roles import Role


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: Role


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    role: Role | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    name: str
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    items: list[UserRead]
    total: int
    page: int
    page_size: int


class UserAssigneeRead(BaseModel):
    """Slim user row for assignee / team pickers (any authenticated role)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    # str not EmailStr: import/system identities may use reserved domains (.local)
    email: str
    name: str
    role: Role


class UserAssigneeListResponse(BaseModel):
    items: list[UserAssigneeRead]
    total: int
