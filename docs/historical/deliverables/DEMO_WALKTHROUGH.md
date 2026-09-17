# Demo walkthrough (15 minutes) — for Viraj call or training

**Prep (once, on your machine):**

```bash
make dev-services          # postgres + redis if not up
# backend + frontend: make dev   OR run them separately
APP_ENV=dev python3 scripts/seed_demo.py
# optional live API check:
python3 scripts/smoke_chain.py
```

Open UI: http://localhost:3100  
API docs: http://localhost:8100/docs  

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@swa.co.in | admin123! |
| PM | pm@swa.co.in | pm123! |
| Designer | designer@swa.co.in | designer123! |

---

## Script (say this out loud)

### 1. Problem (1 min)
“Today SWA runs operations on ~20 Excel files on OneDrive. This ERP is the same business
flow in one system — not new process, digitization of yours.”

### 2. Login + roles (1 min)
Login as **admin**. Mention five roles (admin / pm / designer / auditor / viewer).

### 3. Clients (2 min)
Open **Clients**. Point out **APEX** and **INNER** (client names).  
Service name is separate — next step.

### 4. Core chain — the thing that matters (6 min)
1. **Inquiries** — open one `SWA-YYYY-INQ-…`. Create or show “New” inquiry.  
2. **Convert** — existing client vs new client path (system checks client DB).  
3. **Service Agreement** — `SWA-YYYY-SA-…`, **service_name = INSUDESIGN** (product, not client).  
4. **Token** — unit of work under the agreement `SWA-YYYY-TKN-…`.  
5. **Document Reference** — DBR/KDR share one number sequence `SWA-YYYY-DBR-…`.  

Say: “Yearly reset: 2025 ends at …-011; 2026 starts …-001 everywhere — already how it works.”

### 5. Time + money + compliance (3 min)
- Log time (15‑min style billable hours).  
- Invoice with **GST** if you open financials.  
- Compliance checklist NBC / ECBC / IGBC / IS on a project.

### 6. Close (2 min)
“Build is done. Next is install on your Windows server when you have bandwidth — no separate
IT team needed for decisions; we use Docker defaults. Excel import is one-time after install.
Who should run that import — you, someone you name, or me on a call?”

---

## If the UI is slow / offline — API-only demo

```bash
python3 scripts/smoke_chain.py
```

It prints real `SWA-…` IDs for Inquiry → convert → SA → Token → DocRef.
