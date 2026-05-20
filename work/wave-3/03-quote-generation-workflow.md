# Task 03 — Quote Generation & Approval Workflow

## Goal
Create the Quote model, generation service, and approval status machine. A quote is generated from a BOQ version and goes through a full approval workflow.

## Files to Create/Modify

### 1. Models
Create `src/backend/models/quote.py`:
```python
class Quote(Base):
    __tablename__ = "quotes"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    boq_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("boqs.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    markup_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0"))
    markup_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    tax_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("18"))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    validity_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    client_response: Mapped[str | None] = mapped_column(String(50), nullable=True)
    client_response_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    client_response_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class QuoteItem(Base):
    __tablename__ = "quote_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quotes.id"), nullable=False, index=True)
    boq_item_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("boq_items.id"), nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    specification: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
```

Register in `src/backend/models/__init__.py`.

### 2. Status Machine
Create `src/backend/core/quote_workflow.py`:
```python
VALID_TRANSITIONS = {
    "draft": ["pending_approval"],
    "pending_approval": ["approved", "draft"],
    "approved": ["sent", "draft"],
    "sent": ["accepted", "rejected"],
    "rejected": ["draft"],  # can revise
    "accepted": [],  # terminal
}

def can_transition(from_status: str, to_status: str) -> bool: ...
def get_allowed_transitions(status: str) -> list[str]: ...
```

### 3. Schemas
Create `src/backend/schemas/quote.py`:
- `QuoteItemCreate`, `QuoteItemRead`
- `QuoteCreate` — requires `boq_id`, optional `markup_percent`, `tax_percent`, `terms`, `validity_days`
- `QuoteUpdate` — editable only in draft; `markup_percent`, `tax_percent`, `terms`, `validity_days`, `items` (list of overrides)
- `QuoteRead` — full quote with items, creator name, approver name, project name, client name
- `QuoteListResponse`
- `QuoteSubmitRequest`, `QuoteApproveRequest`, `QuoteSendRequest`, `QuoteRespondRequest`

### 4. Repository
Create `src/backend/db/repositories/quote_repo.py`:
- `create_quote(db, data, items)` — creates quote + quote_items
- `get_by_id(db, quote_id)` — with items
- `list_by_project(db, project_id, page, page_size)` — paginated
- `update_quote(db, quote_id, data)` — update fields + recalc totals
- `update_status(db, quote_id, status, **kwargs)` — e.g. approved_by, approved_at
- `soft_delete(db, quote_id)`
- `clone_quote(db, quote_id, new_quote_id)` — copy items to new quote

### 5. Service
Create `src/backend/services/quote_service.py`:
- `generate_quote(db, project_id, boq_id, markup_percent, tax_percent, terms, validity_days, created_by)`:
  1. Fetch BOQ with items
  2. Create QuoteItems from BOQItems (copy rates)
  3. Calculate subtotal = sum(item.amount)
  4. Calculate markup_amount = subtotal * markup_percent / 100
  5. Calculate tax_amount = (subtotal + markup_amount) * tax_percent / 100
  6. Calculate total = subtotal + markup_amount + tax_amount
  7. valid_until = today + validity_days
  8. Create Quote + QuoteItems
  9. Audit log: "quote.create"
  10. Return QuoteRead

- `recalculate_totals(quote)` — recompute subtotal, markup, tax, total
- `submit_for_approval(db, quote_id, actor_id)` — draft → pending_approval
- `approve(db, quote_id, actor_id)` — pending → approved
- `send(db, quote_id, actor_id)` — approved → sent
- `record_response(db, quote_id, response, notes)` — sent → accepted/rejected
- `clone_to_draft(db, quote_id, actor_id)` — rejected → new draft quote

### 6. Migration
Create `src/backend/alembic/versions/0005_add_quotes.py`

## Acceptance Criteria
- [ ] Can generate a quote from a BOQ version with correct totals
- [ ] Quote items mirror BOQ items with copied rates
- [ ] Totals recalculate correctly when markup/tax changes
- [ ] Status transitions enforce the state machine
- [ ] Audit log records every transition
- [ ] `pytest tests/wave-3/test_quote_workflow.py` passes

## Test File
Create `tests/wave-3/test_quote_workflow.py` with at least:
- `test_generate_quote` — create quote, verify totals
- `test_quote_totals_with_markup` — 15% markup, verify math
- `test_quote_totals_with_tax` — 18% GST, verify math
- `test_submit_for_approval` — draft → pending
- `test_approve_quote` — pending → approved
- `test_send_quote` — approved → sent
- `test_accept_quote` — sent → accepted
- `test_reject_quote` — sent → rejected
- `test_clone_rejected_quote` — rejected → new draft
- `test_invalid_transition` — trying draft → sent returns 400
- `test_only_admin_can_approve` — pm submitting gets 403 on approve
- `test_edit_only_in_draft` — trying to edit approved quote returns 400

## Notes
- Decimal math: `subtotal = sum(item.amount for item in items)`
- `markup_amount = (subtotal * markup_percent / Decimal("100")).quantize(Decimal("0.01"))`
- `tax_amount = ((subtotal + markup_amount) * tax_percent / Decimal("100")).quantize(Decimal("0.01"))`
- `total = (subtotal + markup_amount + tax_amount).quantize(Decimal("0.01"))`
- Use `round_half_even` or `ROUND_HALF_UP` consistently
- `valid_until = date.today() + timedelta(days=validity_days)`
