# SWA Consultancy ERP — Submission Package

**Product version:** 1.0.1 (tagged `v1.0.1`)  
**Package refreshed:** 2026-08-23 (wave-38 — professional-grade metrics)  
**Status:** Product MVP **shipped**. Quality track waves **32–36 + 39 shipped**. Wave-37 independent review **findings pending in parallel** (not claimed closed). **Company-server deploy remains external** (no IT dept; server facts open).

This is the single document handed over with the project. It is honest about what exists, what
does not, and what is still waiting on the client's side. Evaluator front door: [`README.md`](../README.md).
Engineering narrative: [`TECHNICAL_REPORT.md`](TECHNICAL_REPORT.md).

---

## 0. Verified metrics (post wave-32–36)

Safe wording only — every row cites a report. See also [`work/reports/wave-38/_draft-metrics.md`](../work/reports/wave-38/_draft-metrics.md).

| Claim | Number | Source |
|-------|--------|--------|
| Backend coverage (overall) | **86%** (8702 stmts / 1201 miss) | [`COMPLETION-HANDOFF-VERDICT.md`](../work/reports/COMPLETION-HANDOFF-VERDICT.md); wave-33 report 03 |
| Backend services layer | **All `services/*.py` ≥70%** | Same verdict (do **not** claim global “no module under 70%”) |
| Backend suite (independent 2026-08-23) | **557 passed, 5 failed, 1 skipped** | Same (5× 401-vs-403 standing auth assertions) |
| CI coverage floor | `--cov-fail-under=82` (86% clears it) | Makefile + wave-32 |
| Frontend thresholds | **60 / 50 / 60 / 60** met; cite **~61% statements** independently | Verdict + wave-34 report 02 |
| Load test | **10–150 users**, p95 **≈ 29–130 ms**, no 5xx after fixes, **dev machine only** | [`docs/PERFORMANCE.md`](../docs/PERFORMANCE.md) |
| CI honesty | **0** `\|\| true` / `continue-on-error` in `.github/workflows/` | wave-32 report |
| MinIO + Celery | **BUILT** (wave-31) | `src/backend/core/storage.py`, `src/backend/workers/`, compose |
| Observability | `/metrics`, `/healthz`, `/readyz`, optional Sentry | [`docs/OBSERVABILITY.md`](../docs/OBSERVABILITY.md) |
| Deploy on client server | **Not done** — facts OPEN | [`SEND_IT.md`](SEND_IT.md) |

**Forbidden overclaims (anti-fabrication):** “100% complete”; “562 passed” as a pass count; “0 failed” while the five auth tests fail; global “no module under 70%”; stale frontend **65.86%** without a fresh vitest paste; “MinIO/Celery not built.”

---

## 1. What was built

A web-based internal ERP that replaces SWA's ~20 Excel files on OneDrive with one system while
keeping the same business logic staff already use. It digitizes the existing workflow rather
than adding new processes.

The core flow — the thing the client actually asked for — maps 1:1 to the workflow described in
`resources/MEETINGS_MASTER.md` (Meeting 1 + Meeting 2):

```
Inquiry comes in (a lead)                     → SWA-{year}-INQ-{seq}
    ↓
Does the client already exist?                → No: create a new Client   → SWA-{year}-CLT-{seq}
                                             → Yes: reuse the existing Client
    ↓
A Project is created under that Client
    ↓
Recurring client?  Service Agreement          → SWA-{year}-SA-{seq}
    ↓
Work requested under the agreement = Token    → SWA-{year}-TKN-{seq}
    ↓
Actual documents produced get a unique
Document Reference Number                    → SWA-{year}-DBR-{seq} (DBR and KDR share this counter)
    ↓
Staff log hours, tied to Project/Token/Doc
    ↓
Post-completion sustainability metrics
(energy saved, CO2 avoided, payback period)
```

**Modules in plain language:**

| Module | What it does | Wave |
|---|---|---|
| Auth, users, roles | Login (JWT), admin/pm/designer/auditor/viewer permissions, rate-limited login | 1, 18, 22 |
| Clients & Contacts | Company records, contacts, search, client status, industry | 2 |
| Projects | Project records with the 8-step lifecycle (Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed), team assignment, optimistic locking | 2, 23 |
| Quotations / BOQ | Upload a BOQ (JSON/Excel), version it, generate and approve quotes, PDF export | 3 |
| Tasks | Per-project tasks, assignees, dependencies, kanban board | 4 |
| Vendors & Materials | Vendor database, materials catalog, RFQ-to-vendor workflow | 5 |
| Documents & Compliance | File uploads, NBC/ECBC/IGBC/IS compliance checklists | 6 |
| **Inquiry → Client → Agreement → Token → DocRef chain** | The client's core chain above, with the shared `SWA-{year}-{TYPE}-{seq}` reference-ID generator | 9 |
| Sustainability metrics | Energy/CO2/payback tracking per project | 10 |
| Time tracking & financials | Timesheets (15-min increments, billable flag), invoices **with GST breakdown**, project P&L | 7, 23 |
| Reports & dashboards | Project summaries, financial report (real costs), dashboard stats, PDF/JSON exports | 8 |
| Notifications | In-app bell, unread badge, mark-read | 24 |
| Backups & ops | `make backup-db` / `backup-files` / `restore-db` scripts (credential-safe), 30/90-day retention | 19, 27 |
| Excel → ERP importer | One-time migration tool for the existing sheets (dry-run by default) | 13 |

