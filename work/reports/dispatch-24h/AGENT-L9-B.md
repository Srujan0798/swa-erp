# AGENT-L9-B

Repo: `/Users/srujansai/Desktop/swa-erp` (main). NO pytest. MAY EDIT: deliverables/TECHNICAL_REPORT.md.

## Changes made

Updated `deliverables/TECHNICAL_REPORT.md` §5–§6 with verified coverage:

### Excel chain
All 9 links mapped to source:
- Inquiry → Client: `src/backend/services/inquiry_service.py:46-188`
- Client → Project: `src/backend/services/inquiry_service.py:46-188` (convert)
- Project → SA: `src/backend/services/agreement_service.py:36-60`
- SA → Token: `src/backend/models/token.py:15-16` (tokens_used)
- Token → DocRef: `src/backend/services/document_reference.py:19-21`
- DocRef → Time: `src/backend/models/time_tracking.py:14-26`
- Time → Invoice: `src/backend/services/invoice_service.py:144-205`
- Invoice → GST: `src/backend/services/invoice_repo.py:22` (seq)
- Invoice → Compliance: `src/backend/services/compliance.py:37-64`

### GST
- 18% default (`src/backend/services/invoice_service.py:177`)
- draft→sent→paid state machine (`src/backend/services/invoice_service.py:218-227`)
- `CREATE SEQUENCE IF NOT EXISTS` (`src/backend/db/repositories/invoice_repo.py:22`)

### RBAC
- VIEWER read-only (`src/backend/lib/roles.py:17`)
- Admin bypasses IDOR (`src/backend/api/jobs.py:32-33`)
- JWT token_version logout (`src/backend/services/auth_service.py:102-106`, `deps.py:36-39`)
- Refresh rotation (`src/backend/services/auth_service.py:80-84`)

### Audit log
- Inquiry convert (`src/backend/services/inquiry_service.py:162`)
- SA create (`src/backend/services/agreement_service.py:46`)
- Invoice sent/paid (`src/backend/services/invoice_service.py:241`)

### Gaps (honest)
- vitest funcs 60.46% (borderline, below 60% threshold)
- Playwright/backend/wave coverage NOT MEASURED
- "572 tests pass" removed as stale

## Verification

All claims traceable to source lines. Removed "572 tests pass" stale claim. No fabrication.