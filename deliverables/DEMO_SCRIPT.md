# Demo script — 5–10 minutes

Tight, rehearsable walkthrough for an evaluator or Viraj call. Expanded notes:
[`DEMO_WALKTHROUGH.md`](DEMO_WALKTHROUGH.md).

---

## Prep (once)

```bash
make install          # if needed
make dev              # UI http://localhost:3100 · API http://localhost:8100
APP_ENV=dev python3 scripts/seed_demo.py
# API-only fallback / rehearsal:
python3 scripts/smoke_chain.py
```

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@swa.co.in | admin123! |
| PM | pm@swa.co.in | pm123! |
| Designer | designer@swa.co.in | designer123! |

---

## Clock

| Min | Beat | Do / say |
|-----|------|----------|
| 0:00–1:00 | **Problem** | “SWA runs ~20 Excel sheets on OneDrive. This ERP is the **same** Inquiry→Client→Agreement→Token→DocRef→Time flow — digitization, not a new process.” |
| 1:00–1:30 | **Login + RBAC** | Log in as **admin**. Name five roles: admin / pm / designer / auditor / viewer. |
| 1:30–2:30 | **Clients** | Open **Clients**. Point at **APEX** / **INNER** as **client names**. Service product is separate. |
| 2:30–7:00 | **Core chain** | See script below — hit real `SWA-…` IDs. |
| 7:00–9:00 | **Time + GST + access** | Log billable time; open an invoice and show **GST**; optional: Designer can create Inquiry, Viewer blocked on export. |
| 9:00–10:00 | **Close** | “Product is built. Company-server install waits on a short IT fact list — no dedicated IT dept. Who runs Excel import at go-live?” |

---

## Core chain (say while clicking)

1. **Inquiries** — open or create one → `SWA-YYYY-INQ-…`.
2. **Convert** — show **new client** vs **existing client** path (system checks client DB, always ends in a Project).
3. **Service Agreement** — `SWA-YYYY-SA-…`, set **service_name = INSUDESIGN** (product name, not a client).
4. **Token** — unit of work under the agreement → `SWA-YYYY-TKN-…`.
5. **Document Reference** — issue DBR then KDR → both `SWA-YYYY-DBR-…` (**shared counter**).
6. Optional one-liner: “IDs reset every calendar year — `…-2025-…-011` then `…-2026-…-001`.”

---

## Money + compliance (pick 1–2)

- Time entry: 15-minute style, **billable** flag.
- Invoice: show `gst_percent` / `gst_amount` / `total` (18% GST path).
- Project compliance checklist: **NBC / ECBC / IGBC / IS**.

---

## If UI is slow — API-only

```bash
python3 scripts/smoke_chain.py
```

Prints live Inquiry → convert → SA → Token → DocRef IDs. Still narrate the table above.

---

## Rehearsal checklist

- [ ] `make dev` healthy (`/healthz` on :8100)
- [ ] Seeded demo users login
- [ ] One full chain with visible reference IDs
- [ ] One GST invoice field call-out
- [ ] One RBAC contrast (Designer ok / Viewer denied) **or** skip if time-boxed
- [ ] Do **not** claim client-server load numbers or “100% complete”
