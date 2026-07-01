# Task 02 — Document CRUD, Folders, Search

## Goal
Build document management endpoints: full CRUD, folder operations (create/rename/delete), document search by name and tags, document versioning (re-upload creates new version), and move/rename operations.

## Files to Create / Modify

### 1. Repository additions
Modify `src/backend/db/repositories/document_repo.py` (created in task 01) to add:
- `update_document(db, document_id, **kwargs)` — update name, folder_id, tags
- `get_latest_version(db, project_id, name)` — find latest version of a document by name
- `count_versions(db, project_id, name)` — count how many versions exist
- `get_version_chain(db, project_id, name)` — return all versions ordered by version number
- `move_documents(db, document_ids, target_folder_id)` — bulk move
- `rename_folder(db, folder_id, new_name)` — update folder name

### 2. Schemas additions
Modify `src/backend/schemas/document.py` to add:
- `DocumentUpdate` — `name: str | None`, `folder_id: uuid.UUID | None`, `tags: list[str] | None`
- `DocumentVersionListResponse` — `versions: list[DocumentRead]`, `current_version: int`
- `DocumentMoveRequest` — `document_ids: list[uuid.UUID]`, `target_folder_id: uuid.UUID | None`
- `DocumentRenameRequest` — `new_name: str`

### 3. Service additions
Modify `src/backend/services/document_service.py` to add:
- `update_document(db, document_id, update_data: DocumentUpdate)` — update metadata, write audit log "document.update"
- `create_new_version(db, project_id, original_name, file_bytes, file_name, content_type, uploaded_by, tags)`:
  1. Find latest version by `get_latest_version`
  2. Version = latest + 1
  3. Save file, create Document with `parent_version_id` pointing to latest
  4. Write audit log "document.version"
  5. Return DocumentRead
- `get_version_history(db, project_id, name)` — return DocumentVersionListResponse
- `move_documents(db, document_ids, target_folder_id)` — validate all docs belong to same project, move, audit log "document.move"
- `rename_document(db, document_id, new_name)` — update name, audit log "document.rename"
- `rename_folder(db, folder_id, new_name)` — update folder name, audit log "folder.rename"

### 4. API additions
Modify `src/backend/api/documents.py` (created in task 01) to add:
- `PATCH /api/documents/{document_id}` — update metadata (name, folder_id, tags)
- `POST /api/projects/{project_id}/documents/re-upload` — multipart upload that creates new version
  - Form field: `original_name` (the name of the document to version), `file` (UploadFile)
- `GET /api/projects/{project_id}/documents/versions/{name}` — get version history
- `PUT /api/documents/{document_id}/rename` — rename document. Body: `DocumentRenameRequest`
- `PUT /api/documents/move` — bulk move. Body: `DocumentMoveRequest`
- `PUT /api/folders/{folder_id}/rename` — rename folder. Body: `DocumentRenameRequest`

### 5. Search endpoint
Add to `src/backend/api/documents.py`:
- `GET /api/projects/{project_id}/documents/search` — query params: `q` (name search), `tags` (comma-separated), `folder_id` (optional)

## Files you must NOT touch
- `src/backend/models/document.py` — no schema changes needed
- `src/frontend/` — frontend is task 05
- `tests/wave-6/test_document_upload.py` — do not modify task 01 tests

## Skills to use
- `tdd` — red → green → refactor
- `code-review` — self-review before declaring done

## The core problem (inline — no external context needed)
Documents need full lifecycle management beyond upload/download. Versioning is name-based: uploading a file with the same `original_name` creates version N+1. Tags are stored as a JSON array text column, searched via ILIKE on the text representation.

### Edge cases to handle
- Re-upload with name that doesn't exist → 404
- Move documents from different projects → 400
- Rename to name that already exists in same folder → 409
- Rename folder that is a parent of another folder → update children paths (or block)
- Search with empty query → return all
- Tags search: match any tag in comma-separated list (OR logic)

## Acceptance criteria (executable, not prose)
- [ ] `pytest tests/wave-6/test_document_management.py` passes
- [ ] PATCH updates document metadata
- [ ] Re-upload creates version N+1 and links via parent_version_id
- [ ] Version history returns all versions sorted
- [ ] Rename updates document name
- [ ] Bulk move changes folder_id for all specified documents
- [ ] Folder rename works
- [ ] Search by name returns matching documents
- [ ] Search by tags returns documents containing any specified tag
- [ ] `ruff check src/backend/` clean

## Test file
Create `tests/wave-6/test_document_management.py` with at least:
- `test_update_document_metadata` — upload, then PATCH name and tags
- `test_reupload_creates_version` — upload "design.pdf" v1, re-upload same name → v2
- `test_version_history` — upload 3 versions, verify list and current_version
- `test_rename_document` — rename and verify
- `test_move_documents` — create 2 folders, move doc between them
- `test_folder_rename` — rename folder
- `test_search_by_name` — upload "report.pdf" and "spec.pdf", search "report"
- `test_search_by_tags` — upload with tags ["structural", "steel"], search tag "steel"
- `test_move_documents_different_projects` — expect 400

## How to deliver
1. Extend repository, service, API with new endpoints
2. Run `pytest tests/wave-6/test_document_management.py`
3. Run `ruff check src/backend/`
4. Write report to `work/reports/wave-6/02-document-management.report.md`
5. Use `work/REPORT_TEMPLATE.md`
6. Stop

## Constraints
- Time budget: 20 min
- No new dependencies without flagging
- Match existing patterns (see existing repo/service/api files)
- Tags stored as JSON text; do NOT add a separate tags table
- Allowed tools: Read, Edit, Write, Bash, Glob, Grep
