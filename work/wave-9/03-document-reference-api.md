# Task 03 — Document Reference API (DRN)

## What to do
Implement DocumentReference: a numbered document issued against a Project (required) and
optionally a Token. **Depends on Task 00, and on Task 02 (Token) for the optional `token_id` FK.**

Reference: `.specify/specs/wave-9/spec.md` §4, `docs/decisions/0002-core-id-chain-gap.md` items
#4, #5.

**Correction from an earlier draft of this task:** it originally linked DocumentReference to
`token_id` only. The real `Document Reference Sheet.xlsx` has two conflicting header rows in the
same file — one says the FK is `Associated Project ID`, another says `Associated Project/Token
ID` — and the actual sample row's data doesn't cleanly resolve which. Rather than guess again,
model both FKs: `project_id` required, `token_id` nullable.

## Files to create
- CREATE: `src/backend/models/document_reference.py`
- CREATE: `src/backend/schemas/document_reference.py`
- CREATE: `src/backend/db/repositories/document_reference_repo.py`
- CREATE: `src/backend/services/document_reference_service.py`
- CREATE: `src/backend/api/document_references.py`
- CREATE: `src/backend/alembic/versions/0019_add_document_references.py`
- CREATE: `tests/wave-9/test_document_references.py`

## Files to modify
- MODIFY: `src/backend/models/__init__.py`
- MODIFY: `src/backend/api/__init__.py`, `src/backend/main.py`

## Files you must NOT touch
- `src/backend/models/{document,compliance}.py` — wave-6's generic file-upload Document model,
  a DIFFERENT thing from DocumentReference (a numbered reference record, not a file). Coexist,
  don't merge.
- `src/frontend/`

## The core problem (inline)

### DocumentReference model
Field list taken directly from the real `Document Reference Sheet.xlsx` header row: `Sr. No.,
Date, DRN, Associated Project ID, Author, Document Type, Type, User, Description, Revision,
Status, Remarks`. Column meanings (from the sheet's own "Meaning" row):
- `DRN` = "Unique document number" (primary key, our `reference_id`)
- `Document Type` = "Nature of document" (dropdown) — sample value `"Concept Note"`; Meeting 1's
  verbal walkthrough also mentions `DBR`, `KDR` (shared counter with DBR), `GED` (GA drawing),
  `PRN`, `CON` as short codes — treat as free text, not a hardcoded enum, there are clearly more
  categories than the summary implied
- `Type` = "Submittal / Internal / Revision" (a separate dropdown from Document Type)
- `User` = "Client / Reviewer / Authority" per the sheet's own meaning row (despite the one
  sample row putting a person's full name there — model as free text)
- `Revision` = "Rev no. (R0, R1…)"
- `Status` = "Approval state"

```python
class DocumentReference(Base):
    __tablename__ = "document_references"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)  # DRN, via reference_id_service
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    token_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=True, index=True)
    doc_date: Mapped[date] = mapped_column(Date, nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # free text: "Concept Note", "DBR", "KDR", "GED", "PRN", ...
    type_: Mapped[str | None] = mapped_column("type", String(50), nullable=True)  # "Submittal" / "Internal" / "Revision"
    author_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)  # "Client / Reviewer / Authority", free text
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    revision: Mapped[str] = mapped_column(String(10), nullable=False, default="R0")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Draft")
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at / updated_at: standard pattern
```

### Numbering: DBR/KDR share a counter (confirmed by Meeting 1 verbal transcript: *"if it is KDR,
then we'll also put 139... number is continuous"*). Reforge and other document types do not
share that counter. Implementation: call `reference_id_service.generate_reference_id(db,
entity_type)` where `entity_type` is `"DBR"` for BOTH DBR and KDR document types (so they draw
from the same counter row), and the actual `document_type` free-text field on the record still
correctly says "DBR" or "KDR" — the counter key and the display label are decoupled. Any other
`document_type` value gets its own counter keyed by its own short code.

### Edge cases
- `project_id` must reference an existing Project — 422 if not found
- Creating a DBR then a KDR back-to-back yields consecutive numbers (same counter)
- Creating some other doc_type (e.g. "GED") does not consume a DBR/KDR number and vice versa

## Acceptance criteria
- [ ] `python3 -m pytest tests/wave-9/test_document_references.py -q` passes
- [ ] `ruff check src/backend/models/document_reference.py` clean
- [ ] DBR→KDR sequence test passes (shared counter)
- [ ] `token_id` is genuinely optional — creating a DocumentReference with only `project_id` succeeds

## How to deliver
1. Implement model + migration + service + API + tests
2. Run acceptance commands
3. Write report to `work/reports/wave-9/03-document-reference-api.report.md`
4. Stop

## Constraints
- Time budget: 80 min
- Reuse Task 00's numbering service, don't reinvent
- Allowed tools: file edit, pytest, ruff
