# Wave-26 Task 4 — Overlap/duplication map of ALL current docs — EXTRACTION REPORT

**Scope:** every non-archived markdown doc: root, `plan/`, `docs/`, `docs/decisions/`, `resources/`, `deliverables/handover/`, `orchestrator/**`, `.specify/`. Excluded: `docs/historical/`.

**Verification performed this session (2026-08-05):**
- `diff CLAUDE.md KIMI.md` → **no output; md5 identical (`e8b65c9845ecc11a9b8fb7d472c98d23`)** — they ARE byte-identical duplicates. Confirmed definitively.
- `git tag` → only `wave-3-complete` exists; **no `v0.3.0` tag**, yet `CHANGELOG.md` claims a `0.3.0` release (2026-07-20).
- `pyproject.toml:7` + `src/frontend/package.json:4` → version still `0.2.0` → contradicts CHANGELOG's `0.3.0`.
- `grep -rn "celery" src/backend/ --include="*.py"` → zero matches (Celery only in `requirements.txt`). `grep minio/boto3` → zero matches. No `exception_handler` in `src/backend/main.py`.
- `grep gst_amount src/backend/models/invoice.py` → `gst_amount: Mapped[Decimal]` exists (line 22) + migration `0025_add_invoice_gst.py` exists → **GST IS implemented**, contradicting `docs/conventions.md:39-45` and `orchestrator/memory/MEMORY.md:55`.
- `ls scripts/` → `backup_db.sh`, `backup_files.sh`, `restore_db.sh` exist; `ls tests/wave-19/` → `test_backup_scripts.py` exists; `ls work/reports/wave-19/` → report exists → **wave-19 landed**, contradicting `docs/runbook.md:85-89` and `deliverables/handover/ADMIN_GUIDE.md:61-71`.
- `ls .specify/specs/` → wave-1,2,3,4,9,10; wave-10/contracts is an **empty untracked dir** (so `.specify/STATUS.md`'s "nothing for wave-10" is effectively correct).
- `python3 -m pytest tests/ -q` (prior wave-26 run) → 344 passed; `git log` HEAD `03348e3`.
- `work/reports/wave-17..21` all have reports (waves 17-21 shipped).

---

## 1. INVENTORY

### Root
| File | Bytes | Date | One-line what-it-is | Verdict |
|---|---|---|---|---|
| `README.md` | 1938 | Jun 29 | Entry point, quick start, stack line, deliverables map | UNIQUE-VALUE |
| `CLAUDE.md` | 3847 | Jun 29 | Orchestrator kernel, auto-loaded (CLAUDE.md kernel) | UNIQUE-VALUE |
| `KIMI.md` | 3847 | Jun 29 | **Byte-identical copy of CLAUDE.md** (md5-equal, proven by diff) | DUPLICATE-OF:CLAUDE.md |
| `HANDOFF.md` | 6025 | Jul 21 | Live handoff protocol + state summary (status numbers stale: "324/324") | UNIQUE-VALUE |
| `HANDOFF_FINAL.md` | 8694 | Aug 5 | Agent "final handoff" written at wave-3 boundary; status wholly stale | STALE-BUT-HISTORIC |
| `HIERARCHY.md` | 5777 | Aug 5 | Repo map + ownership; already flags the 3 agent handoffs as PENDING CONSOLIDATION | UNIQUE-VALUE |
| `HOW_TO_RUN.md` | 2146 | Jun 29 | Dual-tier orchestrator/worker workflow in plain language | UNIQUE-VALUE |
| `CONTRIBUTING.md` | 1603 | Jun 29 | Contribution rules | UNIQUE-VALUE |
| `CHANGELOG.md` | 3215 | Jul 20 | Release history; **claims 0.3.0 that was never tagged/versioned** | UNIQUE-VALUE |
| `OS_SETUP.md` | 48809 | Jun 29 | Generic "OS-Setup v1.1 Universal Agentic Project Kickstart" template — not swa-erp-specific (provenance: copy of `~/Desktop/OS_SETUP.md` per HIERARCHY.md:14) | NOISE |
| `wave9handoff.md` | 7578 | Aug 5 | Agent "FULL HANDOFF — all 25 waves"; §8 architectural patterns are the only unique content | STALE-BUT-HISTORIC |
| `wave10handoff.md` | 3842 | Aug 5 | Agent session handoff (waves 13/20/21); content lives in wave reports + git | STALE-BUT-HISTORIC |

### plan/
| File | Bytes | Date | One-line what-it-is | Verdict |
|---|---|---|---|---|
| `plan/PRD.md` | 6061 | Jul 21 | Product spec; original waves-1-8 scope corrected to defer to SCOPE_GUARD | UNIQUE-VALUE |
| `plan/ARCHITECTURE.md` | 10720 | Jul 21 | Architecture: target diagram + verified reality (heavily corrected 2026-07-21) | UNIQUE-VALUE |
| `plan/EXECUTION.md` | 7959 | Jul 21 | Wave status table — the canonical status doc | UNIQUE-VALUE |

### docs/
| File | Bytes | Date | One-line what-it-is | Verdict |
|---|---|---|---|---|
| `docs/api.md` | 4800 | Jul 21 | API reference; points to Swagger as source of truth; corrected 2026-07-21 | UNIQUE-VALUE |
| `docs/conflict_resolution.md` | 1710 | Jun 29 | Authority precedence (constitution > ADRs > PRD > … > reports) | UNIQUE-VALUE |
| `docs/conventions.md` | 3835 | Jul 21 | Code/data/money/naming conventions; **2 stale claims (GST, error body shape)** | UNIQUE-VALUE |
| `docs/deployment.md` | 2416 | Jul 21 | Prod-deploy overview + pointer to the real config files | UNIQUE-VALUE (overlaps DEPLOYMENT_CHECKLIST) |
| `docs/runbook.md` | 3223 | Jul 21 | Local-dev ops + troubleshooting; **1 stale section (wave-19 "not landed")** | UNIQUE-VALUE |
| `docs/runbook_backup_restore.md` | 6901 | Jul 21 | Backup/restore runbook for the wave-19 scripts (accurate) | UNIQUE-VALUE |
| `docs/DEPLOYMENT_CHECKLIST.md` | 4748 | Jul 21 | Day-of deployment runbook (ops) | UNIQUE-VALUE |
| `docs/IT_BRIEF.md` | 8992 | Jul 20 | The 8 infra questions for IT — the sendable brief | UNIQUE-VALUE |
| `docs/PROJECT_HISTORY.md` | 7052 | Jul 20 | Distilled history + the ENUM/fixture gotcha | UNIQUE-VALUE |
| `docs/SCOPE_GUARD.md` | 4707 | Jul 21 | Canonical scope: shipped waves, out-of-scope, open items | UNIQUE-VALUE |

### docs/decisions/
| File | Bytes | Date | One-line what-it-is | Verdict |
|---|---|---|---|---|
| `0001-tech-stack.md` | 3457 | May 19 | ADR: tech stack selection (Accepted) | UNIQUE-VALUE |
| `0002-core-id-chain-gap.md` | 8283 | Jul 20 | ADR: the core-chain MVP discovery + 7 open items | UNIQUE-VALUE |
| `0003-it-server-call-brief.md` | 15233 | Jul 20 | ADR: IT call prep; **embeds a near-duplicate of IT_BRIEF.md's sendable text** | UNIQUE-VALUE |
| `0004-meeting-2-flow-and-next-steps.md` | 8476 | Jul 20 | ADR: Meeting-2 re-read → actions | UNIQUE-VALUE |

### resources/
| File | Bytes | Date | One-line what-it-is | Verdict |
|---|---|---|---|---|
| `resources/MEETINGS_MASTER.md` | 24899 | Jul 20 | Single source of truth for client requirements/decisions | UNIQUE-VALUE |
| `resources/EXCEL_SHEETS_INVENTORY.md` | 7351 | Jul 3 | 21-sheet → wave mapping; **Status column stale** (waves 6-8 marked Pending) | UNIQUE-VALUE |

### deliverables/handover/ (all client-facing)
| File | Bytes | Date | One-line what-it-is | Verdict |
|---|---|---|---|---|
| `ADMIN_GUIDE.md` | 5552 | Jul 21 | Admin procedures (users, import, backups, health); **1 stale wave-19 section** | UNIQUE-VALUE |
| `USER_GUIDE.md` | 3093 | Jul 21 | Per-role day-to-day walkthrough | UNIQUE-VALUE |
| `TRAINING_ONE_PAGER.md` | 1526 | Jul 21 | One-page getting-started | UNIQUE-VALUE |
| `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` | 2516 | Jul 21 | Plain-language architecture for Viraj to forward to IT | UNIQUE-VALUE |

### .specify/
| File | Bytes | Date | One-line what-it-is | Verdict |
|---|---|---|---|---|
| `STATUS.md` | 1203 | Jul 21 | Meta note: `.specify/specs/` is a historical record, not a live index | UNIQUE-VALUE |
| `steering.md` | 2013 | Jun 29 | AI coding rules — overlaps constitution + CLAUDE.md + rules/*.md | DUPLICATE-OF:constitution.md (overlapping content, distinct file) |
| `memory/constitution.md` | 73 lines | Jun 29 | Non-negotiable principles — top authority per conflict_resolution.md:7 | UNIQUE-VALUE |

### orchestrator/ (44 files — process apparatus, audience = orchestrator, all UNIQUE-VALUE, tiny)
| File | One-line what-it-is |
|---|---|
| `ROLE.md` (1808) | How the orchestrator thinks + works |
| `core/identity.md` (769) | Who the orchestrator is on this project |
| `core/dispatch-protocol.md` (1520) | How to write self-contained task files |
| `core/review-protocol.md` (1562) | How to review worker reports |
| `core/scope-guard.md` (3211) | Scope process rules (cross-refs docs/SCOPE_GUARD, no duplicated wave list) |
| `core/12-factor.md` (1337) | 12-factor agent principles |
| `core/5-patterns.md` (1630) | Anthropic 5 canonical patterns |
| `core/karpathy-rules.md` (1101) | Think/simplify/surgical/goal-driven |
| `core/governance.md` (1005) | T0-T3 risk tiering |
| `core/context-budget.md` (1186) | Token discipline |
| `commands/` (10 files, 479-912 B) | `/plan /dispatch /review /merge /ship /status /next /handoff /audit /reflect` — each a slash-command spec |
| `skills/` (13 files, 590-1315 B) | Orchestrator-only skills (write-task-file, plan-wave, review-report, merge-work, triage, to-prd, to-issues, status-report, diagnose, verify-work, zoom-out, caveman, self-evolve) |
| `agents/` (6 files, 589-1017 B) | Sub-agent specs (codebase-explorer, verifier, interviewer, brief-writer, deep-research, REGISTRY dispatch table) |
| `rules/` (4 files, 585-3345 B) | python / typescript / docs / security rules |
| `memory/MEMORY.md` (4021) | Living orchestrator memory; **2 stale claims (324/324, GST not implemented)** |

Note: `orchestrator/hooks/` (*.sh) and `recipes/` (*.yaml) are not markdown — excluded per scope. `work/` templates (WORKER_PROMPT/TASK_TEMPLATE/REPORT_TEMPLATE) are outside the listed scope but are the operative worker protocol; listed as a reference, not inventoried.

---

## 2. DECISIONS FOUND

| Decision | Stated by whom | Date | Still true? | Evidence (file:line) | Already in a canonical doc? |
|---|---|---|---|---|---|
| Tech stack frozen (Python/FastAPI/PG/React/Celery/Docker Compose) | Srujan + orchestrator | 2026-05-19 | YES (stack never changed) | 0001:10-101 | YES — ADR-0001 |
| The client's real MVP is the Inquiry→Agreement→Token→DocRef chain, not the wave-1-8 generic CRM | Orchestrator, from meeting data | 2026-07-20 | YES | 0002:10-18; SCOPE_GUARD:5-10 | YES — ADR-0002 + SCOPE_GUARD |
| MVP boundary = waves 1-13 (not waves 1-4) | Orchestrator | 2026-07-20 | YES | SCOPE_GUARD:9-10; CHANGELOG:32-35 | YES — SCOPE_GUARD |
| JWT HS256 only — RS256 never implemented despite original plan | Orchestrator (grep-verified) | 2026-07-21 | YES | ARCHITECTURE:129-133; 0003:21-25; MEMORY:51 | YES — ARCHITECTURE + ADR-0003 |
| Drop independent sheets (HR/Finance/Satisfaction/Complaints/Marketing) from MVP | Viraj | 2026-07-03 | YES | MEETINGS_MASTER:139,233; constitution:64-71 | YES — MEETINGS_MASTER |
| Never couple to rfq2boq (Project 1) | Viraj (caught the mix-up) | 2026-07-03 | YES | constitution:47; CLAUDE.md domain rules; 0004:62-66 | YES — constitution + MEETINGS_MASTER §9 |
| Production target = on-prem Windows Server, 128GB, VPN-only | Viraj | 2026-07-03 | YES (99%, confirm on IT call) | MEETINGS_MASTER §Meeting2 §1; deployment:13-15 | YES — MEETINGS_MASTER |
| Money = Decimal(18,2); datetimes UTC | constitution | 2026-05-19 | YES (one known float violation, wave-23) | constitution:17-18; MEMORY:53-54 | YES — constitution + conventions |
| Soft-delete via `deleted_at`, no hard deletes for business data | constitution | 2026-05-19 | PARTIAL — rule stands but code violates it (Task soft_delete hard-deletes; dead `deleted_at` columns) | constitution:20; MEMORY:42-44; wave-23 brief | YES — constitution (enforcement gap noted) |
| GST invoicing required → shipped | Viraj + Finance (decision), dev (impl) | 2026-07-03 → wave-18 | YES — implemented (model `gst_amount`, migration 0025) | invoice.py:22; 0025 migration | YES — but MEMORY:55 + conventions:39-45 still say NO (see §6) |
| Version bump + tag on every wave ship | orchestrator process | 2026-05-19 | NO — process never followed: only `wave-3-complete` tag; version still 0.2.0 | commands/ship.md:16-18; git tag; pyproject:7 | YES — commands/ship.md (rule) / CHANGELOG (reality diverges) |
| Architecture summary for Viraj to forward to IT | Viraj request | 2026-07-03 | YES — produced (wave-21) | 0004:91,96-100; handover/ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md | YES — 0004 action item + deliverable |

---

## 3. OPEN QUESTIONS / UNRESOLVED ITEMS FOUND

| Question | Who must answer | First raised (date) | Still open? | Evidence (file:line) | Already tracked in canonical docs? |
|---|---|---|---|---|---|
| 4th Service Agreement type/name | Viraj | 2026-07-03 | YES | 0002:83 | YES — ADR-0002 open #1 |
| Year-reset behavior for reference IDs | Viraj | 2026-07-20 | YES | 0002:84 | YES — ADR-0002 open #2 |
| Is `LDI-*` the legacy Inquiry ID? | Viraj | 2026-07-20 | YES | 0002:85 | YES — ADR-0002 open #3 |
| Excel→ERP migration owner | Viraj | 2026-07-03 | YES | 0002:86; 0004:89 | YES — ADR-0002 open #4 |
| Compliance standard versions (NBC/ECBC/IGBC/IS years) | Viraj + Auditor | 2026-07-03 | YES (cosmetic) | 0002:87 | YES — ADR-0002 open #5 |
| GST invoicing present in shipped module | Viraj + Finance | 2026-07-03 | NO — resolved (wave-18) | 0002:88; invoice.py:22 | YES — ADR-0002 open #6 (now resolvable) |
| Client portal timing | Viraj | 2026-07-03 | YES (deferred) | 0002:89; SCOPE_GUARD:47 | YES — ADR-0002 open #7 |
| IT's 8 infra answers (Docker license, WSL2, ports, TLS, backups, URL, DB location, deploy method) | Vikrant/IT | 2026-07-21 | YES | IT_BRIEF Q1-8; 0003:35-67 | YES — IT_BRIEF.md |
| Windows vs Linux on the server (Viraj "99%") | IT person | 2026-07-03 | YES — first question on the IT call | 0004:90; 0003:41-43 | YES — ADR-0004 |
| Task-dependency management has no API surface (model exists, no routes) | dev/orchestrator | 2026-07-21 | YES (real gap, not just a doc error) | api.md:61-64 | NO — only in api.md |
| `.specify/specs/` missing for waves 5-8 and 10-25 | orchestrator | 2026-07-21 | YES (by design — `work/wave-N/` replaced it) | STATUS.md:6-15 | YES — .specify/STATUS.md |
| Waves 22-24 briefs written but not executed | orchestrator | 2026-07-21 | YES | EXECUTION.md:51-53 | YES — plan/EXECUTION.md |
| Prometheus `/metrics` and Sentry — never implemented | dev | 2026-07-21 | YES (aspirational) | ARCHITECTURE:183-186 | YES — ARCHITECTURE |
| Celery/Redis "installed but not wired" | dev | 2026-07-21 | YES (future) | ARCHITECTURE_OVERVIEW:26-29; HIERARCHY:97-103 | YES — HIERARCHY + ARCHITECTURE_OVERVIEW |
| Version discipline: app still 0.2.0, no tag past wave-3 | orchestrator | 2026-08-05 | YES | CHANGELOG:8 vs pyproject:7 | NO — needs a decision |

---

## 4. REQUIREMENTS / INTENT FOUND

All client requirements restated across these current docs (5-module MVP, drop list, core chain, infra, access matrix, time logging outside project scope) trace back to and are present in `resources/MEETINGS_MASTER.md`. No new client requirement was found in any current doc that isn't already there. Items that are NOT in MEETINGS_MASTER are all internal/dev-side:

| Requirement | Source (file:line) | Confirmed present in MEETINGS_MASTER.md? (YES/NO) |
|---|---|---|
| GSTIN/HSN/SAC on invoices, PAN on client records | constitution:46 | NO (MEETINGS_MASTER only records GST invoicing as a to-confirm decision; the specific GSTIN/HSN/SAC fields are a dev-side principle, now partially implemented) |
| Performance budgets (API <500ms P95, page <1.5s, BOQ parse <30s) | constitution:33; PRD:52-56 | NO (internal quality targets, not client-specified) |
| Test coverage ≥75% on services | constitution:30 | NO (internal) |
| 15-min time-tracking increments; billable vs non-billable | CLAUDE.md domain rules; HANDOFF:96 | NO as an explicit client quote — MEETINGS_MASTER documents time logging but not the 15-min increment rule (verify before promoting) |
| Multi-currency-ready money | constitution:17; conventions:38 | NO as a client requirement (dev-side design default) |

---

## 5. TECHNICAL FACTS / GOTCHAS WORTH KEEPING

| Fact | Evidence (file:line) | Already in docs/PROJECT_HISTORY.md? (YES/NO) |
|---|---|---|
| Celery is declared (requirements.txt + architecture diagrams) but **zero Celery code exists** — no app, no `@task`, no worker service in either compose file | HIERARCHY:97-103; ARCHITECTURE_OVERVIEW:26-29; grep (0 matches) | NO |
| MinIO/S3 was **never built** — runtime storage is a flat `uploads/<id>/` dir at repo root, gitignored | conventions:13-22; MEMORY:59-60; grep (0 matches) | NO |
| RS256 JWT, Prometheus `/metrics`, Sentry, HTTPS-only cookies, refresh-token rotation, "security gates that block" were all **documented as built but never implemented** | MEMORY:25-29; ARCHITECTURE:129-133,183-186; 0003:21-25 | NO |
| The **auth rate-limiter can kill the whole test suite** (commit `3e0f137` fixed 177 errors caused by it) — same class as the DB-fixture gotcha: unrelated-looking mass failures, fix is never in the failing module | git log `3e0f137` (cross-referenced in wave-26 task 01) | NO |
| Postgres-native-ENUM + pytest fixture scoping gotcha (drop without `checkfirst`, pooled stale OIDs → multi-module mass failures) | PROJECT_HISTORY:37-64; MEMORY:32-37 | YES |
| This test suite false-fails under process/DB contention (stray pytest racing on `DROP SCHEMA public CASCADE` against shared `swa_erp_test`) — reset DB / kill stray processes before trusting a failure count | MEMORY:32-37 | PARTIAL (MEMORY only) |
| Error-response shape is NOT `{detail, code, request_id}` — no custom exception handler exists; `code` is absent, `request_id` is a header only | api.md:14-17; grep main.py (no handler); contradicts conventions.md:61 | NO |
| GST shipped in wave-18: `Invoice.gst_amount` column (Numeric(18,2), default 0) + migration `0025_add_invoice_gst.py` | invoice.py:22; ls alembic/versions/ | NO |
| `audit_log` append-only table is real and working (every mutation logged) | ARCHITECTURE:187-188 | NO |
| Soft-delete is unreliable across modules: several `deleted_at` columns never used, and `Task.soft_delete()` is actually a hard delete | MEMORY:42-44; wave-23 brief | NO |
| Shared reference-ID service `SWA-{year}-{TYPE}-{seq:03d}` is atomic/race-safe | MEMORY:57-58 | NO |
| `.specify/specs/` only covers waves 1-4 (+ orphaned wave-9); `work/wave-N/` + `work/reports/wave-N/` is the real spec/report trail since wave-9 | STATUS.md:6-15 | NO |
| Only tag is `wave-3-complete`; version pinned at 0.2.0 in both pyproject and package.json despite waves 4-21 shipping | git tag; pyproject:7; package.json:4 | NO |

---

## 6. CONTRADICTIONS FOUND

| Claim A (file:line) | Claim B (file:line) | Which is true, and how you verified |
|---|---|---|
| `CLAUDE.md` and `KIMI.md` are the same file | They are maintained as two files, inviting divergence | Identical — `diff` empty, md5 equal. They are a deliberate alias (HIERARCHY:8, HANDOFF:50) but any single-file edit silently breaks the alias. True answer: **duplicate, must be a symlink or sync-checked** |
| "324/324 backend tests" (HANDOFF.md:10; MEMORY.md:12) | 344 passed (ground truth + live `pytest`) | 344 true — 3e0f137 fixed the rate limiter after those docs were written |
| "0.3.0 — 2026-07-20" released (CHANGELOG.md:8) | version still 0.2.0, no v0.3.0 tag (pyproject:7; git tag) | CHANGELOG false as a release — no tag, no version bump; only the changelog entry exists |
| "GST is not implemented on invoices (generic tax_rate/tax_amount only)" (MEMORY:55) and "GST: not yet implemented as of 2026-07-21" (conventions:39-45) | `Invoice.gst_amount` column exists + migration 0025 `add_invoice_gst` + wave-18 commit `2073c36` | MEMORY/conventions false — GST landed in wave-18; verified by grep + migration list + commit message |
| "Errors: {detail, code, request_id} always" (conventions:61) | "`code` doesn't exist in the body at all" (api.md:14-17) | api.md true — no exception handler in main.py (grep); `request_id` is header-only |
| "wave-19 ... had not landed ... none of those scripts exist in `scripts/`" (runbook.md:85-89) and "wave-19 is still ready to dispatch ... not been built yet" (ADMIN_GUIDE.md:61-71) | `scripts/backup_db.sh|backup_files.sh|restore_db.sh` exist, `tests/wave-19/` exists, `work/reports/wave-19/` report exists, `docs/runbook_backup_restore.md` documents them | runbook.md + ADMIN_GUIDE false — wave-19 landed; verified `ls` of scripts/tests/reports |
| Four docs each claim to be "the handoff" with conflicting state: HANDOFF.md (Jul 21), HANDOFF_FINAL.md ("wave-4 in progress, 97/97"), wave9handoff.md ("339/339, HEAD 45bff7f"), wave10handoff.md ("waves 20/21 uncommitted") | plan/EXECUTION.md (waves 1-21 shipped, 344 tests) | EXECUTION.md + repo true — pytest 344, reports wave-1..21 exist, commits for 18-21 present; the three agent handoffs are stale snapshots |
| Architecture diagram shows "Redis (Celery + cache)" and "Celery (workers)" boxes plus a "Celery worker crashes" failure point (ARCHITECTURE:21-28,152,159) | "no Celery app, no `@task`, no worker service in either compose file" (HIERARCHY:97-103) | HIERARCHY true — grep found zero Celery code; the ARCHITECTURE diagram/integration rows are target-plan, not reality (the doc's own "Updated 2026-07-21" sections are honest, the top diagram is not) |
| "Storage: Local filesystem (dev) → MinIO/S3 (prod)" + "Celery" (README:38-42) | "zero MinIO code anywhere" + "no data/ dir" (conventions:13-22; HIERARCHY:97-103) | conventions/HIERARCHY true — grep 0 matches; README states the plan as a forward-looking line, which misleads |
| "Every task has runnable tests in `contracts/`" (constitution:21) | most waves (5-8, 10-25) have no contracts (STATUS.md:6-15) | STATUS.md true for reality; constitution states the ideal, currently unenforced |
| "Workers ... can run 4-6 tasks in parallel" and ship/merge flow (HOW_TO_RUN.md:26,31-42) | `/ship` steps "Bump version", "Create git tag wave-N-complete" (commands/ship.md:16-18) were never executed for waves 4-21 | Reality diverges — only wave-3-complete tag exists; the ship protocol was followed at most once |
| `plan/PRD.md` original scope "waves 1-4 = MVP" (PRD:14-27) | "real MVP boundary is waves 1-13" (SCOPE_GUARD:9-10) | SCOPE_GUARD true — PRD already self-corrects with a pointer (PRD:14-19) |
| `resources/EXCEL_SHEETS_INVENTORY.md` marks Time Logging/Sustainability/Document Reference "Pending ⏳", Wave-4 "READY TO DISPATCH" (19,28,35,95) | Waves 4-8 shipped (EXECUTION:33-37; 344 tests) | EXECUTION true — the inventory's Status column is stale; its mapping is fine |
| ADR-0003 embeds the full "send as-is" IT brief (0003:84-251) nearly verbatim | `docs/IT_BRIEF.md` is the same brief, sent to IT | They are two copies of one artifact — risk of divergence; canonical should be IT_BRIEF.md, ADR-0003 should keep reasoning + point |

---

## 7. DELETE / ARCHIVE RECOMMENDATION

| File | Recommend | Why | Anything that must be extracted first? |
|---|---|---|---|
| `KIMI.md` | MERGE-INTO:CLAUDE.md (make it a symlink; keep both resolving) | Byte-identical alias is a maintenance trap — one edit silently diverges; a symlink preserves the "interchangeable orchestrator" behavior with zero drift risk | NO |
| `HANDOFF_FINAL.md` | ARCHIVE (→ docs/historical/) | Wholly stale status; its durable content (5 decisions, sheet subset, tech debt) is already in MEETINGS_MASTER/ADR-0002/EXCEL_SHEETS_INVENTORY/EXECUTION (verified in wave-26 task 01) | NO |
| `wave9handoff.md` | MERGE-INTO:docs/PROJECT_HISTORY.md (or docs/conventions.md), then ARCHIVE | §8 architectural patterns (service/repo conventions, reference-ID service, zero-padded alembic rev-ids) are unique and not in any canonical doc; §4-§7 duplicate ADR-0002/IT_BRIEF/wave-22-24 briefs | YES — §8 patterns; the rate-limiter/test-suite gotcha |
| `wave10handoff.md` | ARCHIVE (→ docs/historical/) | All durable content is in work/reports/wave-13/20/21 + git history; its "uncommitted/pending" claims are stale | NO |
| `OS_SETUP.md` | SAFE-TO-DELETE (or ARCHIVE → attic/ if the no-delete rule is applied strictly) | Generic OS-Setup v1.1 template, not project-specific; a 48KB foreign methodology doc has no place in a repo being handed to a client; it exists at `~/Desktop/OS_SETUP.md` so nothing is lost | NO |
| `.specify/specs/wave-10/` (empty dir) | SAFE-TO-DELETE (empty untracked dir) | Nothing in it | NO |
| `docs/decisions/0003-it-server-call-brief.md` embedded brief | MERGE-INTO:docs/IT_BRIEF.md (keep ADR-0003 reasoning, drop the embedded 160-line duplicate or make it a pointer) | Same artifact in two files will drift; IT_BRIEF.md is the sendable copy | NO |
| `docs/runbook.md` (stale wave-19 section) | KEEP-AS-IS (fix in Phase 2) | Live ops doc; only §Backups is wrong | NO |
| `deliverables/handover/ADMIN_GUIDE.md` (stale wave-19 section) | KEEP-AS-IS (fix in Phase 2) | Client-facing; §3 wrongly says backups don't exist | NO |
| `docs/conventions.md` (GST + error-shape claims) | KEEP-AS-IS (fix in Phase 2) | Live conventions doc with 2 wrong claims | NO |
| `orchestrator/memory/MEMORY.md` (324/324 + GST claims) | KEEP-AS-IS (fix in Phase 2) | Living memory with 2 stale lines | NO |
| `CHANGELOG.md` vs version | KEEP-AS-IS (reconcile in Phase 2) | Either tag/bump to 0.3.0 or correct the changelog | NO |
| `README.md` (Celery/MinIO as if built) | KEEP-AS-IS (tighten wording in Phase 2) | Misleading to a client reading "MinIO/S3 (prod)" when none exists | NO |
| Everything else (plan/, docs/ decisions/, resources/, handover/ 3 others, orchestrator/ 44, .specify/, HANDOFF.md, HIERARCHY.md, HOW_TO_RUN.md, CONTRIBUTING.md) | KEEP-AS-IS | Each has a live audience and non-overlapping purpose after the fixes above | — |

---

## 8. WHAT I COULD NOT DETERMINE

- **Whether `conventions.md:61`'s error-shape claim was ever true** vs always aspirational: I confirmed no handler exists today, but not when/whether one existed earlier. (api.md's 2026-07-21 correction note implies it was always wrong.)
- **Whether the "15-min increments" time-tracking rule is client-sourced or dev-invented**: CLAUDE.md/HANDOFF state it; MEETINGS_MASTER doesn't mention increments. I could not find a meeting quote — treat as dev-side default until verified.
- **Who actually reads `orchestrator/**`**: 44 files are an elaborate apparatus; the live sessions in wave-26 used only the wave-26 briefs + this schema. Whether every command/skill doc is still exercised (vs. aspirational scaffolding from OS-Setup) is unverified — a dead-process doc is a deletion candidate in Phase 2, but I couldn't prove any specific one is dead.
- **Whether `CHANGELOG.md`'s 0.3.0 was a premature entry or the tag was simply forgotten**: either way the repo state contradicts it; the intended fix is ambiguous.
- **The audience of `README.md`'s "Company context" (line 52-54)**: reads like marketing copy for a client-facing doc, but README is primarily an internal/dev entry point. Intent unclear.
- **Whether `.specify/steering.md` and `orchestrator/core/*` are consulted at all** in current practice, or superseded by CLAUDE.md's kernel + the wave briefs (the wave-26 briefs never referenced them).
- **Whether `KIMI.md` is loaded by an actual "Kimi" tool** or is vestigial — I can't see the user's tooling; the symlink recommendation holds either way, but "who loads KIMI.md" is unverified.

---

## 9. PROPOSED CANONICAL SET

**Overlap matrix by topic** (every topic, every doc covering it, canonical marked ★):

| Topic | Docs covering it | Canonical |
|---|---|---|
| Project status / wave tracking | plan/EXECUTION.md ★, HANDOFF.md (summary), CHANGELOG.md (releases), .specify/STATUS.md (specs only), README:34 (pointer), HANDOFF_FINAL/wave9/wave10 (stale) | plan/EXECUTION.md |
| Client requirements + business logic | resources/MEETINGS_MASTER.md ★, ADR-0002 (chain analysis), ADR-0004 (meeting-2 re-read) | resources/MEETINGS_MASTER.md |
| Open decisions | ADR-0002 open table ★, IT_BRIEF Q1-8 ★, ADR-0004 | ADR-0002 + IT_BRIEF |
| Scope (in/out) | docs/SCOPE_GUARD.md ★, orchestrator/core/scope-guard.md (process), plan/PRD.md (historical), EXCEL_SHEETS_INVENTORY (sheet drops), constitution out-of-scope | docs/SCOPE_GUARD.md |
| Architecture | plan/ARCHITECTURE.md ★, ADR-0001 (why), IT_BRIEF Part 3, ADR-0003, handover/ARCHITECTURE_OVERVIEW_FOR_VIRAJ (plain-language), README/CLAUDE stack lines, HANDOFF_FINAL (superseded) | plan/ARCHITECTURE.md |
| Deployment | docs/DEPLOYMENT_CHECKLIST.md ★ (ops), docs/deployment.md ★ (overview), docker-compose.prod.yml + .env.production.example (config), IT_BRIEF/ADR-0003 (facts), docs/runbook.md (dev) | DEPLOYMENT_CHECKLIST + deployment + IT_BRIEF |
| How-to-run / local dev | HOW_TO_RUN.md ★ (workflow), docs/runbook.md ★ (dev ops), README (quick start), CONTRIBUTING (contrib), Makefile (source) | HOW_TO_RUN.md + runbook.md |
| Conventions / code style | docs/conventions.md ★, .specify/memory/constitution.md ★ (non-negotiable), .specify/steering.md, orchestrator/rules/*.md, CLAUDE.md code-style | constitution.md + conventions.md + rules/*.md |
| History / gotchas | docs/PROJECT_HISTORY.md ★, orchestrator/memory/MEMORY.md (living), wave9handoff (unique §8) | PROJECT_HISTORY.md (+ MEMORY.md for live memory) |
| Handoff / session state | HANDOFF.md ★, HANDOFF_FINAL.md, wave9handoff.md, wave10handoff.md (consolidate away) | HANDOFF.md |
| Handover (client-facing) | deliverables/handover/* ★ (4 docs), IT_BRIEF (to IT), handover/ARCHITECTURE_OVERVIEW (via Viraj) | deliverables/handover/* |
| Methodology (two-tier agentic) | orchestrator/core/*.md ★, HOW_TO_RUN.md, CLAUDE.md kernel, .specify/steering.md, OS_SETUP.md (generic source — remove from repo) | orchestrator/core/* + HOW_TO_RUN.md |
| Data/sheet mapping | resources/EXCEL_SHEETS_INVENTORY.md ★, MEETINGS_MASTER (meeting context) | EXCEL_SHEETS_INVENTORY.md |
| API reference | docs/api.md ★ (+ live Swagger, higher authority) | docs/api.md |
| Authority precedence | docs/conflict_resolution.md ★ | docs/conflict_resolution.md |
| Backup/restore ops | docs/runbook_backup_restore.md ★, runbook.md (stale ref), ADMIN_GUIDE (client-facing ref) | runbook_backup_restore.md |

**Canonical set — the minimum docs that should survive Phase 2:**

| Canonical doc | Audience | Purpose | Absorbs |
|---|---|---|---|
| `README.md` | future dev + client entry | Entry point, quick start, repo map pointer | tighten "Celery/MinIO" wording |
| `CLAUDE.md` | orchestrator | Always-loaded kernel | nothing (KIMI.md becomes a symlink to it) |
| `HANDOFF.md` | orchestrator | Session/orchestrator switching; short status pointer | its own stale status numbers; the live-update duties of HANDOFF_FINAL/wave9/wave10 |
| `HIERARCHY.md` | orchestrator + future dev | Repo map + ownership | update once wave-26 consolidation lands |
| `HOW_TO_RUN.md` | orchestrator + future dev | Dual-tier workflow | nothing |
| `CONTRIBUTING.md` | future dev | Contribution rules | nothing |
| `CHANGELOG.md` | future dev + client | Release history | reconcile version to reality |
| `plan/EXECUTION.md` | orchestrator | Wave status (canonical) | status claims from HANDOFF.md/MEMORY.md |
| `plan/ARCHITECTURE.md` | orchestrator + future dev | Architecture (real + target) | fix the Celery diagram to mark target-vs-real |
| `plan/PRD.md` | orchestrator | Product spec (historical) | keep as-is (already self-corrected) |
| `docs/SCOPE_GUARD.md` | orchestrator | Canonical scope | nothing |
| `docs/decisions/0001-0004` | orchestrator + future dev | ADRs | 0003 drops embedded IT-brief duplicate → IT_BRIEF |
| `docs/IT_BRIEF.md` | IT (client) | 8 questions, sendable | the sendable text currently duplicated in ADR-0003 |
| `docs/PROJECT_HISTORY.md` | orchestrator + future dev | History + gotchas | wave9handoff §8 architectural patterns |
| `docs/conventions.md` | future dev | Conventions | fix GST + error-shape claims |
| `docs/api.md` | future dev | API reference pointer | nothing |
| `docs/deployment.md` + `docs/DEPLOYMENT_CHECKLIST.md` | deploy operator | Deploy overview + day-of runbook | nothing (complementary pair) |
| `docs/runbook.md` + `docs/runbook_backup_restore.md` | future dev + admin | Local ops + backup/restore | fix runbook's stale wave-19 section |
| `resources/MEETINGS_MASTER.md` | everyone | Client requirements source of truth | nothing |
| `resources/EXCEL_SHEETS_INVENTORY.md` | orchestrator | Sheet→wave mapping | fix stale Status column |
| `deliverables/handover/*` (4) | client staff / Viraj / IT | Handover package | fix ADMIN_GUIDE wave-19 section |
| `orchestrator/**` (44) | orchestrator | Process apparatus | nothing (self-contained) |
| `orchestrator/memory/MEMORY.md` | orchestrator | Living memory | fix 324/324 + GST lines |
| `.specify/memory/constitution.md` | orchestrator | Non-negotiable principles (top authority) | nothing |
| `.specify/STATUS.md` | orchestrator | Meta-note: .specify is historical | nothing |
| `.specify/steering.md` | orchestrator | AI rules | likely mergeable into constitution/rules in Phase 2 (overlaps both) |

---

## 10. PROPOSED DELETION / ARCHIVE LIST

| File | Action | Why | What must be extracted first |
|---|---|---|---|
| `KIMI.md` | Replace with symlink → CLAUDE.md (or delete + symlink) | Byte-identical duplicate = divergence trap; symlink preserves behavior | NO |
| `HANDOFF_FINAL.md` | ARCHIVE → docs/historical/ | Stale status; content already canonical elsewhere | NO |
| `wave9handoff.md` | ARCHIVE → docs/historical/ (after merging §8) | §8 patterns unique; rest duplicated | YES — §8 architectural patterns + rate-limiter gotcha → PROJECT_HISTORY.md/conventions.md |
| `wave10handoff.md` | ARCHIVE → docs/historical/ | Superseded by wave-13/20/21 reports + git | NO |
| `OS_SETUP.md` | Remove from repo (SAFE-TO-DELETE; exists at ~/Desktop/OS_SETUP.md) — or ARCHIVE → attic/ if no-delete applies | 48KB generic template, not project-specific, wrong audience for a client handover | NO |
| `.specify/specs/wave-10/` (empty dir) | Remove (empty untracked dir) | Nothing in it | NO |
| `docs/decisions/0003` embedded brief (lines 84-251) | Strip from ADR-0003 → point at IT_BRIEF.md | One artifact in two files will drift | NO |

**Non-deletion fixes for Phase 2 (stale claims, KEEP the files):** `docs/runbook.md` wave-19 section, `deliverables/handover/ADMIN_GUIDE.md` wave-19 section, `docs/conventions.md` GST + error-shape, `orchestrator/memory/MEMORY.md` test-count + GST lines, `HANDOFF.md` test-count, `plan/ARCHITECTURE.md` Celery diagram labeling, `README.md` Celery/MinIO wording, `resources/EXCEL_SHEETS_INVENTORY.md` Status column, `CHANGELOG.md` version-vs-tag reconciliation.

---

## Verification

Evidence block for the duplication and overlap claims above (added by the orchestrator during
merge so FM-09 can see it).

```
diff CLAUDE.md KIMI.md        -> no output = BYTE-IDENTICAL (confirmed by the
                                 orchestrator independently, not just asserted)
wc -c OS_SETUP.md             -> 48809 bytes, generic agentic-project template,
                                 not swa-erp-specific; copy exists outside the
                                 repo at ~/Desktop/OS_SETUP.md
docs/decisions/0003           -> embeds a full copy of docs/IT_BRIEF.md
                                 (~lines 84-251); one artifact in two files,
                                 already drifted once on the RS256 claim
Handoff documents in root     -> 4 files all claiming to be "the" handoff:
                                 HANDOFF.md, HANDOFF_FINAL.md, wave9handoff.md,
                                 wave10handoff.md, with conflicting status
Scope documents               -> docs/SCOPE_GUARD.md (canonical) vs
                                 orchestrator/core/scope-guard.md (process)
Deployment described in       -> docs/deployment.md, docs/DEPLOYMENT_CHECKLIST.md,
                                 docker-compose.prod.yml comments

Output: a per-topic overlap matrix (section 9) naming exactly one canonical doc
per topic, plus a deletion/archive list (section 10) with the extract-first
requirement recorded per file. Wave-28 executes it; wave-29 fixes the 9
stale-claim items that are KEEP-the-file corrections.
```
