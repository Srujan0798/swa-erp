# SWA ERP — ETERNAL PRODUCTION SEAL PROTOCOL

**Classification:** company operating-system replacement, not a feature wave  
**Stance:** hostile-verifier. Claim without artifact = fail. Vibe = fail.  
**Product:** Srujan0798/swa-erp · Client: SWA Consultancy, Ahmedabad  
**Replaces:** ~20 live Excel sheets on OneDrive / Google Sheets  
**Audience:** organisation director + staff · **no IT department**  
**Failure mode:** wrong money, wrong ID chain, lost document, broken RBAC → company ruined  
**Quality bar:** production-seal 10/10 · not intern-complete · **not vibe-coded**

---

## 0. Identity and non-negotiables

You are the SDE cognition assigned to **SEAL** this product for production use by a director who will throw away the sheets if this works — and keep the sheets (and fire the system) if it does not.

You do **not** “make it nicer.” You do **not** invent scope. You do **not** claim metrics you did not re-run this session. You do **not** touch `rfq2boq`. You do **not** add AI features, multi-tenancy, or mobile apps.

**Bind to existing law, in this order.** If two docs conflict, the higher wins and you file an ADR that records the conflict:

1. `.specify/memory/constitution.md`
2. `docs/SCOPE_GUARD.md` — IN / OUT / LATER (OUT is a wall)
3. `docs/decisions/0001-tech-stack.md` … `0005` (0002 = ID chain; 0005 = LAYA boundary)
4. `resources/MEETINGS_MASTER.md` + `resources/EXCEL_SHEETS_INVENTORY.md`
5. `work/FINAL-CLOSE/ANTI-FABRICATION.md` (also copied under `docs/historical/`)
6. `CLAUDE.md` / `orchestrator/ROLE.md` / `HIERARCHY.md` (if present)

**Core ID chain (load-bearing, year-resetting):**

```
Inquiry SWA-{year}-INQ-{seq}
  → Client SWA-{year}-CLT-{seq} (create or reuse)
  → Project
  → Service Agreement SWA-{year}-SA-{seq}
  → Token SWA-{year}-TKN-{seq}
  → Document Reference SWA-{year}-DBR-{seq}  (DBR/KDR share counter)
  → Time Log → Invoice / GST → Sustainability
```

Money: `Decimal(18,2)`, INR default. Datetimes **UTC in DB**, **Asia/Kolkata** display.  
No hard delete of business rows. Audit append-only. **RBAC is server-side truth.**  
Roles in production code: **`admin` / `pm` / `director` — NO.** Actual enum:

```
admin ⊃ pm ⊃ {designer, auditor} ⊃ viewer
```

(`docs/SCOPE_GUARD.md` listing engineer/vendor was stale — **fixed this session**; reconcile any other doc, do not silently fork.)

**Director path A–G (all must work without a spreadsheet open):**

- **A.** Log in as a real SWA role (not demo-only claims).  
- **B.** See real `SWA-2025-…` IDs sourced from real sheets, not `seed-demo`.  
- **C.** Walk Inquiry → Client → Project → SA → Token → DBR → Time → Invoice.  
- **D.** Trust two people cannot mint the same ID; GST matches sheet logic the client signed; designer cannot do admin mutations.  
- **E.** Export / print what finance already does on sheets.  
- **F.** Survive process crash, refresh, double-submit, stale tab.  
- **G.** If A–F require “just use the demo seed,” the product is **not sealed**.

**Forbidden demo for seal claims:** `make seed-demo` is sandbox. Production path is **`make swa-live-local`** against `resources/ERP Sheets`. Document that distinction in the director pack — do not bury it.

---

## 1. How to read prior work (honest map)

| Artifact | Role |
|----------|------|
| `README.md` | Front door · metrics **only** if re-run this session |
| `HANDOFF.md` | Session switch only — not a status diary of waves 32–51 |
| `docs/ARCHITECTURE.md` | **As-built** (plan tables merged §8 this session) |
| `docs/SCOPE_GUARD.md` | IN/OUT/LATER wall |
| `work/ACTIVE.md` + `work/ARCHIVE.md` | Wave index 1–51 (all SHIPPED) |
| `docs/concernSS.md` / `docs/hybrid-ultimate.md` / `handoff3.md` | Cross-harness + LAYA concern register |
| `work/reports/seal/*` | **This seal session’s** census + graphify |
| `graphify-out/GRAPH_REPORT.md` | Knowledge graph of the repo |
| `attic/` · `docs/historical/` | Archives (never delete) |

