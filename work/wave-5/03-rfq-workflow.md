# Task 03 — RFQ (Request for Quotation) Workflow

## Goal
Create the RFQ model and workflow for sending material requests to vendors, receiving responses, comparing quotes, and awarding. An RFQ belongs to a project and is sent to a specific vendor.

## Files to Create/Modify

### 1. Models
Create `src/backend/models/rfq.py`:
```python
import enum

class RFQStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    RESPONDED = "responded"
    COMPARED = "compared"
    AWARDED = "awarded"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class RFQ(Base):
    __tablename__ = "rfqs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=RFQStatus.DRAFT.value)
    rfq_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    awarded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class RFQItem(Base):
    __tablename__ = "rfq_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfq_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rfqs.id"), nullable=False, index=True)
    material_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("materials.id"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    vendor_rate: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
```

Register both models in `src/backend/models/__init__.py`.

### 2. Schemas
Create `src/backend/schemas/rfq.py`:
- `RFQCreate` — project_id, vendor_id, notes, items (list of {material_id, quantity, notes})
- `RFQUpdate` — notes, status transitions
- `RFQRead` — full RFQ with items, vendor name, project name, created_by name
- `RFQListItem` — abbreviated for list view
- `RFQListResponse` — paginated
- `RFQItemCreate` — material_id, quantity, notes
- `RFQItemRead` — includes material name, unit, vendor_rate
- `RFQResponse` — items with vendor_rate for each
- `RFQCompareResponse` — multiple vendors' rates for same materials

### 3. Repository
Create `src/backend/db/repositories/rfq_repo.py`:
- `create_rfq(db, data, created_by)` — create RFQ + items, auto-generate rfq_number
- `get_by_id(db, rfq_id)` — RFQ with items, vendor, project
- `list_by_project(db, project_id, page, page_size, status)` — paginated
- `list_by_vendor(db, vendor_id, page, page_size, status)` — paginated
- `update_status(db, rfq_id, status, timestamp_field)` — update status + timestamp
- `submit_response(db, rfq_id, items_data)` — update vendor_rate on items
- `get_rfq_number(db)` — auto-generate next RFQ number (format: RFQ-{YYYY}-{NNN})
- `compare_vendors(db, project_id, material_ids)` — get rates from multiple vendors for same materials
- `soft_delete(db, rfq_id)` — set deleted_at

### 4. Service
Create `src/backend/services/rfq_service.py`:
Valid status transitions:
```
DRAFT → SENT, CANCELLED
SENT → RESPONDED, CANCELLED
RESPONDED → COMPARED, CLOSED
COMPARED → AWARDED, CLOSED
AWARDED → CLOSED
```

- `create_rfq(db, project_id, data, created_by)` — create + audit "rfq.create"
- `send_rfq(db, rfq_id, sent_by)` — DRAFT → SENT, set sent_at + audit "rfq.send"
- `receive_response(db, rfq_id, items_data, responded_by)` — SENT → RESPONDED, set responded_at, update vendor_rate on items + audit "rfq.respond"
- `compare_rfq(db, project_id, material_ids)` — get RFQs for project, group by material, return comparison
- `award_rfq(db, rfq_id, awarded_by)` — COMPARED → AWARDED, set awarded_at + audit "rfq.award"
- `close_rfq(db, rfq_id, closed_by)` — any terminal → CLOSED + audit "rfq.close"
- `cancel_rfq(db, rfq_id, cancelled_by)` — DRAFT/SENT → CANCELLED + audit "rfq.cancel"
- `get_rfq(db, rfq_id)` — return with items
- `list_project_rfqs(db, project_id, page, page_size, status)` — paginated
- `get_next_rfq_number(db)` — "RFQ-2026-001" format

### 5. API
Create `src/backend/api/rfqs.py`:
- `POST /api/projects/{project_id}/rfqs` — create RFQ (require admin or PM)
- `GET /api/projects/{project_id}/rfqs` — list RFQs, query: page, page_size, status
- `GET /api/rfqs/{rfq_id}` — get RFQ detail
- `POST /api/rfqs/{rfq_id}/send` — transition to SENT
- `POST /api/rfqs/{rfq_id}/respond` — submit vendor response (body: items with rates)
- `POST /api/rfqs/{rfq_id}/award` — transition to AWARDED
- `POST /api/rfqs/{rfq_id}/close` — transition to CLOSED
- `POST /api/rfqs/{rfq_id}/cancel` — transition to CANCELLED
- `GET /api/projects/{project_id}/rfqs/compare` — compare vendor rates, query: material_ids

Register router in `src/backend/main.py` with appropriate prefixes.

### 6. Migration
Create `src/backend/alembic/versions/0009_add_rfqs.py` — creates `rfqs` and `rfq_items` tables.

## Files you must NOT touch
- `src/backend/models/vendor.py`, `src/backend/models/material.py` (Tasks 01-02)
- `src/backend/models/project.py` (wave-2)

## Acceptance Criteria
- [ ] `pytest tests/wave-5/test_rfq_workflow.py` passes
- [ ] `make lint` clean
- [ ] RFQ auto-numbered: RFQ-2026-001, RFQ-2026-002, etc.
- [ ] Valid status transitions enforced; invalid transitions return 400
- [ ] Send sets sent_at timestamp
- [ ] Response updates vendor_rate on items
- [ ] Compare endpoint returns materials grouped with vendor rates
- [ ] Award sets awarded_at timestamp
- [ ] Audit logs written for every transition
- [ ] Soft-deleted RFQs excluded from queries

## Test File
Create `tests/wave-5/test_rfq_workflow.py` with at least:
- `test_create_rfq` — create with items, verify auto-number
- `test_rfq_status_transitions` — draft → sent → responded → compared → awarded → closed
- `test_rfq_invalid_transition` — e.g., draft → responded fails
- `test_send_rfq` — verify sent_at set
- `test_receive_response` — verify vendor_rate saved
- `test_compare_vendors` — two RFQs same project, compare returns both rates
- `test_cancel_rfq` — draft → cancelled
- `test_list_project_rfqs` — filter by status
- `test_rfq_item_materials` — verify material names in response

## Notes
- RFQ number format: `RFQ-{YYYY}-{NNN}` where NNN resets yearly (or not — configurable)
- Compare endpoint: takes project_id + optional material_ids, returns list of materials with all vendor rates
- Award flow: only COMPARED RFQs can be awarded. Awarding one RFQ for a project does not auto-close others (manual close).
- For response submission: vendor sends back rates for each item. Endpoint accepts list of {item_id, vendor_rate}.