## 2. Verification evidence

### 2a. Professional-grade re-verify (2026-08-23) — prefer these numbers

Independent backend coverage run after `swa_erp_test` reset (see completion verdict):

```
python3 -m pytest tests/ -q --cov=src/backend --cov-report=term
# → 5 failed, 557 passed, 1 skipped
# → TOTAL 8702 stmts, 1201 miss → 86%
# Wave-33 targets: pdf 100%, quote 97%, import 80%, task 97%, notification 100%
```

Frontend: vitest thresholds **60/50/60/60** met; independent measurement **~61% statements**
(do not cite report-02’s 65.86% without a fresh paste). Known flake: TaskCard overdue days under
`TZ=Asia/Kolkata` when tests use UTC `toISOString()`.

Load: see [`docs/PERFORMANCE.md`](../docs/PERFORMANCE.md) — 10/50/100/150 users, p95 ≈ 29–130 ms
**on a development machine**.

CI: wave-32 removed all soft-fail escapes from workflows; security.yml runs real audits.

### 2b. Original v1.0.1 cut evidence (2026-08-07) — historical

All commands below were run live on **2026-08-07** against the working tree that produced the
original client cut. Kept for provenance; **superseded for coverage/suite counts by §2a**.

Backend test suite at that cut (393 passed):

```
$ python3 -m pytest tests/ -q
================= 393 passed, 42 warnings in 135.26s (0:02:15) =================
```

Lint / typecheck / build at that cut: ruff clean; frontend `tsc` / eslint / `vite build` green.

Docker cold boot at that cut used host port **8000** in the curl sample below; **current dev
ports are 3100 (UI) / 8100 (API)**.

```
$ curl -sf http://localhost:8000/healthz
{"status":"ok"}                      # HTTP 200  (historical port)
```

End-to-end browser tests at that cut: `npx playwright test tests/e2e/ --workers=1` → 7 passed.

Live end-to-end business flow — walked via the real API (all `SWA-{year}-{TYPE}-{seq:03d}`):

| Step | Result | Reference ID |
|---|---|---|
| Login (admin) | 200 | — |
| Create Inquiry | 201 | `SWA-2026-INQ-004` |
| Convert — **new-client path** (no `client_id` → client + project created) | 200 | — |
| Create Inquiry #2 | 201 | `SWA-2026-INQ-005` |
| Convert — **existing-client path** (reused seeded Tata Chemicals client) | 200 | — |
| Create Service Agreement | 201 | `SWA-2026-SA-001` |
| Issue Token | 201 | `SWA-2026-TKN-001` |
| Issue **DBR** document reference | 201 | `SWA-2026-DBR-001` |
| Issue **KDR** document reference | 201 | `SWA-2026-DBR-002` |
| Log time against project (8.00 h, billable) | 201 | — |
| Record sustainability metric (12,500 kWh saved) | 201 | — |
| Generate invoice from time | 201 | `INV-202608-0001` |
| Export project summary report | 200 | `application/pdf`, 1,936 bytes |

**GST verification** (the client asked for GST on invoices): `subtotal 40000.00`, `tax_rate
18.00`, `tax_amount 7200.00`, `gst_percent 18.00`, `gst_amount 7200.00`, `total 47200.00` —
GST fields match the tax computation exactly.

**DBR/KDR shared counter confirmed:** both document types increment the same counter
(`SWA-2026-DBR-001` → `SWA-2026-DBR-002`), matching the client's practice of numbering
drawings and documents in one sequence.

**Wave-22 RBAC confirmed live:** the **Designer** role successfully created an Inquiry (201) and
a DBR document reference (201); a **Viewer** was correctly blocked (403) from the exports
endpoint.

## 3. What is explicitly NOT included

Per the client's confirmed decisions (Meeting 1 §7 and Meeting 2 §3 in
`resources/MEETINGS_MASTER.md`):