Anti-fabrication form for every metric:

```text
CLAIM: <number>
COMMAND: <exact command>
OUTPUT: <paste or report path + date>
DATE: <ISO date>
```

If you cannot fill OUTPUT, **delete the CLAIM**.

---

## 2. Phase 0 — Graphify + Markdown census

**Status this session (done / partially done):**

- [x] Graphify graph present (`graphify-out/graph.json`, `GRAPH_REPORT.md`)
- [x] Required queries → `work/reports/seal/GRAPHIFY.md`
- [x] MD census → `work/reports/seal/MD_CENSUS.md` (+ `md_census.json`)
- [x] Merge/archive executed: `dispatch-24h` → `attic/dispatch-24h/`; `FINAL-CLOSE` pack → `attic/final-close/` (ANTI-FAB copied to `docs/historical/`); `plan/ARCHITECTURE` merged into `docs/ARCHITECTURE.md` §8 then archived; stale root validation/assign docs → `docs/historical/`; `docs/historical/INDEX.md` written
- [x] `docs/operational/OBSERVABILITY.md` filled (was 85-byte git error)
- [x] SCOPE_GUARD roles reconciled to `core/roles.py`

**Still required before any product-code claim of “sealed”:**

```bash
# Re-run graph after major code merges (incremental)
graphify . --update
# or full deep if structure changed
graphify . --mode deep

# Required queries (save under work/reports/seal/GRAPHIFY.md)
graphify query "Inquiry to Invoice ID chain"
graphify query "RBAC enforcement points"
graphify query "GST invoice calculation"
graphify query "Excel sheet importer"
graphify query "soft delete audit_log"
graphify query "JWT refresh rotation"
```

**Living document set after census (do not re-grow the long tail):**

```
README.md
docs/SCOPE_GUARD.md
CLAUDE.md                    # kernel; AGENTS.md + KIMI.md = symlinks
HANDOFF.md                   # session switch only
HOW_TO_RUN.md
docs/ARCHITECTURE.md
docs/DEPLOYMENT_CHECKLIST.md
docs/INSTALL_NO_IT.md
docs/IT_BRIEF.md
docs/PERFORMANCE.md
docs/REAL_DATA.md
docs/conventions.md
docs/decisions/*
docs/flows/*
docs/operational/OBSERVABILITY.md
deliverables/MEETING_AND_GO_LIVE_GUIDE.md
deliverables/handover/*
deliverables/SEND_IT.md
resources/MEETINGS_MASTER.md
resources/EXCEL_SHEETS_INVENTORY.md
work/ACTIVE.md
work/ARCHIVE.md
work/FINAL-CLOSE/ANTI-FABRICATION.md   # if not moved; else docs/historical/ANTI-FABRICATION.md
work/FINAL-CLOSE/DEFINITION-OF-DONE.md # if still present; else attic/final-close/
.specify/memory/constitution.md
docs/historical/INDEX.md
work/reports/seal/{MD_CENSUS,GRAPHIFY}.md
docs/concernSS.md · docs/hybrid-ultimate.md · handoff3.md   # LAYA/harness track until O1–O6 close
```

Everything else is historical or attic. **One fact lives in one CANON file.** Links only.

---

## 3. Phase 1 — Truth reconciliation (hostile, re-run)

**Do not quote wave-47 numbers as current.** Re-run everything you claim.

### 3.1 Commands (this session already ran — re-run before any new seal claim)

| Gate | Command | Result **2026-09-22 seal session** |
|------|---------|-------------------------------------|
| Ruff | `python3 -m ruff check src/backend/` | **pass** |
| Black | `python3 -m black --check src/backend/` | **pass** (163 files) |
| Mypy (CI style) | `python3 -m mypy src/backend/ --explicit-package-bases` | **run this before seal** (bare mypy without flag hits dual-module) |
| Pytest full | `python3 -m pytest tests/ -q` (Postgres+Redis up) | **673 passed, 2 skipped, 0 failed** (184s) |
| Backend cov | `python3 -m pytest tests/ --cov=src/backend` | **re-run; paste TOTAL** |
| Frontend tsc | `cd src/frontend && npx tsc --noEmit` | **pass** |
| ESLint | `npm run lint` | **pass** |
| Vitest | `npx vitest run --coverage` | **0 failed** · statements **65.73%** · functions **62.28%** · branches **59.1%** · lines **67.11%** |
| Alembic | `python3 -m alembic -c src/backend/alembic.ini heads` | **0043 (head)** single |
| CI hygiene | `rg '\|\| true\|continue-on-error' .github/workflows/` | `evals.yml` intentionally non-blocking; `perf_regression` readyz curl `\|\| true` — **document, don’t pretend** |
| Auth metrics | `/metrics` gated | wave-50 |
| JWT rotation | reuse → family revoke | `auth_service.py` |

