# Wave 22 — Gotchas

> **Source:** Harvested from `work/reports/wave-22/01-critical-rbac-and-auth-gaps.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### Core-chain RBAC matrix matches client access matrix
RBAC matrix: PM+Designer for DBR/KDR, Auditor+Designer for Reforge. Compliance-review and task/RFQ transitions are gated. Materials endpoints are authenticated, financial modules (project_pnl/exports/invoice-status) are role-gated.

### Documentation-drift risk in RBAC
RBAC decisions are scattered across ADR-0002, MEETINGS_MASTER, and EXECUTION.md. When changing access rules, check all three — they can diverge.

### Wave-9 ID chain is foundational
The core ID chain (Inquiry/Agreement/Token/DocRef) from wave-9 is the foundation RBAC builds on. Don't modify reference-ID generation without checking RBAC implications.