- **HR / Admin records** — explicitly dropped from the MVP (access-restricted, separate sheet).
- **Finance / founder-only sheets** — excluded; kept as a separate, restricted process.
- **Employee Satisfaction** — dropped from MVP.
- **Client Satisfaction & Client Complaints** — explicitly dropped from MVP.
- **Marketing** (Instagram/LinkedIn/website stats) — excluded, separate process.
- **Client portal** — deferred in Meeting 2 ("Wave-8 or later?"); not built.

Also deliberately deferred, not forgotten:
- Reforge/DPR document certification flow is role-gated in the code (Auditor+Designer) but has
  no dedicated UI screen.
- The full 21-sheet Excel import has been validated on the importer for its supported sheet
  types; the actual one-time migration run against real data is a go-live decision for Viraj
  (who runs it — see §7).

## 4. Known limitations, stated honestly

These are real and deliberately not hidden. None were discovered by the client first.

1. **Celery — BUILT (wave-31).** Real app in `src/backend/workers/`, compose `worker` service,
   async export (`?async=true` → job_id + `GET /api/jobs/{id}`). Sync path still available.
   *(Older drafts of this section said Celery was unmet — that claim is obsolete.)*
2. **File storage — local default; MinIO BUILT (wave-31).** `StorageBackend` in
   `src/backend/core/storage.py`; `STORAGE_BACKEND=local|minio`. Default `local` keeps
   `uploads/`. Pre-wave-31 files are not auto-migrated. Backups must cover object storage too
   (`make backup-files` for local).
3. **JWT is HS256, not RS256.** A single shared secret signs tokens; fine for an internal
   on-prem app, but if SWA ever needs token verification by a third party, RS256 is the target.
4. **Alembic heads.** Wave-31 collapsed heads for the release line; always confirm with
   `alembic heads` before a cold boot. Historical multi-head note from the Aug 7 cut is
   provenance only.
5. **Auth rate limiter is on by default (5 login/min per IP).** The dev compose file sets
   `DISABLE_AUTH_RATE_LIMIT=true` so test suites don't get throttled. Production should keep
   the limiter on (or raise it behind shared NAT/VPN).
6. **Standing suite debt (2026-08-23):** five tests still expect **401** for missing
   `Authorization`; FastAPI `HTTPBearer` returns **403**. Not a wave-38 regression — parked for
   wave-37 triage. Frontend TaskCard overdue assertion can flake under IST.
7. **Coverage is not “every module ≥70%.”** Overall backend 86%; services all ≥70%; nine
   non-alembic modules still under 70% (see completion verdict).
8. **Load results are not production-server results.** Measured on a development machine only.
9. **`/metrics` is unauthenticated in app code** — treat as internal-only in production network
   policy (called out again in wave-37 security scratch; final triage pending).
10. **Wave-37 independent review** is not closed in this package — say “findings pending in
    parallel,” do not invent a clean bill of health.

## 5. External blockers

**A. Viraj's 3 data decisions — RESOLVED (2026-08)** — see `docs/decisions/0002-core-id-chain-gap.md`:

| # | Resolution |
|---|------------|
| 1 | **APEX / INNER are client names**; **INSUDESIGN is the service name** (not a 4th SA type). |
| 2 | **Yearly ID reset confirmed everywhere:** e.g. `SWA-2025-SA-011` → next year `SWA-2026-SA-001`. |
| 3 | **No Leads sheet** (removed from design). `LDI-*` / First Lead ID are historical only; new work is Inquiry. |

System already matched these answers (free-text `service_name`, per-year counters, no Leads module).
No code change required. Confirm reply for Viraj: `deliverables/REPLY_VIRAJ.md`.

Still organizational (not a schema question): **who runs the real Excel → ERP migration** at go-live
(Viraj decides).

**B. Server / deploy facts — STILL OPEN (no IT department)**  

Asked in the client WhatsApp group (2026-08-11). Viraj stated **there is no IT department** and
will try to get answers when free. Draft list (reference only, already messaged):
`deliverables/SEND_IT.md`.

1. Docker · 2. WSL2 · 3. Free ports · 4. HTTPS/cert · 5. Backups · 6. Internal hostname/IP ·
7. DB/Redis in Docker vs Windows services · 8. How updates are applied.

*If unanswered:* company-server production deploy waits. Do not invent hostname/ports.
`docker-compose.prod.yml` / `.env.production.example` still have `PENDING IT ANSWER (Q#)`
markers — fill when Viraj (or nominee) provides facts (see §6).

## 6. How to deploy

Full step-by-step: **`docs/DEPLOYMENT_CHECKLIST.md`**.