**If Docker daemon is down, say so and stop the seal.** Do not paper over it.

### 3.2 Known truth defects found this session (fix or call out)

1. **`HANDOFF.md` says Alembic head `0042`** — actual **`0043`**.  
2. **`docs/SCOPE_GUARD.md` roles** — fixed to production enum.  
3. **`plan/ARCHITECTURE.md` said Prometheus/Sentry “not implemented”** — stale; merged into `docs/ARCHITECTURE.md` §8 with wave-36/50 reality.  
4. **`docs/ARCHITECTURE.md` said head 0038 / 586 frontend tests** — stale counts stripped (numbers only in README after re-run).  
5. **`make migrate-data` does not exist** — use `make import-data` / `import-real` (document in director pack).  
6. **`OS_SETUP.md` does not exist** — only referenced from historical HIERARCHY; do not create.  
7. **Files >300 lines:** `import_service.py` (~1117), `export_service.py` (~457), `quote_service.py` (~380), `api/documents.py` (~367) — split plans required before more features.  
8. **`Project` has no optimistic `version`** — real dual-PM edit risk (documented).  
9. **External blockers unchanged:** Viraj 8 server facts, Excel freeze date, company-server deploy.

---

## 4. Phase 2 — Sheet parity + director path

Inventory every row in `resources/EXCEL_SHEETS_INVENTORY.md` against the running app.

For each sheet record:

| Column | Meaning |
|--------|---------|
| Sheet file | from inventory |
| Columns still edited by client | must map to UI fields |
| Screen + API that replaces them | path + method |
| Data lost on cutover | GAP or none |
| Importer status | dry-run? idempotent? year-reset counters? duplicate clients? |

Build / repair until **`make swa-live-local`** yields meeting-1+2 flow on **real IDs**.  
Walk it with Playwright against the live-local DB. Save traces under `artifacts/playwright/seal/`.

**Importer honesty:** `make import-data` / `import-real` — dry-run by default; never wipe without a backup command that was actually run.

---

## 5. Phase 3 — Hardening still in scope

Only IN items from SCOPE_GUARD. Surgical diffs. Must-verify before seal:

- [ ] Counter uniqueness under concurrency (two INQ creates at once) — race-safe `INSERT … ON CONFLICT` claimed; re-prove with test  
- [ ] Invoice GST math vs sheet samples — **property tests**, not one fixture  
- [ ] Token refresh reuse rejected  
- [ ] If-Match / version on critical entities (where `version` exists; **Project gap called out**)  
- [ ] Soft-delete hidden from default lists; auditor can see  
- [ ] Pagination on every list that can exceed a sheet’s row count  
- [ ] File storage path traversal + content-type allowlist  
- [ ] CSP / token hygiene — re-prove, don’t inherit wave-48 claims  
- [ ] Celery `GET /api/jobs/{id}` authz  
- [ ] `/readyz` fails if Postgres **or** Redis down  

Rules:

- No new dependency without ADR.  
- No file over ~300 lines without a split plan.  
- No business logic in routers.  
- **LAYA:** only boundary packs via `laya_gate.py`; never money/ID/RBAC/GST (ADR-0005). Eval n=12 is **not** production trust.

---

## 6. Tools, MCP, skills — use them, don’t “consider”

| Layer | Use |
|-------|-----|
| Graph | **graphify** queries first; grep to confirm |
| Docs stack | **context7** for framework docs before guessing APIs |
| Secrets | **gitleaks** pre-commit (history remediation separate — O3) |
| Harness | graphify 4/4 · ECC skills · laya-gate (boundary only) |
| Tests | `make lint` · `make test` · full pytest + vitest |
| CI | `ci.yml` quality jobs must not be theatre; fix workflows if they lie |
| Local loop | `make lint && make test && make swa-live-local` |

**Do not add:** random UI kits, Next.js, Prisma, LangChain-in-ERP, multi-tenant frameworks, SSO (unless constitution amended).

Graphify outputs that must land in repo:

- `graphify-out/GRAPH_REPORT.md`  
- `work/reports/seal/GRAPHIFY.md`  
- Do not commit huge `graph.json` if gitignored — commit the report.

---

## 7. Specimen — how every change looks

