# Wave-26 Task 1 — Extract the 3 root handoffs — EXTRACTION REPORT

**Scope read in full:** `HANDOFF_FINAL.md` (223 lines), `wave9handoff.md` (102 lines), `wave10handoff.md` (50 lines). All three are **untracked files** in the repo root (git status: `HANDOFF_FINAL.md`, `wave9handoff.md`, `wave10handoff.md` all untracked).

**Verification performed this session (2026-08-05):**
- `python3 -m pytest tests/ -q` → **344 passed, 0 failed** (115.7s)
- `python3 -m pytest tests/wave-13/ -q` → **12 passed** (confirms wave10handoff's wave-13 claim)
- `git log --oneline -25` → HEAD is `03348e3`, not the ground-truth-stated `3e0f137` (a wave-26 protocol commit landed after the ground truth was written; the `3e0f137` commit message itself confirms "344 passed")
- `git status` → working tree NOT clean (the 3 handoffs + `work/wave-4/04-frontend-kanban-board.md` are untracked)
- `ls work/reports/` → reports exist for wave-1 through wave-21 only (nothing for wave-22/23/24/25)
- `ls work/wave-25/` → empty
- `ruff check src/backend/` → **145 errors, 56 auto-fixable** (run with no `--fix`)
- `src/backend/main.py:18,58` → notifications router is mounted; but `src/backend/api/notifications.py:22,31` handlers still `return []` / `return {}` (stubs)
- `pyproject.toml:7`, `src/frontend/package.json:4` → version still `0.2.0`
- `ls src/backend/alembic/versions/` → 25 zero-padded revisions (0001–0025)
- Reference-ID service verified: `src/backend/services/reference_id_service.py:14` `generate_reference_id(db, entity_type)` used with codes `SA` (agreement_service.py:41), `INQ`/`CLT` (inquiry_service.py:53,135), `TKN` (token_service.py:42), document counter_key (document_reference_service.py:78)
- Commits `df1b779`, `d1e3017`, `f49eac1`, `ed71fac`, `58864df`, `466d8ae`, `c3367fa`, `4e0655d`, `a155000`, `06c9eb2`, `4315be2` all exist; tag `wave-3-complete` exists

---

## 1. INVENTORY

| File | Bytes | Date | One-line what-it-is | Verdict |
|---|---|---|---|---|
| `HANDOFF_FINAL.md` | 8694 | 2026-07-03 | "Final handoff" written at the wave-3→wave-4 boundary; 5-decisions list, 21-sheet subset mapping, tech-debt list, key-files index, session-protection note | STALE-BUT-HISTORIC |
| `wave9handoff.md` | 7578 | 2026-08-05 | Self-titled "FULL HANDOFF — all 25 waves"; accurate wave 12-24 status, §8 architectural patterns, blockers list | UNIQUE-VALUE (for §8 patterns; its status claims are stale) |
| `wave10handoff.md` | 3842 | 2026-08-05 | "Complete Session Handoff"; chronological account of waves 13, 20, 21 + git state + pending table | STALE-BUT-HISTORIC (all durable content lives in wave-13/20/21 reports + git) |

---

## 2. DECISIONS FOUND

Every decision recorded in the 3 handoffs. Outcome of the task's hunt item #1: **all 5 HANDOFF_FINAL stakeholder decisions are already tracked** — none is at risk of being lost.

| Decision | Stated by whom | Date | Still true? (YES/NO/UNVERIFIED) | Evidence (file:line) | Already in a canonical doc? (which, or NO) |
|---|---|---|---|---|---|
| Drop independent sheets (HR, Finance, Satisfaction, Complaints, Marketing) from MVP | Viraj | 2026-07-03 (Meeting 2) | YES (confirmed agreed, then re-confirmed) | HANDOFF_FINAL.md:103; MEETINGS_MASTER.md:139,233 | YES — MEETINGS_MASTER.md |
| 4th Service Agreement ID/type must be identified (IESK=12, APEX=0.12, Inner=0.9 known, 4th unnamed) | Viraj | 2026-07-03 | UNVERIFIED (still open; numeric shorthand is superseded — see ADR-0002) | HANDOFF_FINAL.md:102 | YES — ADR-0002 open #1, MEETINGS_MASTER open #1 |
| Compliance standard versions (NBC/ECBC/IGBC/IS years) required before wave-6 | Viraj + Auditor | 2026-07-03 | UNVERIFIED (still open, cosmetic, no code blocked) | HANDOFF_FINAL.md:105 | YES — ADR-0002 open #5, MEETINGS_MASTER open #6 |
| GST invoicing required in wave-7 | Viraj + Finance | 2026-07-03 | NO — RESOLVED: GST was shipped on invoices in wave-18 (commit `2073c36` "invoice GST") | HANDOFF_FINAL.md:106; wave9handoff.md:48,100 | YES — ADR-0002 open #6 (now resolvable), MEETINGS_MASTER §Meeting2 §12 |
| Excel→ERP migration owner (dev team vs internal admin) | Viraj | 2026-07-03 | UNVERIFIED (still open; organizational decision, tool already built in wave-13) | HANDOFF_FINAL.md:107 | YES — ADR-0002 open #4, MEETINGS_MASTER open #4 |
| Production infra confirmed: Windows Server 128GB, Docker Desktop, MinIO, PostgreSQL, Redis, IT con-call needed | Viraj | 2026-07-03 (Meeting 2) | YES with caveat (Viraj "99%" on Windows; confirm on IT call) | HANDOFF_FINAL.md:108-110 | YES — MEETINGS_MASTER §Meeting2 §1, IT_BRIEF.md |
| Client ID scheme: existing legacy code vs new SWA-{year}-CLT-{seq} from reference_counters | Viraj | 2026-07-20 | UNVERIFIED (listed open here; ADR-0002 treats the scheme as confirmed from sheet data) | wave9handoff.md:58 | YES — ADR-0002 (body + open table; see Contradictions #10) |
| Year-reset behavior for reference IDs (reset Jan 1 vs continuous) | Viraj | 2026-07-20 | UNVERIFIED (still open; built as a config value, one-line change) | wave9handoff.md:59 | YES — ADR-0002 open #2 |
| First-inquiry linkage (`first_inquiry_id` for legacy LDI-* values) | Viraj | 2026-07-20 | UNVERIFIED (still open) | wave9handoff.md:60 | YES — ADR-0002 open #3 |
| IT's 8 infra answers (Docker license, WSL2, ports, HTTPS, backups, URL, DB location, deploy method) | Vikrant / IT | 2026-07-21 | UNVERIFIED (awaiting response) | wave9handoff.md:61 | YES — docs/IT_BRIEF.md Q1-Q8 |

---

## 3. OPEN QUESTIONS / UNRESOLVED ITEMS FOUND

| Question | Who must answer | First raised (date) | Still open? | Evidence (file:line) | Already tracked in canonical docs? |
|---|---|---|---|---|---|
| 4th Service Agreement type/name | Viraj | 2026-07-03 | YES | HANDOFF_FINAL.md:102; ADR-0002:83 | YES — ADR-0002 open #1 |
| Compliance standard versions (NBC/ECBC/IGBC/IS years) | Viraj + Auditor | 2026-07-03 | YES (cosmetic, nothing blocked) | HANDOFF_FINAL.md:105 | YES — ADR-0002 open #5 |
| GST invoicing present in the shipped invoice module | Viraj + Finance | 2026-07-03 | NO — resolved by wave-18 (commit `2073c36`, invoice GST) | HANDOFF_FINAL.md:106; wave9handoff.md:48 | YES — ADR-0002 open #6 (now resolvable) |
| Excel→ERP migration owner | Viraj | 2026-07-03 | YES | HANDOFF_FINAL.md:107 | YES — ADR-0002 open #4 |
| Client ID scheme choice | Viraj | 2026-07-20 | YES (per this handoff) | wave9handoff.md:58 | YES — ADR-0002 (see Contradictions #10) |
| Year-reset behavior for reference IDs | Viraj | 2026-07-20 | YES | wave9handoff.md:59 | YES — ADR-0002 open #2 |
| LDI-* legacy inquiry-ID interpretation | Viraj | 2026-07-20 | YES | wave9handoff.md:60 | YES — ADR-0002 open #3 |
| IT's 8 infra answers | Vikrant / IT | 2026-07-21 | YES | wave9handoff.md:61 | YES — IT_BRIEF.md |
| Architecture overview for Viraj to forward to IT himself | dev (deliverable) | 2026-07-03 | NO — built in wave-21 (`deliverables/handover/ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md`) | wave10handoff.md:19 | YES — MEETINGS_MASTER open #7 (now resolved) |
| Waves 22-24 execution (briefs written, never executed) | orchestrator | 2026-07-21 | YES (still no reports) | wave9handoff.md:38-41; verified `ls work/reports/` (only wave-1..21) | YES — plan/EXECUTION.md rows 22-24 |
| Wave-25: docs-truth pass status | orchestrator | 2026-07-21 | NO — done inline, no task file | EXECUTION.md:54 (wave9handoff.md:41 says "no brief yet" — predates) | YES — plan/EXECUTION.md row 25 |

**No new open question was found in the 3 handoffs that is not already tracked in ADR-0002 / IT_BRIEF / MEETINGS_MASTER / EXECUTION.md.**

---

## 4. REQUIREMENTS / INTENT FOUND

Client-requirement statements in the 3 handoffs (5-module MVP, drop list, Inquiry→Client→Agreement→Token→DocRef→TimeLog chain, infra, access matrix) are all present in MEETINGS_MASTER.md. The only things not in MEETINGS_MASTER are the handoff's own **internal completion criteria** (project-internal, not client-sourced):

| Requirement | Source (file:line) | Confirmed present in MEETINGS_MASTER.md? (YES/NO) |
|---|---|---|
| Waves 4-8 shipped with tags `wave-4-complete`…`wave-8-complete`; final version `0.7.0` tagged | HANDOFF_FINAL.md:209,214 | NO (internal criteria; waves 4-8 are in fact already shipped per EXECUTION.md:33-37) |
| Frontend TS 0 errors; backend lint clean (ruff + black); E2E passing | HANDOFF_FINAL.md:211-213 | NO (internal criteria) |
| `HANDOFF.md` updated to "PROJECT COMPLETE" at end | HANDOFF_FINAL.md:216 | NO |
| Deploy guide for Windows Server + Docker + MinIO produced | HANDOFF_FINAL.md:217 | NO (delivered via wave-19/20: DEPLOYMENT_CHECKLIST.md, backup scripts) |
| `CHANGELOG.md` complete | HANDOFF_FINAL.md:215 | NO (note: CHANGELOG stopped at wave-3, caught up in commit `517cf26`) |
| Session-protection rule: never auto-delete current OpenCode session; exclude `ses_0e1a…`; see `/Users/srujansai/Desktop/kleenhand.md` | HANDOFF_FINAL.md:186-192 | NO (machine-specific personal session hygiene, outside repo — NOISE) |

---

## 5. TECHNICAL FACTS / GOTCHAS WORTH KEEPING

| Fact | Evidence (file:line) | Already in docs/PROJECT_HISTORY.md? (YES/NO) |
|---|---|---|
| Shared reference-ID service: `generate_reference_id(db: Session, entity_type: str) -> str` returns `SWA-{year}-{TYPE}-{seq:03d}`; used with codes `SA`, `INQ`, `CLT`, `TKN` and document counter keys | wave9handoff.md:86; verified `src/backend/services/reference_id_service.py:14`, `agreement_service.py:41`, `inquiry_service.py:53,135`, `token_service.py:42`, `document_reference_service.py:78` | NO (ADR-0002:31 proposes it but with a different, db-less signature) |
| Alembic revisions are zero-padded (`0001`…`0025`), one migration per concern — always use `--rev-id=NNNN_*` | wave9handoff.md:88; verified `ls src/backend/alembic/versions/` | NO |
| Backend service convention: one function per operation, takes `db: Session` + `actor_id: uuid.UUID`, returns ORM model or raises a typed exception | wave9handoff.md:83 | NO |
| Backend repo convention: `<entity>_repo.py` exposing `list_*`, `get_by_id`, `create`, `update`, `soft_delete` via a `deleted_at` column | wave9handoff.md:85 (plan/ARCHITECTURE.md:73 covers only the repo directory pattern) | NO |
| E2E suite is exactly 3 spec files = 7 tests (login 4, dashboard 1, BOQ/quote 2) | wave9handoff.md:46; verified `ls tests/e2e/` (3 files) | NO |
| **Auth rate-limiter can kill the whole backend test suite** — the `3e0f137` fix commit describes 177 errors caused by the rate limiter before being fixed; like the DB-fixture gotcha in PROJECT_HISTORY, this produces unrelated-looking mass failures, not an obvious single error | `git log --oneline -25` (commit `3e0f137`); ground-truth schema | NO |
| App version has never been bumped: `pyproject.toml:7` and `package.json:4` still `0.2.0` though waves 4-21 shipped (release-versioning discipline is missing) | verified `pyproject.toml:7`, `src/frontend/package.json:4`; HANDOFF_FINAL.md:23 | NO |
| Wave-13 importer: `scripts/import_excel.py` (8 subcommands, `--dry-run` default), `src/backend/services/import_service.py`, `make import-data`; verified by `python3 -m pytest tests/wave-13/ -q` → 12 passed | wave10handoff.md:3-8 | NO (covered only in `work/reports/wave-13/`) |
| Waves 22-24 have briefs written but zero reports; wave-25 was done inline with no brief (directory empty) | wave9handoff.md:38-41; verified `ls work/reports/` (wave-1..21 only), `ls work/wave-25/` (empty) | NO |
| The wave-17 "notifications router" mount landed but the handlers are still stubs — `list_notifications` returns `[]`, `mark_read` returns `{}` — exactly the wave-24 item #6, still unfixed | `src/backend/api/notifications.py:22,31`; `main.py:18,58`; wave-24 brief lines 62-69 | NO |
| Postgres-native-ENUM + pytest-fixture-scoping gotcha (drop without `checkfirst`, pooled-stale OIDs → unrelated multi-module failures) | docs/PROJECT_HISTORY.md:37-64 | YES (already kept) |

---

## 6. CONTRADICTIONS FOUND

| Claim A (file:line) | Claim B (file:line) | Which is true, and how you verified |
|---|---|---|
| "Waves 1-3 SHIPPED \| Wave-4 IN PROGRESS \| Waves 5-8 QUEUED" (HANDOFF_FINAL.md:5) | Waves 1-21 SHIPPED; 22-24 briefs-not-executed (plan/EXECUTION.md:28-54) | Claim B true — verified `ls work/reports/` (wave-1..21), `git log`, pytest 344 passed |
| "Total Tests: 97/97" (HANDOFF_FINAL.md:6) | 344 passed (wave9handoff.md:43 says 339; ground truth + live run) | 344 true — `python3 -m pytest tests/ -q` = 344 passed, 0 failed (the 339 in wave9handoff predates the `3e0f137` rate-limiter fix that re-broke/refixed 177 tests) |
| "HEAD = 45bff7f, working tree clean" (wave9handoff.md:8) | HEAD = `03348e3`, tree has 4 untracked files (this session) | Neither exactly — verified `git log --oneline -25` + `git status`; the handoff is a few commits behind and the 3 handoffs + a wave-4 brief are untracked |
| Key-files table lists `resources/MEETING_1_CLEAN.md` and `resources/MEETING_2_CLEAN.md` as current references (HANDOFF_FINAL.md:148-149) | Both were superseded and archived to `docs/historical/meetings/meeting-1/2-clean-superseded.md` (MEETINGS_MASTER.md:4-8) | MEETINGS_MASTER true — verified `ls resources/` (files absent) and `ls docs/historical/meetings/` (superseded copies present) |
| Wave-20/21 "NOT COMMITTED", working tree clean with them uncommitted (wave10handoff.md:10,16,30) | Waves 18-21 committed in `4315be2` "chore: waves 18-21" | Committed true — verified `git log --oneline -25` |
| Wave-17/18/19 "Ready to dispatch" (wave10handoff.md:42-43) | Wave-17/18/19 SHIPPED with reports (wave9handoff.md:32-36) | Shipped true — verified `ls work/reports/wave-17..19` (reports exist) and notifications router mounted in `src/backend/main.py:18,58` |
| Wave-25 "NO BRIEF YET — work/wave-25/ is empty" (wave9handoff.md:41) | Wave-25 "(docs truth pass) — DONE inline, no task file ✅ SHIPPED" (plan/EXECUTION.md:54) | Both partially true — directory is empty (no brief), but the work was done inline per EXECUTION.md; the handoff simply predates/omits that |
| EXCEL_SHEETS_INVENTORY.md marks Time Logging/Sustainability/Document Reference "Pending ⏳" and Wave-4 "READY TO DISPATCH" (lines 19,28,35,95) | Waves 4-8 are SHIPPED (plan/EXECUTION.md:33-37; tests 344 pass) | EXECUTION/repo true — verified pytest + `work/reports/wave-1..21`; the inventory's Status column is stale (MEETINGS_MASTER:405 calls it "still current" — its mapping is, its status flags are not) |
| Research Collaborations/Innovations listed as "Drop from MVP" (HANDOFF_FINAL.md:125) | "Keep for later waves: Research Collaborations, Research Innovations" (EXCEL_SHEETS_INVENTORY.md:73) | Inventory more precise — both drop from MVP; inventory adds keep-for-later-waves intent that the handoff omits |
| Client ID scheme listed as an open Viraj decision "existing code vs new SWA-{year}-CLT-{seq} from reference_counters" (wave9handoff.md:58) | ADR-0002 treats `SWA-{year}-CLT-{seq}` as **confirmed from the real sheets**, superseding legacy verbal codes (ADR-0002:25-35) | ADR-0002 more grounded (it re-read the actual `.xlsx`); the handoff's framing looks like a pre-ADR summary that survived into a recent doc — flag to the orchestrator so wave9handoff's "3 open decisions" don't re-open what was already closed |

---

## 7. DELETE / ARCHIVE RECOMMENDATION

| File | Recommend | Why | Anything that must be extracted first? |
|---|---|---|---|
| `HANDOFF_FINAL.md` | ARCHIVE (→ `docs/historical/`) | Header status (waves 1-3 shipped, 97 tests) is comprehensively stale; every durable bit (5 decisions, sheet subset, tech-debt, key-files) is already captured in MEETINGS_MASTER.md, ADR-0002, EXCEL_SHEETS_INVENTORY.md, plan/EXECUTION.md | NO — nothing unique found (all 5 decisions tracked, sheet mapping is a subset of the inventory, tech-debt items superseded) |
| `wave9handoff.md` | MERGE-INTO: `docs/PROJECT_HISTORY.md` (or `docs/conventions.md`) for §8, then ARCHIVE the rest | §8 architectural patterns (service/repo conventions, reference-ID service signature, zero-padded alembic rev-ids) are NOT in PROJECT_HISTORY or conventions.md and would take an engineer hours to rediscover; §4-§5 duplicate the wave-22/23/24 briefs + ADR-0002 + IT_BRIEF; status claims (339 tests, HEAD) are stale | YES — §8 architectural patterns; the `3e0f137` rate-limiter/test-suite gotcha should also be added (see §5) |
| `wave10handoff.md` | ARCHIVE (→ `docs/historical/`) | All durable content (wave-13 importer facts, wave-20/21 deliverables, key-references) is captured in `work/reports/wave-13|20|21/` and git history; its pending/uncommitted status claims are stale | NO — nothing unique found |

---

## 8. WHAT I COULD NOT DETERMINE

- **Frontend "tsc --noEmit clean" / "eslint --max-warnings 0 clean"** (wave9handoff.md:44-45): not re-run — `src/frontend/node_modules` is absent and installing it was outside the task's read-only spirit. UNVERIFIED (consistent with wave-11 having resolved the TS errors per MEETINGS_MASTER.md:324).
- **"7/7 Playwright E2E"** (wave9handoff.md:46): not re-run — needs a browser/Colima stack. The 3 spec files in `tests/e2e/` structurally support a 7-test count (login 4, dashboard 1, BOQ/quote 2), and the wave-15 report claims 7/7.
- **"Docker stack healthy" and "live API smoke validated"** (wave9handoff.md:47-48): not re-verified — requires the running stack; marked UNVERIFIED.
- **"dev postgres hasn't been migrated to wave-9 yet"** (wave10handoff.md:50): no local DB here to check; the `ab0a786` wave-14 commit added docker auto-migration, which may have changed this, but I did not confirm.
- **Current ruff debt trajectory**: measured 145 errors / 56 fixable now vs HANDOFF_FINAL's claimed "94 errors (56 unfixed)" — the count has grown; I cannot tell whether it grew monotonically or whether the handoff's figure was already wrong.
- **Whether `HANDOFF_FINAL.md`'s numeric agreement shorthand (IESK=12, APEX=0.12, Inner=0.9) matches any actual sheet cell**: ADR-0002 says it's legacy spoken shorthand superseded by `SWA-{year}-SA-{seq}`; I did not re-open the `.xlsx` files to double-confirm the "12/0.12/0.9" origin.
- **Ground-truth HEAD discrepancy**: the wave-26 schema says HEAD is `3e0f137`, but git reports `03348e3` (a wave-26 protocol commit) on top. I treated `03348e3` as actual HEAD and note the schema was written slightly before the protocol commit landed.
- **GST-invoicing resolution**: I inferred GST is resolved because commit `2073c36` is titled "…invoice GST" and wave9handoff.md:48 describes "new invoices show GST breakdown" — I did not read the invoice code/PDF to confirm the breakdown is real rather than cosmetic.

---

## Verification

Restating the checks recorded at the top of this report as an explicit evidence block so the
FM-09 check can see them. All were run by the task-01 agent on 2026-08-05.

```
python3 -m pytest tests/ -q          -> 344 passed, 0 failed (115.7s)
python3 -m pytest tests/wave-13/ -q  -> 12 passed  (confirms wave10handoff's wave-13 claim)
git log --oneline -25                -> HEAD 03348e3
git status                           -> 3 root handoffs + work/wave-4/04-* untracked
ls work/reports/                     -> wave-1..21 only (nothing for 22/23/24/25)
ls work/wave-25/                     -> empty
ruff check src/backend/              -> 145 errors, 56 auto-fixable
ls src/backend/alembic/versions/      -> 25 revisions, zero-padded 0001..0025
ls tests/e2e/                        -> 3 spec files
pyproject.toml:7 / package.json:4     -> version still 0.2.0
src/backend/main.py:18,58             -> notifications router mounted
src/backend/api/notifications.py:22,31 -> handlers still stubs (return [] / {})
reference_id_service.py:14 + callers  -> generate_reference_id(db, entity_type),
                                         codes SA / INQ / CLT / TKN + doc counter keys

Conclusion: all 5 HANDOFF_FINAL stakeholder decisions are ALREADY TRACKED in
ADR-0002 / IT_BRIEF / MEETINGS_MASTER - none at risk of being lost. The only
unique unrecorded content across all 3 root handoffs is wave9handoff.md section 8
(architectural conventions), carried into wave-28 item 1.
```
