# Task 03 — Invoice Generation from Project

## Goal
Create `Invoice` and `InvoiceItem` models, schemas, repository, service, and API for generating invoices from billable time entries or project quotes. Invoices track billing status (draft → sent → paid) and financial totals.

Reference spec: `.specify/specs/wave-7/spec.md` section Invoicing.

## Files to Create / Modify

### CREATE: `src/backend/models/invoice.py`
```python
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.db.base import Base


class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("18.00"))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    due_date: Mapped[date | None] = mapped_column(date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "time", "material", "vendor", "other"
    time_entry_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)  # link to time_entry if from time tracking
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

### MODIFY: `src/backend/models/__init__.py`
Add imports for `Invoice` and `InvoiceItem`.

### CREATE: `src/backend/schemas/invoice.py`
- `InvoiceItemCreate` — description, quantity, rate, category, time_entry_id (optional)
- `InvoiceItemRead` — full model
- `InvoiceCreate` — project_id, due_date (optional), notes (optional), tax_rate (default 18%)
- `InvoiceGenerateFromTime` — project_id, start_date, end_date (generates invoice from billable entries in range)
- `InvoiceRead` — full model with project_name, created_by_name, items
- `InvoiceListResponse` — paginated list
- `InvoiceUpdateStatus` — status: "sent" | "paid"

### CREATE: `src/backend/db/repositories/invoice_repo.py`
- `create_invoice(db, data, items_data) -> Invoice` — create invoice + items in one transaction
- `get_invoice_by_id(db, invoice_id) -> Invoice | None` — with items
- `list_invoices(db, project_id, status, page, page_size) -> tuple[list, int, int, int]`
- `update_invoice_status(db, invoice_id, status, paid_at=None) -> Invoice | None`
- `generate_invoice_number(db) -> str` — auto-generate: `INV-{YYYYMM}-{sequence:04d}`
- `soft_delete_invoice(db, invoice_id) -> bool`
- `get_next_sequence_number(db, prefix: str) -> int`

### CREATE: `src/backend/services/invoice_service.py`
- `create_invoice(db, project_id, user_id, data) -> InvoiceRead`
  1. Generate invoice number
  2. Create invoice with items
  3. Compute subtotal = sum(item.amount), tax = subtotal * tax_rate / 100, total = subtotal + tax
  4. Return InvoiceRead
- `generate_from_time_entries(db, project_id, user_id, start_date, end_date) -> InvoiceRead`
  1. Fetch billable time entries in date range for project
  2. Group by user, create line items: "Design services — {user_name} — {hours}h @ {rate}/h"
  3. Rate defaults to 5000 INR/hour (configurable per project later)
  4. Create invoice with generated items
- `generate_from_quote(db, project_id, user_id, quote_id) -> InvoiceRead`
  1. Fetch BOQ items from the specified quote version
  2. Create invoice line items from BOQ items
- `update_status(db, invoice_id, status, user_id) -> InvoiceRead`
  - draft → sent → paid (forward only, no backward transitions)
  - paid: set paid_at timestamp
- `delete_invoice(db, invoice_id, user_id) -> bool` — only draft invoices can be deleted

### CREATE: `src/backend/api/invoices.py`
- `POST /api/projects/{project_id}/invoices` — create invoice
- `POST /api/projects/{project_id}/invoices/generate-from-time` — generate from time entries (body: start_date, end_date)
- `GET /api/projects/{project_id}/invoices` — list invoices for project
- `GET /api/invoices/{invoice_id}` — get invoice with items
- `PATCH /api/invoices/{invoice_id}/status` — update status (sent/paid)
- `DELETE /api/invoices/{invoice_id}` — soft delete (draft only)

### MODIFY: `src/backend/main.py`
Register invoices router.

### CREATE: `src/backend/alembic/versions/0013_add_invoices.py`
- Create `invoices` table
- Create `invoice_items` table

## Files you must NOT touch
- `src/backend/models/user.py`
- `src/backend/models/project.py`
- `src/backend/models/time_entry.py`
- `src/backend/models/timesheet.py`
- `src/backend/api/auth.py`
- `src/backend/core/security.py`

## Skills to use
- `tdd` — red → green → refactor
- `code-review` — self-review before declaring done

## The core problem (inline)

### Invoice number format
`INV-{YYYYMM}-{sequence:04d}` — e.g., `INV-202606-0001`, `INV-202606-0002`
Sequence resets monthly. Use a DB query: `SELECT MAX(sequence) FROM invoices WHERE prefix = 'INV-202606'`.

### Tax calculation
```python
subtotal = sum(item.quantity * item.rate for item in items)
tax_amount = subtotal * tax_rate / 100
total = subtotal + tax_amount
```
Store all amounts as `Decimal(18, 2)`.

### Status transitions
```
draft ──send──→ sent ──mark-paid──→ paid
  │
  └──delete──→ (deleted)
```
- Only draft can be deleted
- Only draft → sent, sent → paid
- No backward transitions

### Edge cases
- Generate from time entries with zero billable hours → 400
- Invoice number collision → regenerate
- Mark as paid when already paid → 400
- Delete non-draft invoice → 400

### Inputs available

```python
# InvoiceCreate
project_id: UUID
due_date: date | None
notes: str | None
tax_rate: Decimal = Decimal("18.00")  # GST default

# InvoiceItemCreate
description: str
quantity: Decimal
rate: Decimal
category: "time" | "material" | "vendor" | "other" | None
time_entry_id: UUID | None

# InvoiceGenerateFromTime
start_date: date
end_date: date
```

## Acceptance criteria (executable, not prose)
- [ ] `pytest tests/wave-7/test_invoicing.py` passes
- [ ] `make lint` clean
- [ ] Create invoice with items → correct subtotal, tax, total
- [ ] Invoice number auto-generates in correct format
- [ ] Generate from time entries creates items with correct amounts
- [ ] Status transitions work: draft → sent → paid
- [ ] Cannot delete non-draft invoice
- [ ] Cannot mark already-paid invoice as paid

## Test File
Create `tests/wave-7/test_invoicing.py` with at least:
- `test_create_invoice_with_items` — verify totals
- `test_invoice_number_auto_generate` — format correct
- `test_generate_from_time_entries` — items created from entries
- `test_generate_from_empty_entries` — 400 error
- `test_send_invoice` — draft → sent
- `test_mark_invoice_paid` — sent → paid, paid_at set
- `test_cannot_delete_non_draft` — 400
- `test_cannot_mark_paid_again` — 400
- `test_list_invoices_by_project` — filter works
- `test_soft_delete_invoice` — draft deleted, not in list

## How to deliver
1. Implement models, schemas, repo, service, API, migration + tests
2. Run `pytest tests/wave-7/test_invoicing.py` — all pass
3. Run `make lint` — clean
4. Write report to `work/reports/wave-7/03-invoicing.report.md`
5. Stop

## Constraints
- Time budget: 45 min
- No new dependencies without flagging
- Match existing patterns (see `src/backend/models/project.py`, `src/backend/api/projects.py`)
- Allowed tools: `ruff`, `black`, `pytest`, `alembic`
