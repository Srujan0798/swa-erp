# Handoff Protocol

> **Role:** Session / orchestrator-switching protocol. Part of the front-door set — start at
> [README.md](README.md).

## Current state (2026-08-23 — ENGINEERING CLOSED)

- **Product:** **v1.0.1** feature-complete (waves 1–31).
- **Professional-grade track (waves 32–39):** **ALL SHIPPED**.
  - 32 real CI · 33 backend 86% cov · 34 frontend Vitest · 35 load tests · 36 observability  
  - 37 adversarial review (critical fixes landed; RISKs documented)  
  - 38 submission package (README / ARCHITECTURE / TECHNICAL_REPORT / SUBMISSION / DEMO)  
  - 39 repo organization  
- **Seal:** [`work/reports/FINAL-CLOSE.report.md`](work/reports/FINAL-CLOSE.report.md)  
- **Close pack:** [`work/FINAL-CLOSE/`](work/FINAL-CLOSE/)  
- **Live wave table:** [`work/ACTIVE.md`](work/ACTIVE.md)

### Verified this close
- Backend: **565 passed / 0 failed / 1 skipped**
- Frontend: **522 passed / 0 failed**
- Critical fixes: LocalStorage path containment; hourly rate from settings; insecure SECRET_KEY denylist; `/readyz` alembic stamp in tests; TaskCard IST flake; vitest in CI

### External (not engineering)
- Viraj / no IT dept — server facts + deploy when free (`docs/INSTALL_NO_IT.md`)
- Excel migration owner — Viraj decides
- Do **not** re-blast SEND_IT / SEND_VIRAJ

### Where to start a new session
1. This file → if closed, only help with deploy/import or bugfixes  
2. `README.md` for evaluator view  
3. `work/ACTIVE.md` if touching waves  

## Open decisions
- Server/deploy 8 facts — Viraj (external)  
- Excel freeze + migration owner — Viraj (external)
