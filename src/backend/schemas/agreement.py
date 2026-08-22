import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ServiceAgreementCreate(BaseModel):
    client_id: uuid.UUID
    inquiry_id: uuid.UUID | None = None
    service_name: str = Field(min_length=1, max_length=255)
    start_date: date
    end_date: date | None = None
    total_tokens: int | None = None
    status: str = Field(default="Active", max_length=50)
    notes: str | None = None

    @model_validator(mode="after")
    def _check_dates(self):
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class ServiceAgreementUpdate(BaseModel):
    service_name: str | None = Field(default=None, min_length=1, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    total_tokens: int | None = None
    status: str | None = Field(default=None, max_length=50)
    notes: str | None = None


class ServiceAgreementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reference_id: str
    client_id: uuid.UUID
    inquiry_id: uuid.UUID | None
    service_name: str
    start_date: date
    end_date: date | None
    total_tokens: int | None
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    # Enriched for Excel mental model (Client Name column)
    client_name: str | None = None


class ServiceAgreementListResponse(BaseModel):
    items: list[ServiceAgreementRead]
    total: int
    page: int
    page_size: int
