# Task 02 — Token API

## What to do
Implement the Token model: issued against a Service Agreement, using the shared reference-ID
generator from Task 00. **Depends on Task 00 and Task 01 merging first** (`agreement_id` FK
needs the `service_agreements` table).

Reference: `.specify/specs/wave-9/spec.md` §3. Field names/format are taken directly from the
real `Tokens Sheet.xlsx`, which has actual live sample rows — this is not guessed:

```
Sr. No. | Date       | Token ID          | Agreement ID       | Token Type | Description                          | Token Status | Tokens Used | Swa Employee Name/Team Leader | Project Owner | Client Employee Name
1       | 2025-10-03 | SWA-2025-TKN-001  | SWA-2025-SA-011    | Query      | System R & U value calculation       | (blank)      | 1           | Mihir                         | (blank)        | Akash
2       | 2025-10-03 | SWA-2025-TKN-002  | SWA-2025-SA-011    | Query      | TDS & TC submission                  | (blank)      | 1           | Mihir                         | (blank)        |
3       | 2025-10-03 | SWA-2025-TKN-003  | SWA-2025-SA-011    | Design     | Submission and Thickness reports     | (blank)      | 2           | Mihir                         | (blank)        | RP
```
`Token Status` dropdown values observed elsewhere in the sheet: `In Progress`, `Closed`, `Under Review`.

**Correction from an earlier draft of this task:** Token IDs are NOT the legacy "1801/1802"
verbal format — that's superseded by `SWA-{year}-TKN-{seq:03d}`, confirmed by real data. Use
Task 00's `generate_reference_id(db, "TKN")`, don't build separate numbering logic.

## Files to create
- CREATE: `src/backend/models/token.py`
- CREATE: `src/backend/schemas/token.py`
- CREATE: `src/backend/db/repositories/token_repo.py`
- CREATE: `src/backend/services/token_service.py`
- CREATE: `src/backend/api/tokens.py`
- CREATE: `src/backend/alembic/versions/0018_add_tokens.py`
- CREATE: `tests/wave-9/test_tokens.py`

## Files to modify
- MODIFY: `src/backend/models/__init__.py`
- MODIFY: `src/backend/api/__init__.py`, `src/backend/main.py`

## Files you must NOT touch
- `src/backend/models/{inquiry,agreement}.py` (Task 01's — read-only dependency)
- `src/backend/services/reference_id_service.py` (Task 00's — call it, don't modify it)
- `src/frontend/`

## The core problem (inline)

### Token model
```python
class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)  # via reference_id_service.generate_reference_id(db, "TKN")
    agreement_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("service_agreements.id"), nullable=False, index=True)
    token_date: Mapped[date] = mapped_column(Date, nullable=False)
    token_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g. "Query", "Design" — free text, observed values not exhaustive
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_status: Mapped[str] = mapped_column(String(50), nullable=False, default="In Progress")  # In Progress / Closed / Under Review
    tokens_used: Mapped[int] = mapped_column(nullable=False, default=1)  # quantity consumed by this entry, not an identity field
    swa_employee_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    project_owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    client_employee_name: Mapped[str | None] = mapped_column(String(255), nullable=True)  # external person, not a User FK
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    created_at / updated_at: standard pattern
```
Note `tokens_used` is a plain integer count field on the sample data (values 1, 1, 2) — it is
NOT part of the ID/numbering scheme. Don't confuse it with `reference_id`'s sequence number.

### Numbering
Call `reference_id_service.generate_reference_id(db, "TKN")` from Task 00 inside the same DB
transaction as the Token insert — do not implement a second numbering mechanism.

## Acceptance criteria
- [ ] `python3 -m pytest tests/wave-9/test_tokens.py -q` passes
- [ ] `ruff check src/backend/models/token.py src/backend/services/token_service.py` clean
- [ ] POST /tokens with agreement_id → sequential `reference_id` (`SWA-{year}-TKN-{seq}`), no gaps under 20 parallel requests in test (this reuses Task 00's already-tested locking — just confirm it holds through this API layer too)

## How to deliver
1. Implement model + migration + service (thin wrapper over Task 00's generator) + API + tests
2. Run acceptance commands
3. Write report to `work/reports/wave-9/02-token-api.report.md`
4. Stop

## Constraints
- Time budget: 75 min
- Do not reimplement ID generation — call Task 00's service
- Allowed tools: file edit, pytest, ruff
