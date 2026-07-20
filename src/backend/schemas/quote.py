import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class QuoteItemCreate(BaseModel):
    boq_item_id: uuid.UUID | None = None
    line_number: int
    category: str | None = None
    description: str = Field(min_length=1)
    specification: str | None = None
    unit: str = Field(min_length=1, max_length=50)
    quantity: Decimal
    rate: Decimal
    amount: Decimal


class QuoteItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    quote_id: uuid.UUID
    boq_item_id: uuid.UUID | None
    line_number: int
    category: str | None
    description: str
    specification: str | None
    unit: str
    quantity: Decimal
    rate: Decimal
    amount: Decimal


class QuoteCreate(BaseModel):
    boq_id: uuid.UUID
    markup_percent: Decimal = Decimal("0")
    tax_percent: Decimal = Decimal("18")
    terms: str | None = None
    validity_days: int = 30


class QuoteUpdate(BaseModel):
    markup_percent: Decimal | None = None
    tax_percent: Decimal | None = None
    terms: str | None = None
    validity_days: int | None = None
    items: list[QuoteItemCreate] | None = None


class QuoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    boq_id: uuid.UUID
    code: str | None = None
    version_number: int
    status: str
    subtotal: Decimal
    markup_percent: Decimal
    markup_amount: Decimal
    tax_percent: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    terms: str | None
    validity_days: int
    valid_until: date | None
    created_by: uuid.UUID | None
    approved_by: uuid.UUID | None
    approved_at: datetime | None
    sent_at: datetime | None
    client_response: str | None
    client_response_at: datetime | None
    client_response_notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[QuoteItemRead] = []
    creator_name: str | None = None
    approver_name: str | None = None
    project_name: str | None = None
    client_name: str | None = None


class QuoteListResponse(BaseModel):
    items: list[QuoteRead]
    total: int
    page: int
    page_size: int


class QuoteRespondRequest(BaseModel):
    response: str = Field(pattern=r"^(accepted|rejected)$")
    notes: str | None = None
