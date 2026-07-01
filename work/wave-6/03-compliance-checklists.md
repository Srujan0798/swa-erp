# Task 03 — Compliance Checklists (NBC/ECBC/IGBC/IS)

## Goal
Create compliance checklist models and CRUD API for tracking building code compliance across projects. Standards: NBC (National Building Code), ECBC (Energy Conservation Building Code), IGBC (Indian Green Building Council), IS (Indian Standards / Fire codes). Each project has compliance items linking to checklist requirements with status tracking and evidence linking.

## Files to Create / Modify

### 1. Models
Create `src/backend/models/compliance.py`:
```python
class ComplianceStandard(Base):
    __tablename__ = "compliance_standards"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)  # NBC, ECBC, IGBC, IS
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ComplianceChecklistItem(Base):
    __tablename__ = "compliance_checklist_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    standard_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("compliance_standards.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    requirement: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ProjectComplianceItem(Base):
    __tablename__ = "project_compliance_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    checklist_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("compliance_checklist_items.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending, compliant, non_compliant, na
    evidence_document_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
```

Register all three models in `src/backend/models/__init__.py`.

### 2. Schemas
Create `src/backend/schemas/compliance.py`:
- `ComplianceStandardRead` — `model_config = ConfigDict(from_attributes=True)`; id, name, version, description
- `ComplianceChecklistItemRead` — id, standard_id, category, requirement, description, is_mandatory
- `ComplianceChecklistItemCreate` — for seeding: standard_id, category, requirement, description, is_mandatory
- `ProjectComplianceItemRead` — id, project_id, checklist_item_id, status, evidence_document_id, notes, reviewed_by, reviewed_at, plus joined fields: `standard_name: str`, `category: str`, `requirement: str`, `is_mandatory: bool`
- `ProjectComplianceItemUpdate` — status: ComplianceStatus enum, evidence_document_id: uuid.UUID | None, notes: str | None
- `ProjectComplianceItemReview` — reviewed_by is set from auth; optional notes
- `ComplianceStatus(StrEnum)` — `PENDING = "pending"`, `COMPLIANT = "compliant"`, `NON_COMPLIANT = "non_compliant"`, `NA = "na"`
- `ComplianceDashboardResponse` — per-standard summary: `standard_name`, `total_items`, `compliant_count`, `non_compliant_count`, `pending_count`, `na_count`, `compliance_percentage: float`
- `ComplianceSummaryResponse` — `project_id`, `standards: list[ComplianceDashboardResponse]`, `overall_percentage: float`

### 3. Repository
Create `src/backend/db/repositories/compliance_repo.py`:
- `seed_standards(db)` — insert NBC, ECBC, IGBC, IS if not exist (idempotent)
- `seed_checklist_items(db, standard_id, items: list[dict])` — bulk insert checklist items for a standard
- `get_standards(db)` — list all standards
- `get_checklist_items_by_standard(db, standard_id)` — list checklist items
- `create_project_compliance_item(db, project_id, checklist_item_id)` — create with status=pending
- `bulk_create_project_items(db, project_id, standard_id)` — create ProjectComplianceItems for all checklist items of a standard
- `get_project_compliance_items(db, project_id, standard_id=None)` — list with optional filter
- `get_project_compliance_item(db, item_id)` — get single item
- `update_project_compliance_item(db, item_id, **kwargs)` — update status, evidence, notes
- `review_project_compliance_item(db, item_id, reviewed_by)` — set reviewed_by, reviewed_at
- `get_compliance_summary(db, project_id)` — aggregate counts per standard
- `get_checklist_item_by_id(db, checklist_item_id)` — return ComplianceChecklistItem

### 4. Service
Create `src/backend/services/compliance_service.py`:
- `initialize_compliance(db)` — call seed_standards, then seed checklist items for each standard (provide a reasonable default set of 5-10 items per standard covering key requirements)
- `get_standards(db)` — return all standards
- `get_checklist_items(db, standard_id)` — return items for a standard
- `create_project_compliance_item(db, project_id, checklist_item_id)` — create, audit log "compliance.item_created"
- `update_compliance_item_status(db, item_id, status, evidence_document_id, notes)` — update, audit log "compliance.status_changed"
- `review_compliance_item(db, item_id, reviewed_by, notes=None)` — set reviewed_by + reviewed_at, audit log "compliance.reviewed"
- `get_compliance_summary(db, project_id)` — compute ComplianceSummaryResponse with percentages
- `get_project_items(db, project_id, standard_id=None)` — return list with joined data

