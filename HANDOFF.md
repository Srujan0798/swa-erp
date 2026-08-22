# Handoff Protocol

> **Role:** Session / orchestrator-switching protocol. Part of the front-door set — start at
> [README.md](README.md).

## Current state (2026-08-23 — RECOVERY MONTH / SWA-USABLE)

**Feedback:** SWA said product felt unusable / “dummy”. Response is a **4-week recovery** focused on real Excel chain UX — not more test waves.

**Week 1 done on main:** Document References first-class page; Excel-first sidebar; dashboard full chain; `make swa-live-local`; [`deliverables/VIRAJ_TRIAL_SCRIPT.md`](deliverables/VIRAJ_TRIAL_SCRIPT.md).

**Week 2+ field parity (in progress on main):** Time Logging Sheet columns on model/API/UI/import; Inquiry `technical_lead`; Doc Refs list matches Excel columns; Login/Dashboard/`VIRAJ_TRIAL_SCRIPT` real-data messaging. See `work/reports/recovery/LOOP.md`.

Plan: session `plan.md` recovery (Weeks 1–4). Reports: `work/reports/recovery/`.

---

## Prior seal (still true)

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