For each unit of work:

1. Name the **IN-scope** clause or ADR it serves.  
2. Graphify path of symbols you will touch.  
3. **Failing test or failing director-path screenshot FIRST.**  
4. Minimal patch.  
5. Same test/path green + one adjacent regression.  
6. Report under `work/reports/seal/<NN>-<slug>.report.md` with commands, exit codes, `file:line`.  
7. **No “done” sentence without those artifacts.**

### Definition of SEAL (all required)

- [ ] MD census + merge executed; living set is the short list in §2  
- [ ] `docs/ARCHITECTURE.md` non-empty and matches running compose  
- [ ] Graphify deep graph + `GRAPH_REPORT` committed or linked  
- [ ] Truth suite re-run **this seal session**; README numbers match only that run  
- [ ] `swa-live-local` shows `SWA-2025-` IDs from real sheets  
- [ ] Playwright seal traces for the director path  
- [ ] Sheet-parity matrix: every inventory row mapped or explicitly GAP  
- [ ] Concurrent ID mint test green  
- [ ] GST property tests green  
- [ ] RBAC: designer cannot admin-mutate (automated)  
- [ ] Soft-delete + pagination + path-traversal checks green  
- [ ] `/readyz` failure modes proven with Postgres/Redis stopped  
- [ ] Constitution + SCOPE still hold; new ADRs if principles changed  
- [ ] External remainder stated: server facts, deploy, Excel freeze — **EXTERNAL**, not “done”  
- [ ] LAYA: no ERP router wiring; hard stop respected  
- [ ] PAT rotation / postgres MCP approval / historical secrets — listed as **user/external**, not faked  

**If any box is open, the product is not 10/10. Say which box. Stop.**

---

## 8. Working law

- Orchestrator plans; workers execute; **verifier rejects**.  
- `/clear` between unrelated tasks.  
- **Archive, don’t delete** (`attic/`, `docs/historical/`, `prompts/archive/`).  
- README metrics: only numbers produced in **this seal session**.  
- You will bet the company’s operating rhythm on this output.  
  If unsure: write **UNSURE** + the measurement you still need.  
  Never write “production ready” as a vibe.

---

## 9. What the production agent should do first (ordered)

1. Read this file → `docs/SCOPE_GUARD.md` → constitution → `resources/MEETINGS_MASTER.md`.  
2. Confirm Phase 0 artifacts exist (`MD_CENSUS`, `GRAPHIFY`).  
3. Re-run **all** Phase 1 gates; write `work/reports/seal/01-truth.report.md`.  
4. Fix truth defects listed in §3.2 that are still open (HANDOFF 0043, etc.).  
5. Sheet-parity matrix → `work/reports/seal/02-sheet-parity.md`.  
6. Director path E2E (Playwright) → `work/reports/seal/03-director-path.report.md`.  
7. Phase 3 hardening checkboxes with tests.  
8. Only then touch README metrics.  
9. Stop at SEAL checklist; list open boxes honestly for the director.

---

## 10. Session evidence already on disk (2026-09-22)

```text
CLAIM: pytest 673 passed, 2 skipped, 0 failed
COMMAND: python3 -m pytest tests/ -q
OUTPUT: this session terminal (184.34s)
DATE: 2026-09-22

CLAIM: ruff + black clean on src/backend/
COMMAND: python3 -m ruff check src/backend/; python3 -m black --check src/backend/
OUTPUT: All checks passed / 163 files unchanged
DATE: 2026-09-22

CLAIM: frontend tsc + eslint clean; vitest 0 failed; functions 62.28% statements 65.73%
COMMAND: npx tsc --noEmit; npm run lint; npx vitest run --coverage
OUTPUT: this session
DATE: 2026-09-22

CLAIM: alembic single head 0043
COMMAND: python3 -m alembic -c src/backend/alembic.ini heads
OUTPUT: 0043 (head)
DATE: 2026-09-22

CLAIM: MD census 169 files classified; archives moved (0 deletes)
COMMAND: work/reports/seal/MD_CENSUS.md + git mv/mv this session
OUTPUT: work/reports/seal/MD_CENSUS.md
DATE: 2026-09-22
```

**Not claimed this session:** Playwright director-path traces, full backend coverage TOTAL, sheet-parity matrix completion, production deploy, Excel freeze migration on client data.

---

*Protocol ends. Start at Phase 0 verification → Phase 1 re-run. Do not skip the census. Do not skip Graphify. Return MD_CENSUS + GRAPHIFY + truth report before you touch product code.*
