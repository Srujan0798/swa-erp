import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MaterialCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    parent_id: uuid.UUID | None = None


class MaterialCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    parent_id: uuid.UUID | None = None


class MaterialCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None
    created_at: datetime


class MaterialCategoryTree(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None
    created_at: datetime
    children: list["MaterialCategoryTree"] = []


class MaterialCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    description: str | None = None
    category_id: uuid.UUID | None = None
    unit: str = Field(min_length=1, max_length=50)


class MaterialUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    category_id: uuid.UUID | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=50)
    is_active: bool | None = None


class MaterialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    description: str | None
    category_id: uuid.UUID | None
    unit: str
    is_active: bool
    created_at: datetime
    category_name: str | None = None


class MaterialListResponse(BaseModel):
    items: list[MaterialRead]
    total: int
    page: int
    page_size: int
