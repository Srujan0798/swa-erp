# Task 01 — Vendor Models & CRUD API

## Goal
Create the Vendor and VendorContact data models, CRUD endpoints with search and pagination, and Alembic migration. Vendors are external suppliers the company engages for materials and services.

## Files to Create/Modify

### 1. Models
Create `src/backend/models/vendor.py`:
```python
class Vendor(Base):
    __tablename__ = "vendors"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gst_number: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    pan_number: Mapped[str | None] = mapped_column(String(10), nullable=True, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class VendorContact(Base):
    __tablename__ = "vendor_contacts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
```

Register both models in `src/backend/models/__init__.py`.

### 2. Schemas
Create `src/backend/schemas/vendor.py`:
- `VendorCreate` — name, code, email, phone, address, city, state, gst_number, pan_number
- `VendorUpdate` — all fields optional
- `VendorRead` — includes id, created_at, contacts list
- `VendorListResponse` — paginated list with total, page, page_size, items
- `VendorContactCreate` — name, designation, email, phone, is_primary
- `VendorContactRead` — full contact with id

### 3. Repository
Create `src/backend/db/repositories/vendor_repo.py`:
- `create_vendor(db, data)` — creates vendor, returns VendorRead
- `get_by_id(db, vendor_id)` — returns vendor with contacts
- `get_by_code(db, code)` — unique lookup
- `list_vendors(db, page, page_size, search, is_active)` — paginated, soft-delete excluded. Search matches name, code, city, gst_number (case-insensitive LIKE)
- `update_vendor(db, vendor_id, data)` — partial update
- `soft_delete(db, vendor_id)` — set deleted_at, cascade to contacts
- `create_contact(db, vendor_id, data)` — create contact for vendor
- `list_contacts(db, vendor_id)` — all contacts for vendor
- `update_contact(db, contact_id, data)` — update contact
- `delete_contact(db, contact_id)` — hard delete contact

### 4. Service
Create `src/backend/services/vendor_service.py`:
- `create_vendor(db, data, created_by)` — create vendor + audit log "vendor.create"
- `update_vendor(db, vendor_id, data, updated_by)` — update + audit log "vendor.update"
- `get_vendor(db, vendor_id)` — return vendor with contacts
- `list_vendors(db, page, page_size, search, is_active)` — paginated list
- `delete_vendor(db, vendor_id, deleted_by)` — soft delete + audit log "vendor.delete"
- `add_contact(db, vendor_id, data)` — add contact
- `update_contact(db, contact_id, data)` — update contact
- `remove_contact(db, contact_id)` — delete contact

### 5. API
Create `src/backend/api/vendors.py`:
- `POST /api/vendors` — create vendor (require admin or PM role)
- `GET /api/vendors` — list vendors, query params: page, page_size, search, is_active
- `GET /api/vendors/{vendor_id}` — get vendor with contacts
- `PUT /api/vendors/{vendor_id}` — update vendor
- `DELETE /api/vendors/{vendor_id}` — soft delete vendor
- `POST /api/vendors/{vendor_id}/contacts` — add contact
- `GET /api/vendors/{vendor_id}/contacts` — list contacts
- `PUT /api/vendors/{contacts_id}` — update contact
- `DELETE /api/vendors/{contact_id}` — delete contact

Register router in `src/backend/main.py` with prefix `/api/vendors`.

### 6. Migration
Create `src/backend/alembic/versions/0007_add_vendors.py` — creates `vendors` and `vendor_contacts` tables.

## Files you must NOT touch
- `src/backend/models/client.py`
- `src/backend/models/project.py`
- `src/backend/main.py` (only add router import + include)

## Acceptance Criteria
- [ ] `pytest tests/wave-5/test_vendors.py` passes
- [ ] `make lint` clean (ruff + eslint)
- [ ] Can create a vendor, list vendors, search by name, update, soft-delete
- [ ] Can add multiple contacts to a vendor, mark one as primary
- [ ] Vendor code is unique; duplicate returns 409
- [ ] GST/PAN unique constraints enforced
- [ ] Soft-deleted vendors excluded from list queries
- [ ] Pagination works: page, page_size, total count returned
- [ ] Audit log entries written for create/update/delete

## Test File
Create `tests/wave-5/test_vendors.py` with at least:
- `test_create_vendor` — create vendor, verify fields
- `test_create_vendor_duplicate_code` — expect 409
- `test_list_vendors_search` — create 3 vendors, search by name returns correct subset
- `test_list_vendors_pagination` — page_size=2, verify total and items
- `test_update_vendor` — update name and city
- `test_soft_delete_vendor` — delete, verify excluded from list
- `test_add_vendor_contact` — add contact, verify is_primary
- `test_update_vendor_contact` — update contact designation
- `test_delete_vendor_contact` — remove contact
- `test_get_vendor_includes_contacts` — verify contacts in response

## Notes
- Match patterns from wave-2 Client/Contact models (see `src/backend/models/client.py`)
- Use `UUID(as_uuid=True)` for all PKs/FKs
- Search is case-insensitive LIKE: `Vendor.name.ilike(f"%{search}%")`
- Code generation: if not provided, auto-generate from name (e.g., first 3 chars uppercase + sequence)
