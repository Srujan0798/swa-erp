import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentReferenceCreate(BaseModel):
    project_id: uuid.UUID
    token_id: uuid.UUID | None = None
    doc_date: date
    document_type: str = Field(min_length=1, max_length=50)
    type_: str | None = Field(default=None, max_length=50, alias="type")
    author_id: uuid.UUID | None = None
    user_ref: str | None = Field(default=None, max_length=255)
    description: str | None = None
    revision: str = Field(default="R0", max_length=10)
    status: str = Field(default="Draft", max_length=50)
    remarks: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class DocumentReferenceUpdate(BaseModel):
    doc_date: date | None = None
    document_type: str | None = Field(default=None, min_length=1, max_length=50)
    type_: str | None = Field(default=None, max_length=50, alias="type")
    author_id: uuid.UUID | None = None
    user_ref: str | None = Field(default=None, max_length=255)
    description: str | None = None
    revision: str | None = Field(default=None, max_length=10)
    status: str | None = Field(default=None, max_length=50)
    remarks: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class DocumentReferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    reference_id: str
    project_id: uuid.UUID
    token_id: uuid.UUID | None
    doc_date: date
    document_type: str
    type_: str | None = Field(alias="type")
    author_id: uuid.UUID | None
    user_ref: str | None
    description: str | None
    revision: str
    status: str
    remarks: str | None
    created_at: datetime
    updated_at: datetime


class DocumentReferenceListResponse(BaseModel):
    items: list[DocumentReferenceRead]
    total: int
    page: int
    page_size: int
