# Viraj Decision Log — Action Required

**Purpose:** Every decision Viraj must make before go-live. One line per decision. No fluff.

---

## 🔴 BLOCKING GO-LIVE (Must Resolve)

| # | Decision | Options | Default/Recommendation | Status |
|---|----------|---------|------------------------|--------|
| 1 | **Who runs the Excel → ERP migration at go-live?** | You / Balram / Designated admin | You decide; importer is ready | ❌ No owner |
| 2 | **8 IT answers** (Docker, WSL2, ports, HTTPS, backups, URL, DB location, deploy) | You → IT (Vikrant) | Forward `SEND_IT.md` + `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` | ✅ Sent to group 2026-09-22 — awaiting answers |
| 3 | **Internal web address** staff will use (e.g., `erp.swa.local` or IP) | `erp.swa.local` / IP:port | Must be locked before deploy | ❌ Not set |

---

## 🟡 NEEDS CONFIRMATION (Clarify Your Intent)

| # | Decision | Current Implementation | Your Confirmation Needed |
|---|----------|------------------------|--------------------------|
| 4 | **4th Agreement ID** — is there a 4th service product type? | `service_name` is free-text (not enum). INSUDESIGN works. No 4th-type enum. | Confirm: "Free-text is fine, no 4th enum needed" OR "Add 4th type: [name]" |
| 5 | **Annual ID reset** — counters reset Jan 1 for all entities? | Implemented: `reference_counters` keyed by `(entity_type, year)`, resets Jan 1 | Confirm: "Yes, reset every year everywhere" |
| 6 | **Windows Server** — 100% confirmed on IT call? | 99% per Meeting 2. | Confirm: "Yes, Windows Server on-prem" |
| 7 | **Reforge ID format** — `INNN074` or free-text? | Currently free-text (no validation). | Confirm: "Free-text is fine" OR "Enforce pattern: [pattern]" |

---

## 🟢 COSMETIC / NO CODE BLOCKED

| # | Decision | Notes |
|---|----------|-------|
| 8 | **Compliance standard versions** (NBC/ECBC/IGBC/IS years) | Purely display. Provide years when convenient. |
| 9 | **Client portal** | Explicitly deferred — out of MVP scope. No action. |
| 10 | **HR/Finance/Satisfaction/Complaints/Marketing sheets** | Explicitly dropped from MVP. No action. |

---

## ✅ ALREADY RESOLVED (No Action Needed)

| Item | Resolution |
|------|------------|
| APEX / INNER / INSUDESIGN | APEX/INNER = client names; INSUDESIGN = service name (free-text) |
| Yearly ID reset | Implemented as config (per-year counters) — confirm it matches expectation |
| Lead ID / LDI | Removed entirely (migration 0030 applied) |
| GST on invoices | Built and verified (wave-7/11) |
| Client portal | Explicitly deferred — out of MVP |
| HR/Finance/Satisfaction/Complaints | Explicitly dropped from MVP |
| Independent sheets (HR/Finance/Marketing) | Dropped from MVP |
| Reforge/DPR | Role-gated (Auditor+Designer) — no dedicated UI |
| GST invoicing | Built and verified (wave-7/11) |

---

## How to Respond

**For each 🔴/🟡 item:** Reply with the decision number and your answer. Example:

```
1. Migration owner: Balram
2. IT answers: Forwarded to Vikrant, expecting answers by Friday
3. Internal URL: erp.swa.local
4. 4th Agreement ID: Free-text is fine, no 4th enum
5. Annual ID reset: Yes, reset every year everywhere
6. Windows Server: Confirmed 100%
7. Reforge ID: Free-text is fine
```

---

## Files to Review (Ready Now)

| File | Purpose |
|------|---------|
| `deliverables/SEND_IT.md` | 8 questions for IT — sent to group 2026-09-22 |
| `deliverables/handover/ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` | Architecture for IT (sent with SEND_IT.md) |
| `decisions/OPEN_ITEMS_FROM_MEETINGS.md` | Full context for every open item |
| `deliverables/DEMO_SCRIPT.md` | 10-min demo walkthrough |

---

## Quick Commands for Demo

```bash
make dev                    # UI :3100, API :8100
python3 scripts/smoke_chain.py    # Full chain verification
# Login: admin@swa.co.in / admin123!
```

---

*Updated: 2026-09-22 | All code gates pass | Files sent to group — awaiting Vikrant's 8 answers + migration owner*