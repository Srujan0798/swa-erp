# Open Items from Client Meetings — Requires Viraj/IT Input

**Status as of 2026-09-22**

---

## Critical Items Blocking Go-Live

### 1. Architecture Summary for Viraj → IT  ✅ **SENT 2026-09-22**
**File:** `deliverables/handover/ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md`
**Status:** ✅ Produced and sent to the company group 2026-09-22
**Action:** Await IT responses; re-send only if no reply

---

### 2. IT Con-Call & 8 Factual Answers  🔴 **BLOCKING DEPLOY**
**Owner:** Viraj → IT (Vikrant)
**Status:** 📮 Brief sent 2026-09-22 — **awaiting the 8 answers**
**Required:** 8 specific answers from IT (see `deliverables/SEND_IT.md`):

1. **Docker** — Installed? Free Engine or paid Desktop?
2. **WSL2** — Available/enabled on Windows Server?
3. **Free ports** — 5 ports needed (DB, Redis, MinIO, API, UI)?
4. **HTTPS** — Internal CA or self-signed cert?
5. **Backups** — Existing process to join?
6. **Internal URL** — What staff will type (e.g., `erp.swa.local`)?
7. **DB location** — Inside Docker or Windows services?
8. **Deploy process** — Remote access, commands, or existing pipeline?

**Impact:** Without these, `docker-compose.prod.yml` and `.env.production.example` have `PENDING IT ANSWER` placeholders — cannot deploy to company server.

---

### 3. Excel → ERP Migration Owner  🔴 **NO OWNER NAMED**
**Owner:** Viraj (organizational decision)
**Status:** ❌ No named owner
**Context:** The importer (`scripts/import_excel.py`) is built and tested. The one-time migration run against real data needs a named person who:
- Runs the dry-run against real Excel files
- Reviews row-by-row report
- Executes `--commit` when satisfied
- Coordinates with staff who currently edit the live Excel sheets

**Decision needed:** Who runs the real migration at go-live? (Viraj, Balram, or designated admin?)

---

## Open Business Decisions (Need Viraj Confirmation)

### 4. 4th Agreement ID  🟡 **UNCLEAR — MEETING SAYS "STILL OPEN"**
**Meeting 1 §7 / Meeting 2 §3:** "4th Agreement ID — What is it? (IESK/APEX/Inner known, 4th unnamed) — **Still open**"
**ADR-0002:** Viraj answered: "APEX and INNER are client names, not agreement types. INSUDESIGN is the service name. Earlier verbal 'IESK/APEX/Inner as three SA types' was a misread."

**Discrepancy:** Meeting notes say "Still open" but ADR records Viraj's answer that APEX/INNER are client names, INSUDESIGN is service name.

**Needed:** Viraj to clarify:
- Is there a 4th *agreement type* (like a 4th service product)?
- Or was the question based on a misread (as ADR states)?
- If service_name is free-text (as implemented), is any action needed?

**Current implementation:** `service_name` is free-text (not enum), INSUDESIGN is a valid value. No 4th-type enum.

---

### 5. Token / Reference-ID Annual Reset Behavior  🟡 **IMPLEMENTED, PENDING CONFIRMATION**
**Meeting 1 §7:** "Token/reference-ID annual reset behavior — implemented as a config-level choice, not hardcoded, pending confirmation either way."
**ADR-0002:** Viraj answered: "Yes — reset every year, everywhere. Example: `SWA-2025-SA-011` in 2025 → `SWA-2026-SA-001` in 2026. Same rule on all sheets/entity types."

**Status:** ✅ Implemented in code (counters keyed by `(entity_type, year)`). **Needs Viraj to confirm** this matches his expectation before go-live.

---

### 6. Reforge ID Exact Format  🟡 **PENDING CONFIRMATION**
**Meeting 1 §7:** "Reforge ID exact format (`INNN074`) — stored as free text pending confirmation."
**Current implementation:** `refoge_id` stored as free-text (no validation). Sample format `INNN074` from meeting notes.

**Needed:** Viraj to confirm exact format or confirm free-text is acceptable.

---

### 8. Compliance Standard Versions  🟢 **COSMETIC — NO CODE BLOCKED**
**Meeting 2 Action Item:** "Share compliance standard versions (NBC/ECBC/IGBC/IS years) — Viraj + Auditor — Before Wave-6 (**still open**)"
**ADR-0002:** "Cosmetic; no code blocked."

**Needed:** Viraj/Auditor to provide which years of NBC/ECBC/IGBC/IS standards to reference in compliance checklists. Purely display/cataloging.

---

### 9. Windows Server OS Confirmation  🟡 **99% — NEEDS 100%**
**Meeting 2 §1:** "Windows Server, on-prem — Viraj: '99% confident it's Windows only' — not 100%. Confirm on the IT call."
**Status:** 99% confirmed. Need IT call to reach 100% or confirm alternative.

---

## Summary: What Viraj Needs to Do Before Go-Live

| # | Action | Owner | Blocking? |
|---|--------|-------|-----------|
| 1 | Forward `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` to IT with `SEND_IT.md` | Viraj | ✅ Sent 2026-09-22 — awaiting responses |
| 2 | Get 8 IT answers from IT team | Viraj → IT | 🔴 Yes (deployment blocked) |
| 3 | Name migration owner (who runs real Excel import) | Viraj | 🔴 Yes (go-live blocked) |
| 4 | Confirm 4th Agreement ID question resolution | Viraj | 🟡 Clarify |
| 5 | Confirm annual ID reset behavior matches expectation | Viraj | 🟡 Confirm |
| 8 | Provide compliance standard versions (NBC/ECBC/IGBC/IS years) | Viraj + Auditor | 🟢 Cosmetic |
| 9 | Confirm Windows Server 100% on IT call | Viraj → IT | 🟡 Confirm |

---

## Already Resolved (No Action Needed)

| Item | Resolution |
|------|------------|
| APEX/INNER/INSUDESIGN | APEX/INNER = client names; INSUDESIGN = service name (free-text) |
| Yearly ID reset | Implemented as config (per-year counters) — confirm with Viraj |
| Lead ID / LDI | Removed entirely (Viraj instruction) — migration 0030 applied |
| GST on invoices | Built and verified (wave-7/11) |
| Client portal | Explicitly deferred — out of MVP |
| HR/Finance/Satisfaction sheets | Explicitly dropped from MVP |
| Reforge/DPR | Role-gated (Auditor+Designer) but no dedicated UI |
| Independent sheets (HR/Finance/Marketing) | Dropped from MVP |
| GST invoicing | Built and verified (wave-7/11) |

---

## Quick Reference for Viraj

**Files to send to IT:**
1. `deliverables/handover/ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` (this repo)
2. `deliverables/SEND_IT.md` (8 questions)

**Questions to answer yourself:**
- [ ] Who runs the Excel → ERP migration at go-live?
- [ ] Is the annual ID reset behavior correct? (counters reset Jan 1)
- [ ] Is the 4th Agreement ID question resolved? (service_name is free-text)
- [ ] Confirm Windows Server 100% on IT call
- [ ] Provide compliance standard years (NBC/ECBC/IGBC/IS)

**Files ready for demo:**
- `make dev` → UI at :3100, API at :8100
- `python3 scripts/smoke_chain.py` → full chain verification
- Demo script: `deliverables/DEMO_SCRIPT.md`

---

## Contact

**Srujan** — Available for 15-min call with Viraj + IT to walk through architecture and 8 questions.

---

*This document consolidates all open items from `resources/MEETINGS_MASTER.md`, `docs/decisions/0002-core-id-chain-gap.md`, and meeting action items. Update as items are resolved.*