- Production compose file: **`docker-compose.prod.yml`** + `.env.production.example`.
- **Before deploying, every `PENDING IT ANSWER (Q#)` placeholder** in those two files must be
  filled using IT's answers from `docs/IT_BRIEF.md` (Q1, Q2, Q3, Q4, Q6, Q7). The checklist
  walks through each one.
- Rollback: image-tagged stack; `docker compose -f docker-compose.prod.yml down` preserves data
  volumes (never `down -v` in production); re-deploy the previous tag. A failed migration means
  restore the pre-deployment DB backup instead.
- Post-deploy smoke test: log in as each role, walk the chain (the checklist has an 18-row API
  smoke table plus a UI walk).

## 7. How to import the existing Excel data

One-time migration tool: **`scripts/import_excel.py`**.

```
python3 scripts/import_excel.py <sheet_type> <file.xlsx>         # DRY-RUN by default (no writes)
python3 scripts/import_excel.py <sheet_type> <file.xlsx> --commit  # persists
```

Supported sheet types: `clients, inquiries, agreements, tokens, document_references, projects,
time_logs, sustainability`. **Always dry-run first** and review the row-by-row report before
committing. The importer maps legacy `LDI-*` IDs into the Inquiry table. Who runs this against
real data is a go-live decision for Viraj (ADR-0002 open item #4).

## 8. Where the docs live

The canonical set (consolidated by waves 26-29; superseded files are archived under
`docs/historical/` and `attic/`, never deleted):

| Doc | Purpose |
|---|---|
| `README.md` | Evaluator front door (60s) + verified metrics |
| `docs/ARCHITECTURE.md` | Mermaid architecture (built vs target) |
| `deliverables/TECHNICAL_REPORT.md` | Engineering case study |
| `deliverables/DEMO_SCRIPT.md` | 5–10 min demo script |
| `CHANGELOG.md` | Full release history (`[1.0.1]` product cut) |
| `plan/EXECUTION.md` / `work/ACTIVE.md` | Wave status (1–31 product; 32–39 professional-grade) |
| `docs/DEPLOYMENT_CHECKLIST.md` | Production deploy steps (see §6) |
| `docs/IT_BRIEF.md` / `deliverables/SEND_IT.md` | The 8 IT questions + deploy brief |
| `docs/INSTALL_NO_IT.md` | Install path when there is no IT department |
| `docs/decisions/0001..0004` | ADRs (tech stack, core ID chain, IT brief, meeting-2 flow) |
| `docs/PERFORMANCE.md` | Load-test evidence |
| `docs/OBSERVABILITY.md` | Metrics / health / Sentry |
| `docs/runbook.md` + `docs/runbook_backup_restore.md` | Day-to-day ops + backup/restore |
| `docs/api.md`, `docs/conventions.md`, `docs/SCOPE_GUARD.md` | API reference, conventions, scope |
| `docs/PROJECT_HISTORY.md` | How the project got here (distilled history) |
| `resources/MEETINGS_MASTER.md` | Consolidated record of both client meetings |
| `resources/EXCEL_SHEETS_INVENTORY.md` | The 21 source sheets and their mapping |
| `deliverables/handover/` | `ADMIN_GUIDE.md`, `USER_GUIDE.md`, `TRAINING_ONE_PAGER.md`, `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` |
| `work/reports/wave-N/` | Per-wave verification reports |

## 9. Support / next steps

What a future developer picks up first:

1. Read `deliverables/SUBMISSION.md` (this file) → `MASTER-FLOW.md` → `HANDOFF.md`.
2. Viraj data Qs are closed (§5A). Optional: send `deliverables/REPLY_VIRAJ.md` to confirm +
   LDI example + ask who owns migration.
3. Send `deliverables/SEND_IT.md` to IT if not yet answered — only remaining deploy blocker.
4. Deploy per §6 and `docs/DEPLOYMENT_CHECKLIST.md` once IT answers land.
5. Run the Excel import (§7) against real data when Viraj confirms who owns the migration.
6. Highest-value engineering follow-ups (optional, post-MVP):
   - Move transactional email off the request path onto the Celery queue.
   - (Resolved: year-reset policy confirmed by Viraj — already implemented.)
   - (Resolved in wave-31: MinIO/S3 + Celery worker; Alembic heads collapsed.)

Everything else — the core chain, RBAC matrix, GST invoicing, compliance, time tracking, and
the backup/ops scripts — shipped in product `1.0.1`. Professional-grade evidence (real CI,
86% backend coverage, frontend thresholds, load, observability) landed in waves 32–36.
**Deploy to the company Windows Server is still an external step** — use `SEND_IT.md` /
`INSTALL_NO_IT.md` when Viraj has bandwidth. Do not invent server facts.
