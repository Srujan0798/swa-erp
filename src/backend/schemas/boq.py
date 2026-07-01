import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BOQItemCreate(BaseModel):
    line_number: int = Field(ge=1)
    category: str | None = Field(default=None, max_length=100)
    description: str = Field(min_length=1)
    specification: str | None = None
    unit: str = Field(min_length=1, max_length=50)
    quantity: Decimal = Field(ge=0)
    rate: Decimal = Field(ge=0)
    amount: Decimal = Field(ge=0)


class BOQItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    boq_id: uuid.UUID
    line_number: int
    category: str | None
    description: str
    specification: str | None
    unit: str
    quantity: Decimal
    rate: Decimal
    amount: Decimal


class BOQCreate(BaseModel):
    project_id: uuid.UUID
    version_number: int
    file_name: str
    file_path: str
    parsed_by: uuid.UUID | None = None
    notes: str | None = None
    items: list[BOQItemCreate] = []


class BOQRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    version_number: int
    file_name: str
    parsed_at: datetime
    parsed_by: uuid.UUID | None = None
    notes: str | None
    is_active: bool
    created_at: datetime
    file_path: str | None = None
    items: list[BOQItemRead] = []


class BOQListRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    version_number: int
    file_name: str
    parsed_at: datetime
    parsed_by: uuid.UUID | None = None
    notes: str | None
    is_active: bool
    created_at: datetime
    item_count: int = 0


class BOQListResponse(BaseModel):
    items: list[BOQListRead]
    total: int
    page: int
    page_size: int


class BOQItemListResponse(BaseModel):
    items: list[BOQItemRead]
    total: int
    page: int
    page_size: int
