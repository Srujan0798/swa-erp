# SWA Consultancy ERP — v1.0.0 Submission Package

**Version:** 1.0.0 (client-submission release; tagged `v1.0.0`)
**Date:** 2026-08-07
**Status:** READY TO SUBMIT

This is the single document handed over with the project. It is honest about what exists, what
does not, and what is still waiting on the client's side.

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

All commands below were run live on **2026-08-07** against the working tree that produced this
release. Nothing is claimed from memory — outputs are pasted.

Backend test suite (expect 344+, actual 393):

```
$ python3 -m pytest tests/ -q
================= 393 passed, 42 warnings in 135.26s (0:02:15) =================
$ python3 -m pytest tests/ -q          # re-run after release edits
================= 393 passed, 42 warnings in 129.70s (0:02:09) =================
```

Lint / typecheck / build:

```
$ ruff check src/backend/
All checks passed!
$ npx tsc --noEmit           (src/frontend)
$ npx eslint . --ext ts,tsx --max-warnings 0     # exit 0, no warnings
$ npx vite build             (src/frontend)
✓ 1794 modules transformed.  ✓ built in 1.45s
```

Docker cold boot (`docker-compose down -v` then `up -d --build` — a fresh database, migrations
run automatically):

```
$ docker-compose ps
NAME                    STATUS
wave-30-postgres-1      Up 10 seconds (healthy)
wave-30-redis-1         Up 10 seconds (healthy)
wave-30-backend-1       Up 16 seconds (healthy)
wave-30-frontend-1      Up 15 seconds
wave-30-adminer-1       Up 5 seconds
$ curl -sf http://localhost:8000/healthz
{"status":"ok"}                      # HTTP 200
```

End-to-end browser tests:

```
$ npx playwright test tests/e2e/ --workers=1
  7 passed (3.5s)
```

Alembic migration graph:

```
$ alembic -c src/backend/alembic.ini heads
0011 (head)  0018 (head)  0020 (head)  0021 (head)  0022 (effective head)
0023 (head)  0027 (head)
```

Live end-to-end business flow — walked via the real API as a real user would, with real
reference IDs generated this session (all `SWA-{year}-{TYPE}-{seq:03d}`):

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
- MinIO/S3 object storage and a Celery background worker — target-state, not live (see §4).
- Reforge/DPR document certification flow is role-gated in the code (Auditor+Designer) but has
  no dedicated UI screen.
- The full 21-sheet Excel import has been validated on the importer for its supported sheet
  types; the actual one-time migration run against real data is a go-live decision for Viraj
  (who runs it — see §7).

## 4. Known limitations, stated honestly

These are real and deliberately not hidden. None were discovered by the client first.

1. **Celery is installed but not implemented.** `celery==5.4.0` is in `requirements.txt` only;
   there is no Celery app, no worker, and no queue. Everything that *could* be async (PDF
   generation, report export, email) runs **synchronously** and returns when done. Verified this
   session: `grep -rn "celery" src/backend --include="*.py"` → zero code matches.
2. **File storage is local disk.** Uploads live in `uploads/` at the repo root. MinIO/S3 is not
   wired (documented as target-state in `docs/IT_BRIEF.md` Part 3 and `docs/conventions.md`).
   Backups must therefore cover the `uploads/` directory too (`make backup-files`).
3. **JWT is HS256, not RS256.** A single shared secret signs tokens; fine for an internal
   on-prem app, but if SWA ever needs token verification by a third party, RS256 is the target.
4. **Alembic migration graph has multiple heads.** Seven branch heads exist (see §2) and are
   resolved by `upgrade heads` on boot, which works and is what the deploy does. There are no
   merge migrations. Safe to operate, but a future cleanup should add merge points.
5. **Auth rate limiter is on by default (5 login/min per IP).** The dev compose file sets
   `DISABLE_AUTH_RATE_LIMIT=true` so test suites (7 logins in under a minute) don't get
   throttled. Production should keep the limiter on (or raise the limit if staff find it
   annoying over VPN/NAT where everyone shares one IP).
6. **Wave-24's full test run was blocked at the time** by a test-database deadlock from a prior
   session (environment issue, not code). That deadlock is long resolved — the suite has been
   run green (393/393) many times since, including twice today for this release.
