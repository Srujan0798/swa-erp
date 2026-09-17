# 24-hour handoff — Jaydeep meeting is TOMORROW

**Assign agents from `work/DISPATCH-24H.md` (master).** This file is session context only.

**Previous agent: STOPPED.** Do not continue vibe-coding. Meeting script: `deliverables/JAYDEEP_MEETING_TODAY.md`.

Meeting shifted **24 hours**. Srujan will assign this to a new agent. Goal: product that can be **shown live** to Jaydeep (server person Viraj tagged — no IT dept), plus CEO/CFO/technical if they join. Not a dummy website.

---

## 0. Truth hierarchy (do not invent)

1. Client words: `resources/MEETINGS_MASTER.md` + `docs/decisions/0002` `0003` `0004`
2. Working system: `src/backend/`, `src/frontend/`, tests, **fresh command output**
3. Meeting scripts: `deliverables/JAYDEEP_MEETING_TODAY.md` then `MEETING_AND_GO_LIVE_GUIDE.md`
4. Evaluator: `README.md`, `deliverables/SUBMISSION.md`
5. Session files (`HANDOFF.md`, `MASTER-FLOW.md`, old wave reports) — **stale numbers**. Code wins.

**Locked with Viraj (do not reopen, do not “fix” into enums):**
- APEX / INNER = **client names**
- INSUDESIGN = **service name**
- Yearly ID reset everywhere (`SWA-2025-SA-011` → `SWA-2026-SA-001`)
- No Leads module; Lead ID / LDI **removed even historically**
- HR / complaints / marketing / client portal = **out of MVP**

**Still on them (not code):** Windows Server person, 1–2 hour slot, Excel freeze name, import runner, first 3–5 users.

---

## 1. Repo state when I stopped

- Branch `main`, **ahead of origin** (unpushed). HEAD around `e08482b`.
- **Large dirty tree** — mix of this session’s meeting fixes **and another worker’s files**. Orient with `git status` / `git diff` **before** commit or revert.
- Alembic: DB was upgraded to **0036** locally (`token_version`, `is_billed`, `CREATE SEQUENCE IF NOT EXISTS invoice_number_seq`). File `src/backend/alembic/versions/0036_token_version_and_is_billed.py` may still be **untracked**.
- Docker **dead** on this machine. Local Postgres `swa:swa@localhost:5432/swa_erp`. Redis often down (login still works).
- Dev: UI **http://127.0.0.1:3100**, API **http://127.0.0.1:8100**. Login `admin@swa.co.in` / `admin123!`.
- Real data: `make swa-live-local` (Excel extract). **Never** `make seed-demo` for SWA.

Uncommitted that **this session** meant to land (keep):
- `AgreementsPage.tsx` / `TokensPage.tsx` — **New Agreement / New Token** on sidebar pages
- `lib/api.ts` — 204 empty body + better error `detail`
- `invoice_repo.py` — create sequence if missing
- `inquiry_service.py` — convert allow `Contacted`; yearly `CLT`/`PRJ` IDs; project status Awarded
- `InvoicesPage.tsx` — GST display, Mark sent / Mark paid
- `InvoiceDetail.tsx` — GST % not ×100
- `DashboardPage.tsx` — “Lead / ML” copy removed
- `ClientForm` / `ProjectForm` — empty dates / `__none__` select
- `auth_service.py` — was **IndentationError** (login dead); indentation restored
- `0036_*.py` migration
- `deliverables/JAYDEEP_MEETING_TODAY.md` + expanded `MEETING_AND_GO_LIVE_GUIDE.md`

Other dirty files (`documents.py` IDOR, `jobs.py`, wave reports, extra tests) may be **another session**. Do not revert blindly.

---

## 2. What was verified live (fresh HTTP, this session)

| Check | Result |
|---|---|
| `GET /healthz` | `{"status":"ok"}` |
| Login admin | 200 |
| After `bootstrap_real` | Inquiries `SWA-2025-INQ-001/002/003` (003 **New**); SA-011 **INSUDESIGN**; tokens TKN-001…004; CON/DBR/CAS/GAD |
| Create inquiry → convert → SA INSUDESIGN → token → DBR (`doc_date` required) → time | worked |
| Create invoice | **201** `INV-202609-0001` subtotal 5000 + GST 900 = **5900** (after sequence fix) |
| Convert IDs before fix | `SWA-CLT-001` / `SWA-PRJ-001` (no year) — **code patched**, re-verify after commit |
| `GET /api/invoices` global | **404** — invoices are `/api/projects/{id}/invoices` |

Dummy **Smoke Client** / **LIVECHECK-** rows appear if anyone runs `smoke_chain.py` or test creates. **Re-run `make swa-live-local` before the meeting.**

---

## 3. 24-hour improvement protocol (assign in this order)

Do **not** start new modules. Do **not** “complete the whole ERP.” Jaydeep needs the **Excel chain** to click without embarrassment.

### Phase A — freeze a bootable tree (hour 0–2)

1. `git status` / `git diff`. Split: meeting-critical vs other-worker.
2. Commit **or** stash the meeting-critical set listed in §1. Leave unrelated reports/tests unless they compile.
3. Confirm `alembic current` = **0036** on `swa_erp`. If login 500 `token_version`: upgrade.
4. `make swa-live-local`. Login. Screenshot/list: INQ-001, SA-011 INSUDESIGN.
5. `python3 scripts/smoke_chain.py` **pollutes DB** — if you run it, bootstrap again after.

### Phase B — must-work walkthrough (hour 2–10)

Walk as a user on :3100 (admin). Fix only if it **fails the click**:

