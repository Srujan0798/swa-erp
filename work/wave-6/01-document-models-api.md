# Task 01 — Document Models & Upload/Download API

## Goal
Create the Document and DocumentFolder data models, file upload/download endpoints, and Alembic migration. Documents belong to a project and are stored on disk with metadata in the database. Files are uploaded as multipart/form-data (max 50MB) and downloaded via a presigned-like endpoint.

## Files to Create / Modify

### 1. Models
Create `src/backend/models/document.py`:
```python
class Document(Base):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    folder_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("document_folders.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array stored as text
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DocumentFolder(Base):
    __tablename__ = "document_folders"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("document_folders.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

Register both models in `src/backend/models/__init__.py`.

### 2. Schemas
Create `src/backend/schemas/document.py`:
- `DocumentCreate` — internal, for DB creation
- `DocumentRead` — Pydantic model for API response with `model_config = ConfigDict(from_attributes=True)`. Include `uploaded_by_name: str | None = None`, `tags` parsed as `list[str]`
- `DocumentListResponse` — paginated list: `items: list[DocumentRead]`, `total: int`, `page: int`, `page_size: int`
- `DocumentFolderCreate` — `name: str`, `parent_id: uuid.UUID | None = None`
- `DocumentFolderRead` — with `model_config = ConfigDict(from_attributes=True)`
- `DocumentFolderListResponse` — `items: list[DocumentFolderRead]`

### 3. Repository
Create `src/backend/db/repositories/document_repo.py`:
- `create_document(db, project_id, folder_id, name, file_path, file_size, content_type, uploaded_by, tags, version, parent_version_id)` — returns Document
- `get_by_id(db, document_id)` — returns Document or None
- `list_by_project(db, project_id, folder_id=None, page=1, page_size=20)` — paginated, exclude deleted, filter by folder
- `search_by_name(db, project_id, query)` — ILIKE search on name
- `search_by_tags(db, project_id, tags)` — JSON contains search on tags column
- `soft_delete(db, document_id)` — set deleted_at
- `create_folder(db, project_id, name, parent_id)` — returns DocumentFolder
- `list_folders(db, project_id, parent_id=None)` — exclude deleted
- `get_folder_by_id(db, folder_id)` — returns DocumentFolder or None
- `soft_delete_folder(db, folder_id)` — set deleted_at, also soft-delete all documents in folder

### 4. Service
Create `src/backend/services/document_service.py`:
- `upload_document(db, project_id, folder_id, file_bytes, file_name, content_type, uploaded_by, tags)`:
  1. Compute file hash (sha256) for dedup (informational, not blocking)
  2. Save file to `uploads/documents/{project_id}/{uuid}_{file_name}`
  3. Create Document record with version=1
  4. Write audit log entry "document.upload"
  5. Return DocumentRead
- `download_document(db, document_id)` — verify exists, not deleted; return file_path
- `get_document(db, document_id)` — return DocumentRead with uploaded_by_name
- `list_documents(db, project_id, folder_id, page, page_size)` — return DocumentListResponse
- `search_documents(db, project_id, query, tags)` — combine name + tag search
- `soft_delete_document(db, document_id)` — set deleted_at, write audit log

### 5. API
Create `src/backend/api/documents.py`:
- `POST /api/projects/{project_id}/documents` — multipart/form-data upload
  - Form fields: `file` (UploadFile), `folder_id` (optional UUID), `tags` (optional JSON string)
  - Require admin or PM role
  - File size limit: 50MB (validate `file.size`)
  - Return 201 with DocumentRead
- `GET /api/projects/{project_id}/documents` — list with query params: `folder_id`, `page`, `page_size`
- `GET /api/documents/{document_id}` — get metadata
- `GET /api/documents/{document_id}/download` — stream file response with correct Content-Type
- `DELETE /api/documents/{document_id}` — soft delete
- `POST /api/projects/{project_id}/folders` — create folder. Body: `DocumentFolderCreate`
- `GET /api/projects/{project_id}/folders` — list folders with optional `parent_id` filter
- `DELETE /api/folders/{folder_id}` — soft delete folder + contents

Register router in `src/backend/main.py` with appropriate prefixes.

### 6. Migration
Create `src/backend/alembic/versions/0010_add_documents.py`:
- Create `documents` table with all columns, FKs, indexes
- Create `document_folders` table with all columns, FKs, indexes

## Files you must NOT touch
- `src/backend/models/project.py` — no changes
- `src/frontend/` — frontend is task 05
- `tests/wave-3/` — other wave tests

## Skills to use
- `tdd` — red → green → refactor
- `code-review` — self-review before declaring done

## The core problem (inline — no external context needed)
Documents are files uploaded against a project. They live in folders (optional nesting). Each upload creates a version. Tags are stored as a JSON array in a text column. Files are stored on the local filesystem at `uploads/documents/{project_id}/`.

### Edge cases to handle
- Upload with no folder_id (root-level document)
- Upload with folder_id that doesn't exist → 404
- Download a soft-deleted document → 404
- Delete folder with nested documents → all soft-deleted
- File size exceeds 50MB → 413
- Unsupported content type → 400
- Tags must be valid JSON array string if provided

## Acceptance criteria (executable, not prose)
- [ ] `pytest tests/wave-6/test_document_upload.py` passes
- [ ] Can upload a file (any type) and get back DocumentRead with correct metadata
- [ ] Download endpoint returns file bytes with correct Content-Type header
- [ ] Listing documents excludes soft-deleted ones
- [ ] Folder creation and listing works
- [ ] Deleting a folder soft-deletes its documents
- [ ] `ruff check src/backend/` clean
- [ ] `alembic upgrade head` creates both tables

## Test file
Create `tests/wave-6/test_document_upload.py` with at least:
- `test_upload_document` — upload a small file, verify metadata returned
- `test_upload_document_with_folder` — create folder first, then upload into it
- `test_download_document` — upload then download, verify bytes match
- `test_list_documents_pagination` — upload 5 docs, list with page_size=2
- `test_soft_delete_document` — delete then list, verify excluded
- `test_upload_exceeds_max_size` — mock 51MB file, expect 413
- `test_create_folder` — create folder, verify returned
- `test_delete_folder_soft_deletes_documents` — create folder + doc, delete folder, list docs

## How to deliver
1. Implement models, schemas, repo, service, API, migration
2. Run `pytest tests/wave-6/test_document_upload.py`
3. Run `ruff check src/backend/`
4. Write report to `work/reports/wave-6/01-document-models-api.report.md`
5. Use `work/REPORT_TEMPLATE.md`
6. Stop

## Constraints
- Time budget: 25 min
- No new dependencies without flagging
- Match existing patterns (see `src/backend/models/project.py`, `src/backend/schemas/project.py`)
- File storage path: `uploads/documents/` relative to project root. Create directory if not exists.
- Allowed tools: Read, Edit, Write, Bash, Glob, Grep