7. **Migration 0026 cold-boot ordering bug** (found and fixed this session): on a fresh database
   the `documents` table could be missing when migration `0026` ran, because it lives on a
   sibling branch. Fixed by declaring `depends_on = "0022"`; verified with a full `down -v` cold
   boot. Also fixed this session: a missing `Notification` type import in the frontend API client
   (resolved to the DOM global, causing 7 `tsc` errors), and 37 `B008` FastAPI-DI lint items that
   had never received the repo's inline-`# noqa` convention.

## 5. The 2 open external blockers

Neither is resolvable in code. They are the only things standing between this build and a fully
production-live system, and both are **client-side**.

**A. Viraj's 3 open decisions** — `docs/decisions/0002-core-id-chain-gap.md`:
1. What is the 4th Service Agreement type/service name? (Sample row says `INSUDESIGN`; does not
   match the 3 verbally-named agreements.)
2. Does the yearly ID sequence reset on Jan 1, or run continuously across years? (Counter is
   built so this is a one-line config change either way.)
3. Is `LDI-*` really the legacy Inquiry ID, or a distinct concept? (No "Leads Sheet.xlsx" exists
   among the 21 source files.)

*If unanswered:* fields involved are free-text/nullable so nothing breaks; the year-reset
behavior defaults to "reset per year" (a design inference) and the importer maps `LDI-*` into
Inquiries (an assumption). Each could need a one-line correction later.

**B. IT/Vikrant's 8 answers** — `docs/IT_BRIEF.md`:
1. Docker license (Engine vs Desktop) · 2. WSL2/Linux containers · 3. Free ports · 4. HTTPS/cert
   source · 5. Existing backup process · 6. Internal web address · 7. Postgres/Redis in-compose
   vs native Windows · 8. How updates get deployed.

*If unanswered:* the production deployment cannot be configured correctly. `docker-compose.prod.yml`
and `.env.production.example` carry explicit `PENDING IT ANSWER (Q#)` markers for every value
that depends on these — the deploy **must not proceed** until they're filled (see §6).

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
| `README.md` | Entry point, quick start |
| `CHANGELOG.md` | Full release history (this release is `[1.0.0]`) |
| `plan/EXECUTION.md` | Wave-by-wave status (all 30 waves shipped) |
| `docs/DEPLOYMENT_CHECKLIST.md` | Production deploy steps (see §6) |
| `docs/IT_BRIEF.md` | The 8 IT questions + full deployment brief |
| `docs/decisions/0001..0004` | ADRs (tech stack, core ID chain, IT brief, meeting-2 flow) |
| `docs/runbook.md` + `docs/runbook_backup_restore.md` | Day-to-day ops + backup/restore |
| `docs/api.md`, `docs/conventions.md`, `docs/SCOPE_GUARD.md` | API reference, conventions, scope |
| `docs/PROJECT_HISTORY.md` | How the project got here (distilled history) |
| `resources/MEETINGS_MASTER.md` | Consolidated record of both client meetings |
| `resources/EXCEL_SHEETS_INVENTORY.md` | The 21 source sheets and their mapping |
| `deliverables/handover/` | `ADMIN_GUIDE.md`, `USER_GUIDE.md`, `TRAINING_ONE_PAGER.md`, `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` |
| `work/reports/wave-N/` | Per-wave verification reports (waves 1-30) |

## 9. Support / next steps

What a future developer picks up first:

1. Read `deliverables/SUBMISSION.md` (this file) → `HANDOFF.md` → `plan/EXECUTION.md`.
2. Resolve the two external blockers (§5) — send `docs/IT_BRIEF.md` to IT if not yet answered,
   and the ADR-0002 question list to Viraj.
3. Deploy per §6 and `docs/DEPLOYMENT_CHECKLIST.md` once IT answers land.
4. Run the Excel import (§7) against real data when Viraj confirms who owns the migration.
5. Highest-value engineering follow-ups, in order:
   - Add merge migrations to collapse the 7 Alembic heads (see §4.4).
   - Decide the year-reset ID policy once Viraj answers ADR-0002 Q2 (one config change).
   - Wire MinIO/S3 + a Celery worker to move PDF/export work off the request path (target-state).
   - (Already resolved, noted for the record: `tests/wave-22/test_rbac_gaps.py` exists and
     all 39 tests pass — an earlier draft of the wave-22 report incorrectly claimed the file
     was missing; it was created, then had real bugs the orchestrator found and fixed
     post-merge — see the "fix: post-merge verification catches" commit. No action needed.)

Everything else — the core chain, RBAC matrix, GST invoicing, compliance, time tracking, and
the backup/ops scripts — is verified working as of 2026-08-07 and ready to hand over.
