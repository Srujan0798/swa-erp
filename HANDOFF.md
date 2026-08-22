# Handoff Protocol

> **Role:** Session / orchestrator-switching protocol. Part of the front-door set — start at
> [README.md](README.md).

## Current state (2026-08-23 — INDUSTRY-HARDENED)

- **Product:** **v1.0.1** feature-complete (waves 1–31).
- **Professional-grade track (waves 32–39):** **ALL SHIPPED**.
- **Industry hardening (post-seal):** Meeting-fidelity pass complete.
  - Front-door metrics corrected (no stale “5 failed”)
  - Time/finance/document RBAC aligned to Meeting 1 matrix
  - `/metrics` requires auth; failed-login counter wired; import fatal rollback zeros counts
  - Alignment map: [`work/reports/industry-hardening/00-ALIGNMENT.md`](work/reports/industry-hardening/00-ALIGNMENT.md)
- **Seal:** [`work/reports/FINAL-CLOSE.report.md`](work/reports/FINAL-CLOSE.report.md)
- **Truth hierarchy:** MEETINGS + ADRs → code/tests → README → MASTER-FLOW → HANDOFF

### Verified (industry pass)
- Backend: **566 passed / 0 failed / 1 skipped**
- Frontend: **522 passed / 0 failed**
- Wave-9 chain tests: **81 passed**; no Lead ID in models/schemas

### External (not engineering)
- Viraj / no IT dept — server facts + deploy (`docs/INSTALL_NO_IT.md`)
- Excel migration owner — Viraj decides
- Do **not** re-blast SEND_IT / SEND_VIRAJ

### Where to start a new session
1. This file → deploy/import help only unless a bug is reported  
2. `README.md` for evaluator view  
3. `MASTER-FLOW.md` for the one ops path  

## Open decisions
- Server/deploy 8 facts — Viraj (external)  
- Excel freeze + migration owner — Viraj (external)
