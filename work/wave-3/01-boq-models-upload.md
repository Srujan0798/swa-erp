# Task 01 — BOQ Models & Upload API

## Goal
Create the BOQ (Bill of Quantities) data model, file parser, and upload API. A BOQ belongs to a project and contains line items. Each upload creates a new version.

## Files to Create/Modify

### 1. Models
Create `src/backend/models/boq.py`:
```python
class BOQ(Base):
    __tablename__ = "boqs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    parsed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    parsed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Unique constraint: project_id + version_number

class BOQItem(Base):
    __tablename__ = "boq_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    boq_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("boqs.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    specification: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
```

Register both models in `src/backend/models/__init__.py`.

### 2. Parser
Create `src/backend/core/boq_parser.py`:
- `parse_excel(file_bytes: bytes) -> list[dict]` — uses `openpyxl` (add to requirements). Reads first sheet. Expects header row with columns: `description`, `specification`, `unit`, `quantity`, `rate`, `category` (optional). Returns list of dicts.
- `parse_json(file_bytes: bytes) -> list[dict]` — expects JSON array of objects with same keys.
- Compute `amount = quantity * rate` for each row.
- Skip empty rows.
- Return rows as dicts: `{line_number, category, description, specification, unit, quantity, rate, amount}`

**Install:** `pip install openpyxl` (add to requirements)

### 3. Schemas
Create `src/backend/schemas/boq.py`:
- `BOQItemCreate` — internal use
- `BOQItemRead` — Pydantic model for API response
- `BOQCreate` — internal
- `BOQRead` — includes version_number, file_name, parsed_at, parsed_by name
- `BOQListResponse` — paginated list

### 4. Repository
Create `src/backend/db/repositories/boq_repo.py`:
- `create_boq(db, project_id, version_number, file_name, file_path, parsed_by, items)` — creates BOQ + BOQItems in one transaction
- `get_next_version_number(db, project_id)` — `SELECT MAX(version_number) + 1 FROM boqs WHERE project_id = ?`
- `get_by_id(db, boq_id)` — returns BOQ with items
- `list_by_project(db, project_id, page, page_size)` — paginated, exclude deleted
- `soft_delete(db, boq_id)` — set deleted_at

### 5. Service
Create `src/backend/services/boq_service.py`:
- `upload_boq(db, project_id, file_bytes, file_name, content_type, parsed_by)`:
  1. Determine parser based on file extension (.xlsx vs .json)
  2. Parse file into items
  3. Compute next version number
  4. Save file to `uploads/boqs/{project_id}/{uuid}_{file_name}`
  5. Create BOQ + BOQItems in DB
  6. Write audit log entry "boq.upload"
  7. Return BOQRead

### 6. API
Create `src/backend/api/boqs.py`:
- `POST /api/projects/{project_id}/boqs` — multipart/form-data upload. Require admin or PM role.
  - Accept `file` (multipart) + optional `notes` (form field)
  - File size limit: 10MB
  - Allowed types: `.xlsx`, `.json`
  - Return 201 with BOQRead
- Register router in `src/backend/main.py` with prefix `/api/projects/{project_id}/boqs`

Actually, use a cleaner route structure:
- `POST /api/projects/{project_id}/boqs` — upload
- `GET /api/projects/{project_id}/boqs` — list versions
- `GET /api/boqs/{boq_id}` — get version
- `GET /api/boqs/{boq_id}/items` — get items
- `DELETE /api/boqs/{boq_id}` — soft delete

### 7. Migration
Create `src/backend/alembic/versions/0004_add_boqs.py`

## Acceptance Criteria
- [ ] Can upload a sample .xlsx file and get back parsed BOQ with correct line items
- [ ] Second upload for same project gets version_number = 2
- [ ] Invalid file type returns 400
- [ ] Malformed Excel (missing required columns) returns 422 with clear error
- [ ] BOQ items have correct amounts (quantity × rate)
- [ ] `pytest tests/wave-3/test_boq_upload.py` passes

## Test File
Create `tests/wave-3/test_boq_upload.py` with at least:
- `test_upload_excel_boq` — upload valid xlsx, verify items
- `test_upload_json_boq` — upload valid json, verify items
- `test_version_auto_increment` — upload twice, verify v1 then v2
- `test_invalid_file_type` — upload .txt, expect 400
- `test_missing_columns` — upload xlsx without description column, expect 422

## Notes
- Create a sample Excel file in `tests/fixtures/sample_boq.xlsx` for tests
- For tests, you can create the xlsx programmatically using openpyxl in a fixture
- File storage path: `uploads/boqs/` relative to project root. Create directory if not exists.
- Use `Decimal(str(value))` when converting parsed numbers to Decimal to avoid float precision issues.
