import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    project_id: uuid.UUID
    folder_id: uuid.UUID | None = None
    name: str = Field(min_length=1, max_length=255)
    stored_name: str = Field(min_length=1, max_length=255)
    file_path: str = Field(min_length=1, max_length=500)
    file_size: int = Field(default=0, ge=0)
    content_type: str = Field(min_length=1, max_length=255)
    uploaded_by: uuid.UUID | None = None
    tags: str | None = None
    version_number: int = Field(default=1, ge=1)
    parent_version_id: uuid.UUID | None = None


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    folder_id: uuid.UUID | None
    name: str
    stored_name: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_by: uuid.UUID | None
    tags: str | None
    version_number: int
    parent_version_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DocumentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    folder_id: uuid.UUID | None = None
    tags: str | None = None


class DocumentVersionListResponse(BaseModel):
    versions: list[DocumentRead]
    current_version: int


class DocumentMoveRequest(BaseModel):
    document_ids: list[uuid.UUID]
    target_folder_id: uuid.UUID | None = None


class DocumentRenameRequest(BaseModel):
    new_name: str = Field(min_length=1, max_length=255)


class DocumentListResponse(BaseModel):
    items: list[DocumentRead]
    total: int
    page: int
    page_size: int


class DocumentFolderCreate(BaseModel):
    project_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    name: str = Field(min_length=1, max_length=255)


class DocumentFolderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    parent_id: uuid.UUID | None
    name: str
    created_at: datetime


class DocumentFolderListResponse(BaseModel):
    items: list[DocumentFolderRead]
    total: int
