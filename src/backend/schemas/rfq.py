import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RFQItemCreate(BaseModel):
    material_id: uuid.UUID
    quantity: Decimal = Field(gt=0)
    notes: str | None = None


class RFQItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rfq_id: uuid.UUID
    material_id: uuid.UUID
    material_name: str | None = None
    material_unit: str | None = None
    quantity: Decimal
    vendor_rate: Decimal | None = None
    notes: str | None = None


class RFQCreate(BaseModel):
    project_id: uuid.UUID
    vendor_id: uuid.UUID
    notes: str | None = None
    items: list[RFQItemCreate] = Field(min_length=1)


class RFQUpdate(BaseModel):
    notes: str | None = None


class RFQRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    project_name: str | None = None
    vendor_id: uuid.UUID
    vendor_name: str | None = None
    status: str
    rfq_number: str
    created_by: uuid.UUID
    created_by_name: str | None = None
    sent_at: datetime | None = None
    responded_at: datetime | None = None
    awarded_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    items: list[RFQItemRead] = []


class RFQListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    vendor_id: uuid.UUID
    vendor_name: str | None = None
    status: str
    rfq_number: str
    created_by: uuid.UUID
    sent_at: datetime | None = None
    responded_at: datetime | None = None
    awarded_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    item_count: int = 0


class RFQListResponse(BaseModel):
    items: list[RFQListItem]
    total: int
    page: int
    page_size: int


class RFQResponseItem(BaseModel):
    item_id: uuid.UUID
    vendor_rate: Decimal = Field(ge=0)


class RFQCompareVendor(BaseModel):
    vendor_id: uuid.UUID
    vendor_name: str | None = None
    rfq_id: uuid.UUID
    rfq_number: str
    rate: Decimal | None = None


class RFQCompareMaterial(BaseModel):
    material_id: uuid.UUID
    material_name: str | None = None
    vendors: list[RFQCompareVendor]
