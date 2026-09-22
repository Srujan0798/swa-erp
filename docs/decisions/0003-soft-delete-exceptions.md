# Decision: Soft-Delete Exceptions

## Status
Accepted (documenting existing state)

## Context
The codebase implements soft-delete (`deleted_at` column) on 20 of 27 model files. This decision documents which models intentionally lack soft-delete and why. (Audited 2026-09-21 against migration `0038`; matrix also lives in `docs/conventions.md`.)

## Models WITH Soft-Delete (20 files)
- Agreement
- BOQ / BOQItem
- Client
- Contact (0038)
- DocumentFolder (0038)
- DocumentReference
- Inquiry
- Invoice
- Material
- Project
- ProjectCost
- Quote
- RFQ
- SustainabilityMetric (0038)
- Task
- TimeEntry / Timesheet (time_tracking)
- Token
- User
- Vendor
- VendorContact (0038)

**Special case — Document:** deactivates via `is_active` (version chain preserved). A `deleted_at` column was deliberately REMOVED by migration `0026` — do not re-add it; the two mechanisms would compete.

## Models WITHOUT Soft-Delete (9) — Intentional Exceptions

### 1. AuditLog (`audit_log.py`)
**Rationale:** Append-only immutable log. Deletion violates audit integrity. Regulatory requirement.

### 2. ComplianceStandard / ComplianceChecklistItem (`compliance.py`)
**Rationale:** Reference/master data. Standards and checklist items are versioned, not deleted. Retired standards remain for historical project compliance records.

### 3. ProjectComplianceItem (`compliance.py`)
**Rationale:** Project-specific compliance tracking. Status field (`pending`, `reviewed`, `approved`, `waived`) captures lifecycle. Removal = data loss for certification evidence.

### 4. ExportJob (`export_job.py`)
**Rationale:** Ownership record for async exports (SEC-07). Must persist beyond Celery result TTL (1hr) to enforce ownership checks. Never deleted.

### 5. Notification (`notification.py`)
**Rationale:** User-facing notifications. Current UX: mark read, not delete. Future: add `deleted_at` if "delete notification" feature requested.

### 6. ReferenceCounter (`reference_counter.py`)
**Rationale:** System-internal sequencing. Per-year counters for reference ID generation. Never deleted; reset annually via new row.

### 7. RefreshToken (`refresh_token.py`)
**Rationale:** Uses `revoked_at` instead (different semantics). Token rotation/revocation is security event, not soft-delete. `revoked_at` enables audit trail of logout/revocation.

### 8. TaskDependency (`task_dependency.py`)
**Rationale:** Pure relationship table (many-to-many self-ref on Task). Deleting a task soft-deletes the task; dependencies cascade via FK `ondelete=CASCADE`. No independent lifecycle.

## Models Requiring Future Review
- `Notification` — if "delete notification" UX added
- `ProjectComplianceItem` — if "remove compliance item from project" workflow added

## Migration Impact
Adding `deleted_at` to existing tables requires:
1. `ALTER TABLE ... ADD COLUMN deleted_at TIMESTAMPTZ`
2. Index: `CREATE INDEX ix_<table>_deleted_at ON <table>(deleted_at) WHERE deleted_at IS NOT NULL`
3. Update repositories to filter `.filter(Model.deleted_at.is_(None))`
4. Update any raw SQL queries

## Related
- `docs/decisions/0001-tech-stack.md`
- `docs/decisions/0002-core-id-chain-gap.md`