# Task 01 — Inquiry + Service Agreement API + Client model patch

## What to do
Implement Inquiry and ServiceAgreement, and patch the already-shipped Client model, which is
missing fields the client's real data requires. Implement the conversion flow EXACTLY as
described by the client in the raw transcript (see below) — this is not a blind "always create a
new Client" flow.

Reference: `.specify/specs/wave-9/spec.md` §1-2, `docs/decisions/0002-core-id-chain-gap.md`
items #2, #3, #6. **Depends on Task 00 (shared ID generator) merging first.**

## Files to create
- CREATE: `src/backend/models/inquiry.py`
- CREATE: `src/backend/models/agreement.py`
- CREATE: `src/backend/schemas/inquiry.py`
- CREATE: `src/backend/schemas/agreement.py`
- CREATE: `src/backend/db/repositories/inquiry_repo.py`
- CREATE: `src/backend/db/repositories/agreement_repo.py`
- CREATE: `src/backend/services/inquiry_service.py` (includes `convert_inquiry` — see flow below)
- CREATE: `src/backend/services/agreement_service.py`
- CREATE: `src/backend/api/inquiries.py`
- CREATE: `src/backend/api/agreements.py`
- CREATE: `src/backend/alembic/versions/0016_add_inquiries_and_agreements.py`
- CREATE: `src/backend/alembic/versions/0017_patch_client_fields.py` (adds columns to existing `clients` table — see below)
- CREATE: `tests/wave-9/test_inquiries.py`
- CREATE: `tests/wave-9/test_agreements.py`

## Files to modify
- MODIFY: `src/backend/models/__init__.py` — import Inquiry, ServiceAgreement
- MODIFY: `src/backend/models/client.py` — ADD these columns (nullable, so it's a safe additive
  migration on an existing shipped table):
  - `industry: Mapped[str | None] = mapped_column(String(100), nullable=True)`
  - `client_status: Mapped[str] = mapped_column(String(50), nullable=False, default="Active")`
  - `first_lead_id: Mapped[str | None] = mapped_column(String(30), nullable=True)` — free text,
    may hold a legacy `LDI-*` value on imported rows, see ADR-0002 item #6
  - `first_inquiry_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("inquiries.id"), nullable=True)`
  - Do NOT touch `code` (existing unique field) — this stays as-is, `first_inquiry_id`/`first_lead_id` are additive, not a replacement ID scheme for Client itself. (Client's own `id`/`code` are unaffected; only the *display* reference for new clients optionally adopts `SWA-{year}-CLT-{seq}` via Task 00's generator when created through the Inquiry conversion flow — store it in `code` if `code` is otherwise auto-generated, or add a `reference_id` column if `code` already means something else — check `client.py`'s actual current usage of `code` before deciding, don't blindly overwrite its semantics)
- MODIFY: `src/backend/api/__init__.py`, `src/backend/main.py` — mount both new routers

## Files you must NOT touch
- `src/backend/api/auth.py`, `src/backend/api/users.py`
- `src/backend/models/project.py` (Project creation is called by this task's conversion flow,
  but the Project model itself is out of scope here — use the existing `project_service.create_project`)
- `src/frontend/` (Task 04)

## The core problem (inline)

### Inquiry model
```python
class Inquiry(Base):
    __tablename__ = "inquiries"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)  # SWA-{year}-INQ-{seq}, via Task 00
    inquiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    inquiry_type: Mapped[str | None] = mapped_column(String(50), nullable=True)   # e.g. "Design"
    inquiry_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)  # free-text name as entered pre-conversion
    requirement_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)  # High/Medium/Low
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="New")  # New/Contacted/Converted/Dropped
    owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    technical_lead_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    converted_client_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True)
    converted_project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    created_at / updated_at / deleted_at: standard pattern (see models/client.py)
```
Field names/types are taken directly from the real `Inquiries Sheet.xlsx` header row: `Sr No,
Inquiry ID, Inquiry Date, Inquiry Type, Inquiry Source, Client Name, Requirement Summary,
Estimated Value, Priority, Status, Owner, Technical Lead, Notes`.

### ServiceAgreement model
```python
class ServiceAgreement(Base):
    __tablename__ = "service_agreements"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)  # SWA-{year}-SA-{seq}
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    inquiry_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("inquiries.id"), nullable=True)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)  # free-text, NOT an enum — see ADR-0002 open item #1, the 4th agreement type is still unconfirmed
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(nullable=True)  # nullable — real sample data has "N/A"
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Active")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at / updated_at / deleted_at: standard pattern
```
Field names taken from real `Service Agreements Sheet.xlsx`: `Sr No, Agreement ID, Client Name,
Client ID, Inquiry ID, Service Name, Start Date, End Date, Total Tokens, Status, Notes`.
**`service_name` is free text — do not hardcode "IESK/APEX/Inner Engineering" as an enum.** The
real sample row's Service Name value is `"INSUDESIGN"`, which doesn't match the verbally-named
list at all — confirms the enum approach would already be wrong on day one.

### Conversion flow — implement exactly this, from the client's own words (Meeting 2 transcript)
> "we inquire the first time into the system, then if the inquiry converts, then we go into the
> client database, check if the client already exists. If the client exists, we go to the
> project and add the project, and the inquiry got converted into a project. And if the client
> does not exist, we first add the client details and then go to the project and add the project."

`POST /inquiries/{id}/convert` body: `{ "project_name": str, ... project fields }`
1. Look up an existing Client by name match against `Inquiry.client_name` (exact match first;
   if none, this is a genuine ambiguity — surface a 300-style "multiple/no match, confirm" response
   rather than silently fuzzy-matching and picking wrong).
2. If a Client match is confirmed (either exact-matched or explicitly passed as `client_id` in
   the request body to disambiguate) → skip client creation, go straight to step 4.
3. If no Client exists → create one via the existing `client_service.create_client`, populating
   `first_inquiry_id` = this Inquiry's id.
4. Create a Project via the existing `project_service.create_project`, linked to the resolved
   Client.
5. Set `Inquiry.status = "Converted"`, `converted_client_id`, `converted_project_id`.
6. Reject (409) if `Inquiry.status == "Converted"` already — don't double-convert.

### Edge cases
- ServiceAgreement `end_date` before `start_date` → 422
- Ambiguous client-name match on convert (e.g. two clients named "Acme") → 300-style response
  listing candidates, require `client_id` to disambiguate, don't guess

## Acceptance criteria
- [ ] `python3 -m pytest tests/wave-9/test_inquiries.py tests/wave-9/test_agreements.py -q` passes
- [ ] `ruff check src/backend/models/inquiry.py src/backend/models/agreement.py` clean
- [ ] Convert flow test: existing-client case does NOT create a duplicate Client, only a Project
- [ ] Convert flow test: no-existing-client case creates both Client and Project, Client gets `first_inquiry_id` set
- [ ] Migration `0017_patch_client_fields.py` applies cleanly on top of existing `clients` table without data loss

## How to deliver
1. Implement models + 2 migrations + repos + services + API + tests
2. Run acceptance commands
3. Write report to `work/reports/wave-9/01-inquiry-agreement-api.report.md`
4. Stop

## Constraints
- Time budget: 100 min
- No new dependencies
- Match existing patterns in `models/client.py`, `api/clients.py`, `services/client_service.py`, `services/project_service.py`
- Allowed tools: file edit, pytest, ruff
