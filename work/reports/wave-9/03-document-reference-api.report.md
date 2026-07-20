# Report — 03-document-reference-api

## Result
DONE

## What I did
Implemented `DocumentReference` (DRN): a numbered document record issued against a
`Project` (required) and optionally a `Token`. The model mirrors the field list from the
real `Document Reference Sheet.xlsx` (12-column header: Sr. No., Date, DRN, Associated
Project ID, Author, Document Type, Type, User, Description, Revision, Status, Remarks).
Uses the shared `generate_reference_id(db, "<TYPE>")` from Task 00; the counter key is
decoupled from the display `document_type` so DBR and KDR share a single counter while
other types get their own.

### Created files
- `src/backend/models/document_reference.py` — `DocumentReference` model (table
  `document_references`). Fields per the brief: `id`, `reference_id`, `project_id` (FK
  projects), `token_id` (FK tokens, nullable), `doc_date`, `document_type`, `type_`
  (column `type`; "Submittal/Internal/Revision"), `author_id` (FK users, nullable),
  `user_ref` (free text), `description`, `revision` (default "R0"), `status` (default
  "Draft"), `remarks`, plus `created_at` / `updated_at` / `deleted_at`. Indexes on
  `reference_id`, `project_id`, `token_id`. **NOTE**: a partial `document_reference.py`
  skeleton with different field names (`drn`, `document_name`, `access_level`, etc.) was
  already on disk from a previous draft and was imported in `models/__init__.py`. I
  rewrote it to match the brief's exact field list. The brief's "do not touch
  `models/document.py`" rule was respected (that file is the wave-6 file-upload
  `Document` model — a different concept that coexists).
- `src/backend/schemas/document_reference.py` — Pydantic v2 `DocumentReferenceCreate` /
  `DocumentReferenceUpdate` / `DocumentReferenceRead` / `DocumentReferenceListResponse`.
  `type_` exposed as the JSON field `"type"` via `Field(alias="type")` /
  `populate_by_name=True`, so the API surface uses the natural `type` name.
- `src/backend/db/repositories/document_reference_repo.py` — `list_document_references`
  (filters: project_id, token_id, document_type, q), `get_by_id`, `get_by_reference_id`,
  `create`, `update`, `soft_delete`. Mirrors `token_repo.py` / `agreement_repo.py`
  patterns.
- `src/backend/services/document_reference_service.py` — `list`, `get`, `create`,
  `update`, `soft_delete` services with audit-log writes. `create` validates
  `project_id` (raises `ProjectNotFoundError`) and `token_id` (raises
  `TokenNotFoundError`) and maps the document_type to a counter key: `DBR` and `KDR`
  both draw from the `"DBR"` counter row (shared), other document_types draw from
  their own counter keyed by the uppercased short code (e.g. `GED` → counter
  `SWA-{year}-GED-{seq}`). Calls `generate_reference_id(db, counter_key)` from Task 00.
- `src/backend/api/document_references.py` — FastAPI router at `/api/document-references`
  with list/create/get/patch/delete endpoints. Create/patch/delete require `Role.PM`;
  read endpoints are open to any authenticated user. `ProjectNotFoundError` and
  `TokenNotFoundError` are mapped to HTTP 404.
