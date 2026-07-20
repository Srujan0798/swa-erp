# Task 01 — Critical RBAC and auth gaps (found by 2026-07-21 full-project audit)

## What to do
A 4-agent traceability audit (2026-07-21) read every backend module line-by-line against
`resources/MEETINGS_MASTER.md`'s actual access-control matrix and found real, confirmed security
gaps. Fix them exactly as specified below — every finding has a file:line citation, don't re-derive
from scratch, verify then fix.

## Files to modify
- MODIFY: `src/backend/api/materials.py`
- MODIFY: `src/backend/api/project_pnl.py`
- MODIFY: `src/backend/api/exports.py`
- MODIFY: `src/backend/api/invoices.py`
- MODIFY: `src/backend/api/inquiries.py`
- MODIFY: `src/backend/api/document_references.py`
- MODIFY: `src/backend/api/compliance.py`
- MODIFY: `src/backend/api/tasks.py`
- MODIFY: `src/backend/api/rfqs.py`
- CREATE/MODIFY: `tests/wave-22/test_rbac_gaps.py`

## Files you must NOT touch
- Any model, schema, or service file — these are router-level `Depends(...)` fixes only, no
  business logic or data model changes needed for this task
- `src/backend/core/roles.py`, `src/backend/core/deps.py` — the role hierarchy and
  `require_role`/`role_includes` mechanism already work correctly, don't change them, just use
  them correctly at each router

## The core problem (inline)

### 1. Genuinely unauthenticated endpoints — highest severity
`src/backend/api/materials.py:53-58` (`GET /api/material-categories`), `:116-130`
(`GET /api/materials`), `:133-141` (`GET /api/materials/{material_id}`) have **no auth dependency
at all** — not even `Depends(get_current_user)`. Anyone with network access can read the full
pricing catalog unauthenticated. Add `current_user: User = Depends(get_current_user)` to all
three (read access for any authenticated user is fine — these don't need role restriction, just
authentication).

### 2. Zero role enforcement on financial modules
`src/backend/api/project_pnl.py` (all 5 endpoints, lines 26-75) and `src/backend/api/exports.py`
(all 4 endpoints, whole file) only require `get_current_user` — any VIEWER can create/delete
project cost entries, view P&L, and download financial PDFs. Per the access matrix
(`resources/MEETINGS_MASTER.md` §Meeting 1 section 4: "Finance Sheet — Founder only" → Admin
only in RBAC), these need role gating:
- `project_pnl.py`: reads (summary, list costs, cost breakdown) → `Role.PM` (PM+ can see their
  own project's financials); writes (add cost, delete cost) → `Role.ADMIN`
- `exports.py`: all 4 endpoints (`summary.pdf`, `financial.pdf`, `slides.pdf`, `demo.json`) →
  `Role.PM` minimum; if `financial.pdf` specifically pulls raw financial data, consider
  `Role.ADMIN` for that one specifically — use judgment, but do not leave it at VIEWER-accessible

### 3. Invoice status mutation has no role gate
`src/backend/api/invoices.py:115-119`, `PATCH /invoices/{invoice_id}/status` (marks
sent/paid) only requires `get_current_user`. Add `Depends(require_role(Role.PM))` — matches the
role already required for invoice creation/generation in the same file.

### 4. Core chain RBAC doesn't match the client's access matrix
Per `resources/MEETINGS_MASTER.md` §Meeting 1 section 4:
- Segmentation/lead entry (Inquiry) → **PM, Designer**
- DBR/KDR generation → **PM, Designer**
- Reforge/DPR → **Auditor, Designer**

Currently `src/backend/api/inquiries.py:54` (create) requires `Role.PM` only — Designer gets
403. Fix: the create endpoint should accept PM OR Designer. Check how `require_role` is used
elsewhere for multi-role acceptance (there may already be a pattern for "any of these roles" —
if not, the simplest fix is a small dependency function accepting a list of acceptable roles,
matching the existing `require_role` style/location in `core/deps.py`... but per the "files you
must NOT touch" list above, do NOT modify `core/deps.py` itself — if a multi-role check doesn't
already exist there, implement the OR-logic inline in the router file instead, e.g. a local
dependency function in `inquiries.py`/`document_references.py` that checks
`current_user.role in {Role.PM, Role.DESIGNER}` directly).

`src/backend/api/document_references.py:64` (create) currently applies one blanket PM-only gate
regardless of `document_type` — there is no type-conditional access control. Fix: branch on the
request's `document_type` field:
- `document_type` in `{"DBR", "KDR"}` → require PM or Designer
- `document_type` == `"Reforge"` (case-insensitive match, check how document_type values are
  actually cased elsewhere in this codebase before hardcoding) → require Auditor or Designer
- any other `document_type` → keep existing PM-only gate as the safe default (this task only
  needs to correctly implement the two cases the matrix explicitly names, not invent rules for
  every possible document_type)

### 5. Compliance review role mismatch
`src/backend/api/compliance.py:89`, `review_item` requires `Role.AUDITOR` only. Per the matrix,
Reforge/DPR review should also accept Designer. Because `role_includes` hierarchy means
`ROLE_HIERARCHY[Role.DESIGNER] = {DESIGNER, VIEWER}` (doesn't include AUDITOR), a Designer
currently gets 403. Same OR-logic fix as item 4: accept AUDITOR or DESIGNER for this endpoint.

### 6. Task/RFQ transition endpoints have no role gate at all
Systemic pattern found across `tasks.py` (transition/reorder/comments, lines 121-134, 187-191)
and `rfqs.py` (send/respond/compare/close/cancel, lines 106,122,138,168,183) — only
`get_current_user`, letting VIEWER-role accounts perform state-mutating actions. Add
`Depends(require_role(Role.PM))` to all of these — matches the role already required for the
adjacent create/award endpoints in the same files.

## Acceptance criteria
- [ ] All materials read endpoints require authentication (401 for unauthenticated requests, was previously 200)
- [ ] VIEWER role gets 403 on project_pnl writes, exports, invoice status change, task
  transition/reorder, RFQ send/respond/compare/close/cancel (all previously allowed)
- [ ] Designer role gets 200 (not 403) creating an Inquiry
- [ ] Designer role gets 200 (not 403) creating a DBR/KDR DocumentReference
- [ ] Auditor OR Designer role gets 200 (not 403) creating a Reforge DocumentReference
- [ ] Auditor OR Designer role gets 200 (not 403) on compliance item review
- [ ] `python3 -m pytest tests/ -q` — 324+ pass, including new tests in `tests/wave-22/` —
  **run with no other pytest process active and a freshly reset test DB** (`DROP DATABASE
  swa_erp_test; CREATE DATABASE swa_erp_test;` if in doubt) — this suite produces false failures
  under process/DB contention, confirmed multiple times this session, see
  `docs/PROJECT_HISTORY.md`
- [ ] `ruff check` on all touched files — clean

## How to deliver
1. Fix all 6 items
2. Write `tests/wave-22/test_rbac_gaps.py` covering every positive AND negative case above
   (both "role X succeeds" and "role Y gets 403") — the audit specifically found that prior
   waves only tested the negative case, never the positive Designer/Auditor success case; don't
   repeat that gap
3. Run every acceptance check
4. Write report to `work/reports/wave-22/01-critical-rbac-and-auth-gaps.report.md`
5. Stop

## Constraints
- Time budget: 100 min
- Don't touch `core/roles.py` or `core/deps.py` — work within the existing mechanism
- Allowed tools: file edit, pytest, ruff, curl
