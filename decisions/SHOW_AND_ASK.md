# Demo & Show Guide — What to Show Viraj & IT

**Purpose:** Exact script for demo. 10 minutes max. No fluff.

---

## 1. Pre-Demo Checklist (Do Before Call)

```bash
make dev                          # UI :3100, API :8100
python3 scripts/smoke_chain.py    # Verify full chain works
```

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@swa.co.in | admin123! |
| PM | pm@swa.co.in | pm123! |
| Designer | designer@swa.co.in | designer123! |

---

## 2. 10-Minute Demo Script

| Time | Beat | Click / Say |
|------|------|-------------|
| **0:00–1:00** | **Problem** | "SWA runs ~20 Excel sheets on OneDrive. This ERP is the **same** Inquiry→Client→Agreement→Token→DocRef→Time flow — digitization, not a new process." |
| **1:00–1:30** | **Login + RBAC** | Login as **admin**. Show 5 roles: admin / pm / designer / auditor / viewer. |
| **1:30–2:30** | **Clients** | Open **Clients**. Point at **APEX** / **INNER** as **client names**. Service product is **INSUDESIGN** (separate). |
| **2:30–7:00** | **Core Chain** | See script below — hit real `SWA-…` IDs live. |
| **7:00–9:00** | **Time + GST + Access** | Log billable time; open invoice → show **GST**; Designer creates Inquiry, Viewer blocked on export. |
| **9:00–10:00** | **Close** | "Product is built. Company-server install waits on short IT fact list — no dedicated IT dept. Who runs Excel import at go-live?" |

---

## 3. Core Chain — Click & Say (Exact IDs)

| Step | Page | Action | Say |
|------|------|--------|-----|
| 1 | **Inquiries** | Create or open one | "Inquiry `SWA-2026-INQ-004` — annual counter reset" |
| 2 | **Convert** | Click **Convert** → choose **new client** vs **existing client** | "System checks client DB. Always ends in a Project. New client → creates Client + Project. Existing → reuses Client, creates Project." |
| 3 | **Service Agreement** | Open **Agreements** → create | "`SWA-2026-SA-003` — service_name = **INSUDESIGN** (product, not client)" |
| 4 | **Token** | Open **Tokens** → create under SA | "`SWA-2026-TKN-003` — unit of work under the agreement" |
| 5 | **Document Reference** | Open **Doc Refs** → issue **DBR** then **KDR** | "Both `SWA-2026-DBR-…` — **shared counter** (DBR 001 → KDR 002)" |
| 6 | *Optional* | | "IDs reset every calendar year — `…-2025-…-011` then `…-2026-…-001`" |

---

## 4. Money + Compliance (Pick 1–2)

| Feature | Where | Call Out |
|---------|-------|----------|
| Time entry | Time Tracking page | 15-min increments, **billable** flag |
| Invoice | Invoices page | Show `gst_percent` / `gst_amount` / `total` (18% GST) |
| Compliance | Projects → Compliance | **NBC / ECBC / IGBC / IS** checklists |

---

## 5. API-Only Fallback (If UI Slow)

```bash
python3 scripts/smoke_chain.py
```

Prints live: `INQ → convert → SA → TKN → DBR → Invoice → Paid`

---

## 5. What NOT to Claim

| ❌ Don't Say | ✅ Say Instead |
|--------------|----------------|
| "100% complete" | "Product MVP shipped; IT deploy pending" |
| "Load tested on client server" | "Load tested 10–150 users on dev machine (p95 29–130 ms)" |
| "Zero risk" | "Known test infra gaps documented; production code solid" |
| "All modules done" | "5 MVP modules shipped; HR/Finance/Marketing explicitly dropped" |

---

## 6. What to Hand Over (Files)

| File | Who Gets It |
|------|-------------|
| `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` | Viraj → forwards to IT |
| `SEND_IT.md` | Viraj → forwards to IT (8 questions) |
| `OPEN_ITEMS_FROM_MEETINGS.md` | Viraj (your decision log) |
| `DEMO_SCRIPT.md` | You (this script) |
| `SMOKE_CHAIN` output | Live proof |

---

## 7. What to Ask Live (Decision Close)

| To Viraj | To IT (Vikrant) |
|----------|-----------------|
| "Who runs the Excel import at go-live?" | "Can you answer the 8 questions in `SEND_IT.md`?" |
| "Confirm: annual ID reset = Jan 1 reset?" | "Docker/WSL2/ports/HTTPS/backups/URL/DB location/deploy?" |
| "Who runs the real Excel migration at go-live?" | "Internal URL (erp.swa.local)? HTTPS cert?" |
| "4th Agreement ID: free-text OK?" | "DB in Docker or Windows services? Backup process?" |

---

## 8. One-Liner Close

> "Product is built and tested. Company-server install waits on a short IT fact list — no dedicated IT dept. Who runs Excel import at go-live?"

---

*Demo time: 10 min | Practice once | Have `smoke_chain.py` ready as backup*