1. Login  
2. Dashboard 1–7 (no empty amber banner)  
3. Inquiries: New Inquiry; open INQ-003; **Convert** (unique name)  
4. Clients: New Client with blank optional date (must not 422)  
5. **3. Service Agreements → New Agreement** (INSUDESIGN)  
6. **4. Tokens → New Token**  
7. **5. Document refs → New** (type exactly `DBR` or `KDR` for designer; project required)  
8. Time logging → Add 1.00h billable  
9. Invoices: pick project → New Invoice GST 18% → View → Mark sent  

**Known remaining product bugs (fix if time; do not hide):**

| Severity | Issue | Where |
|---|---|---|
| HIGH | **Files / drawings** is a stub (“implementation pending”). Meeting script: **do not open**. | `FileBrowser.tsx` |
| HIGH | Convert HTTP **300** duplicate-name picker reads `body.candidates` but FastAPI wraps `detail.candidates` — silent no-op | `ConvertToClientButton.tsx` |
| HIGH | Delete 204 was fixed in `api.ts` — **re-test** inquiry/client/SA delete toast |
| MED | Invoice-from-time API has **no UI** | `generateInvoiceFromTime` |
| MED | Client Edit: PM sees button, API **admin-only** 403 | `ClientDetailPage` vs `clients.py` |
| MED | Inquiry field edit missing; designer sees status/delete, API PM-only 403 | `InquiryDetailPage` |
| MED | Doc type must be exact `DBR`/`KDR` for shared counter; “Design Basis Report” 403s designer | `document_references.py` |
| LOW | Sample extract has **no APEX/INNER**; SA clients ABCD/APPLE/GOOGLE; `SWA-SYS-UNLINKED` stub | Explain, don’t fake |

Out of scope for 24h: Vendors, RFQs, Materials, Tasks, Quotes, Word generation, client portal, Docker-on-Windows (needs Jaydeep).

### Phase C — verify with evidence (hour 10–16)

For every “fixed” claim, paste **fresh** command output. No “should work.”

```bash
# API
curl -s http://127.0.0.1:8100/healthz
# login + list inquiries/agreements (see JAYDEEP_MEETING_TODAY.md)
# Frontend
cd src/frontend && npx tsc --noEmit
# Backend lint on touched files only if time
python3 -m ruff check src/backend/services/inquiry_service.py src/backend/services/auth_service.py src/backend/db/repositories/invoice_repo.py
```

Full pytest on this laptop: Python **3.14** vs project **3.11**; Redis down; shared `swa_erp_test`. Prefer **targeted** tests. Do not fabricate wave-49/50/51 report numbers.

### Phase D — docs hygiene (hour 16–20)

**Canonical for tomorrow:** `deliverables/JAYDEEP_MEETING_TODAY.md`  
**Long script:** `deliverables/MEETING_AND_GO_LIVE_GUIDE.md`  
**Stubs (already point at the guide):** `DEMO_SCRIPT.md`, `VIRAJ_TRIAL_SCRIPT.md`

Do **not** send clients: `SEND_VIRAJ.md` (obsolete 3 Qs), `SEND_IT.md` wall, `SUBMISSION.md`, `MEETINGS_MASTER.md`.

Archive never delete. Replace never append. One current truth per claim.

If you merge junk: keep handover/`USER_GUIDE.md` for **after** install only.

### Phase E — meeting dress rehearsal (hour 20–24)

1. `make swa-live-local`  
2. Rehearse `JAYDEEP_MEETING_TODAY.md` once, 12 minutes  
3. Confirm :3100 not :3000  
4. Paper: 8 closed questions (server name, slot, Docker Engine, IP, Excel same?, freeze name, import runner, first users)  
5. Do not promise company-server load numbers  

---

## 4. Folder / hierarchy (what is junk vs live)

| Path | Role |
|---|---|
| `src/backend/{api,services,models,schemas}` | Product |
| `src/frontend/src/{pages,components}` | Product |
| `resources/ERP_Sheets_Extracted/` | Real sample Excel |
| `docs/decisions/` | Locked answers |
| `deliverables/JAYDEEP_MEETING_TODAY.md` | **Tomorrow’s script** |
| `work/reports/` | Historical evidence; often stale |
| `docs/historical/`, `attic/` | Archived — do not resurrect |
| `plan/PRD.md` | Historical waves 1–4 “MVP” — **wrong** vs Excel chain |
| `scripts/seed_demo.py` | Synthetic. Forbidden for SWA show |

---

## 5. Questions for Jaydeep tomorrow (do not rewrite)

See `deliverables/JAYDEEP_MEETING_TODAY.md`. Short form:

1. Are you the Windows Server person?  
2. 1–2 hours when?  
3. Free Docker Engine + WSL2 OK?  
4. IP vs hostname week 1?  
5. Same as Excel — list or nothing?  
6. Who freezes OneDrive — one name?  
7. Who runs import — one name?  
8. First 3–5 users + roles?

---

## 6. Explicit do-nots for the next agent

- Do not start a new wave / new module / AI / portal.  
- Do not run `seed-demo` and call it the product.  
- Do not claim 100% complete or “thresholds met” (frontend functions were **58.45%**).  
- Do not fabricate test counts. `NOT MEASURED` is allowed.  
- Do not mix two workers’ uncommitted files into one sloppy commit.  
- Do not “fix” APEX into a service-type enum.  
- Do not open Files/drawings in the demo until FileBrowser is real.

---

## 7. Start command for the next agent

> Meeting is tomorrow with Jaydeep. Read `work/HANDOFF-24H-JAYDEEP.md` then `deliverables/JAYDEEP_MEETING_TODAY.md`. Do not redesign. Phase A freeze the dirty tree, Phase B make the Excel walkthrough click-clean, Phase C verify with pasted output, Phase E dress rehearsal. Stop when the 12-minute script works on :3100 with real Excel IDs. Remaining server/Excel-freeze questions are for Jaydeep, not more code.
