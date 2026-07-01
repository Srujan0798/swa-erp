import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InvoiceItemCreate(BaseModel):
    description: str = Field(min_length=1)
    quantity: Decimal
    rate: Decimal
    category: str | None = None
    time_entry_id: uuid.UUID | None = None


class InvoiceItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    invoice_id: uuid.UUID
    description: str
    quantity: Decimal
    rate: Decimal
    amount: Decimal
    category: str | None
    time_entry_id: uuid.UUID | None
    created_at: datetime


class InvoiceCreate(BaseModel):
    due_date: date | None = None
    notes: str | None = None
    tax_rate: Decimal = Decimal("18.00")
    items: list[InvoiceItemCreate] = Field(min_length=1)


class InvoiceGenerateFromTime(BaseModel):
    start_date: date
    end_date: date


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    invoice_number: str
    status: str
    subtotal: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total: Decimal
    currency: str
    due_date: date | None
    notes: str | None
    created_by: uuid.UUID
    paid_at: datetime | None
    created_at: datetime
    items: list[InvoiceItemRead] = []
    project_name: str | None = None
    created_by_name: str | None = None


class InvoiceListResponse(BaseModel):
    items: list[InvoiceRead]
    total: int
    page: int
    page_size: int


class InvoiceUpdateStatus(BaseModel):
    status: str = Field(pattern=r"^(sent|paid)$")