### 5. API
Create `src/backend/api/compliance.py`:
- `POST /api/compliance/initialize` — seed standards + checklist items (admin only, idempotent)
- `GET /api/compliance/standards` — list standards
- `GET /api/compliance/standards/{standard_id}/checklist` — list checklist items
- `POST /api/projects/{project_id}/compliance/items` — create compliance item (body: `checklist_item_id`)
- `POST /api/projects/{project_id}/compliance/items/bulk/{standard_id}` — create all items for a standard
- `GET /api/projects/{project_id}/compliance/items` — list project items, optional `standard_id` filter
- `PATCH /api/compliance/items/{item_id}` — update status/evidence/notes
- `POST /api/compliance/items/{item_id}/review` — reviewer approves/rejects (require auditor role)
- `GET /api/projects/{project_id}/compliance/summary` — compliance dashboard data

Register router in `src/backend/main.py`.

### 6. Migration
Create `src/backend/alembic/versions/0011_add_compliance.py`:
- Create `compliance_standards` table
- Create `compliance_checklist_items` table
- Create `project_compliance_items` table
- Seed initial standards: NBC, ECBC, IGBC, IS

## Files you must NOT touch
- `src/backend/models/document.py` — from task 01, read-only dependency
- `src/frontend/` — frontend is task 04
- `tests/wave-6/test_document_upload.py` — task 01 tests

## Skills to use
- `tdd` — red → green → refactor
- `code-review` — self-review before declaring done

## The core problem (inline — no external context needed)
Compliance tracking links projects to building code requirements. There are 4 standards (NBC, ECBC, IGBC, IS), each with a checklist of requirements. Each project tracks which requirements are compliant, non-compliant, pending, or N/A. Evidence is linked to uploaded documents. An auditor reviews and approves/rejects compliance items.

### Default checklist items to seed (5-10 per standard)
**NBC:** Structural safety, Fire safety, Accessibility, Ventilation, Sanitation, Lighting, Rainwater harvesting, Staircase width
**ECBC:** Envelope performance, HVAC efficiency, Lighting power density, Water heating, Building energy rating
**IGBC:** Energy efficiency, Water conservation, Materials, Indoor environment quality, Site planning
**IS:** Fire resistance, Exit provisions, Smoke control, Fire extinguisher placement, Emergency lighting

### Edge cases to handle
- Initialize called twice → idempotent (skip if standards exist)
- Create compliance item for checklist_item that doesn't exist → 404
- Create duplicate compliance item (same project + checklist_item) → 409
- Review by non-auditor user → 403
- Update status of already-reviewed item → allow (re-review)

## Acceptance criteria (executable, not prose)
- [ ] `pytest tests/wave-6/test_compliance.py` passes
- [ ] POST /compliance/initialize creates 4 standards and their checklist items
- [ ] Can create project compliance items per standard
- [ ] Status update works: pending → compliant/non_compliant/na
- [ ] Review endpoint sets reviewed_by and reviewed_at
- [ ] Summary endpoint returns correct counts and percentages
- [ ] Duplicate compliance item returns 409
- [ ] `ruff check src/backend/` clean
- [ ] `alembic upgrade head` creates all 3 tables

## Test file
Create `tests/wave-6/test_compliance.py` with at least:
- `test_initialize_compliance` — call initialize, verify 4 standards created
- `test_get_standards` — list standards, verify 4 returned
- `test_get_checklist_items` — get NBC items, verify list non-empty
- `test_create_project_compliance_item` — create item, verify status=pending
- `test_update_compliance_status` — update to compliant, verify
- `test_review_compliance_item` — review, verify reviewed_by set
- `test_compliance_summary` — create items, update some, verify summary counts
- `test_duplicate_compliance_item` — create same item twice, expect 409
- `test_initialize_idempotent` — call initialize twice, no error, same count

## How to deliver
1. Implement models, schemas, repo, service, API, migration
2. Run `pytest tests/wave-6/test_compliance.py`
3. Run `ruff check src/backend/`
4. Write report to `work/reports/wave-6/03-compliance-checklists.report.md`
5. Use `work/REPORT_TEMPLATE.md`
6. Stop

## Constraints
- Time budget: 25 min
- No new dependencies without flagging
- Match existing patterns (see `src/backend/models/project.py`, `src/backend/schemas/project.py`)
- Allowed tools: Read, Edit, Write, Bash, Glob, Grep