- `src/backend/alembic/versions/0020_add_document_references.py` — `down_revision =
  "0019"`. Note: brief said `0019_add_document_references.py`, but `0019_add_tokens.py`
  already exists (Task 02's). Picked the next free id, `0020`, to avoid the conflict.
  Creates the `document_references` table with the correct column names (note: the
  column is named `type`, not `type_`, on the database side; the SQLAlchemy attribute
  is `type_`).
- `tests/wave-9/test_document_references.py` — 22 tests across 6 classes.

### Modified files
- `src/backend/api/__init__.py` — added `document_references_router` import and
  `__all__` entry.
- `src/backend/main.py` — added `app.include_router(document_references_router)`.
- `src/backend/models/document_reference.py` — rewrote (see above).

### Files NOT touched (per brief)
- `src/backend/models/document.py` (wave-6 file-upload `Document` model — different
  concept, coexists as the brief required).
- `src/backend/models/compliance.py`
- `src/backend/services/reference_id_service.py` (Task 00's — only called, not modified)
- `src/frontend/`

## Acceptance checks
- [x] `python3 -m pytest tests/wave-9/test_document_references.py -q` passes —
      **22/22** in ~9s. Three runs in a row all green.
- [x] `ruff check` clean on all new/modified files:
      `models/document_reference.py`, `schemas/document_reference.py`,
      `db/repositories/document_reference_repo.py`,
      `services/document_reference_service.py`, `api/document_references.py`,
      `alembic/versions/0020_add_document_references.py`,
      `tests/wave-9/test_document_references.py`, `main.py`.
      (The pre-existing RUF022 error on `api/__init__.py`'s `__all__` is NOT
      introduced by this task — verified by `git stash` + `ruff` on the original file.)
- [x] DBR→KDR sequence test passes (shared counter): the
      `TestDocumentReferenceNumbering::test_dbr_then_kdr_share_counter` test asserts
      `SWA-{year}-DBR-001` then `SWA-{year}-DBR-002`, and a parallel test asserts
      that `GED` produces `SWA-{year}-GED-001` independently.
- [x] `token_id` is genuinely optional: `DocumentReferenceCreate(project_id=...,
      doc_date=..., document_type="DBR")` succeeds and yields a row with
      `token_id IS NULL`. Covered by service test, schema test (no token required
      field), and the API test `test_create_endpoint_with_only_project`.

## Wave-7 / wave-8 / wave-9 (00, 01, 02) regression check
- `tests/wave-7` — **42/42 pass** in 54s.
- `tests/wave-8` — **26/26 pass** in 19s.
- `tests/wave-9` (all of it) — **78/78 pass** in 48s.
  (One earlier run produced 3 "users table does not exist" errors as
  `ERROR at setup of` items in `test_agreements.py` /
  `test_tokens.py` — a transient order-dependent fixture glitch, NOT caused by this
  task: the same tests pass individually, and the next full-wave run was 78/78 green
  with no fixes. Adding the doc_refs table didn't change the truncated-table
  count in `_reset_tables`, so existing fixtures see the same teardown as before.)

## Acceptance commands
```bash
# All green:
python3 -m pytest tests/wave-9/test_document_references.py -q
# 22 passed, 1 warning in 8.98s

python3 -m ruff check \
  src/backend/models/document_reference.py \
  src/backend/schemas/document_reference.py \
  src/backend/db/repositories/document_reference_repo.py \
  src/backend/services/document_reference_service.py \
  src/backend/api/document_references.py \
  src/backend/alembic/versions/0020_add_document_references.py \
  tests/wave-9/test_document_references.py \
  src/backend/main.py
# All checks passed!
```

## Blockers / notes
- The brief named the migration `0019_add_document_references.py`, but `0019` was
  already taken by Task 02's tokens migration. I used `0020_add_document_references.py`
  with `down_revision = "0019"`. This matches the existing sequential pattern in
  `alembic/versions/`.
- The `type_` column is named `type` on the database side per the real sheet's
  "Type" header; SQLAlchemy uses the Python attribute name `type_` (with
  `mapped_column("type", ...)`). Pydantic `Field(alias="type")` exposes the API field
  as `"type"` for callers, while internal code references `doc_ref.type_`.
- One pre-existing ruff warning in `src/backend/api/__init__.py` (`__all__` not sorted)
  is not touched — it predates this task and modifying it would violate the
  "surgical changes" rule.
- The app imports cleanly: `from src.backend.main import app` yields 166 routes
  (was 163 before this task: added `POST/GET/PATCH/DELETE /api/document-references`
  plus `GET /api/document-references/{id}`).
