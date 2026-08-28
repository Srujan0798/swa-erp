# Technical Report — SWA Consultancy ERP

**Audience:** engineers and internship evaluators who were not in the room.  
**Date:** 2026-08-23  
**Scope:** product v1.0.1 + professional-grade evidence track (waves 32–39, all shipped). Residual ops RISKs from wave-37 are listed in §5 — not claimed as zero.

---

## 1. Problem

SWA Consultancy is an insulation engineering firm in Ahmedabad (thermal, acoustic, passive fire; standards NBC / ECBC / IGBC / IS). In ~3 years they ran ~750 projects. Day-to-day operations lived in **~20 Excel files on OneDrive**, with staff manually generating IDs, linking tokens to drawings, and logging hours in personal “dashboard” sheets.

Viraj (founder) described the live process in Meeting 1:

> “First of all, inquiry came, and then converted into client… based on client's requirement, we generated a specific document based on work… if IESK came through any work, then we go into tokens… token ID… document reference number… each ID has a specific flow.”

And the tone that mattered for product decisions:

> “We are doing this flow in live. Currently we are doing this flow, but the final flow decided by Viraj.”

Source: [`resources/MEETINGS_MASTER.md`](../resources/MEETINGS_MASTER.md).

**Goal:** replace the spreadsheet mesh with one internal ERP that **digitizes the existing workflow** — not invent a new process — with role-based access matching how sheets were already restricted (PM vs designer vs founder-only finance, etc.).

---

## 2. Requirements discovery (including the misread)

### What we thought we were building

Early delivery waves (1–8) produced a solid **generic CRM**: clients, projects, BOQ/quotes, tasks, vendors, documents, time, reports. Useful software — and the wrong intellectual center of gravity for this client.

### What the transcripts and sheets actually required

Re-reading the **raw** meeting transcripts and the live `.xlsx` extracts (not only cleaned summaries) showed the client’s MVP was a linear **ID chain**:

```
Inquiry → Client → Service Agreement → Token → Document Reference → Time Log
```

Verified against source data: IDs are `SWA-{year}-{3-letter-code}-{seq:03d}` (e.g. `SWA-2025-INQ-001`, `SWA-2025-SA-011`), not the verbal numeric shorthand (“IESK=12…”) from Meeting 1. Inquiry→Client conversion is **not** blind 1:1 create — the system must check whether the client already exists, then always land on a **Project**. DocumentReference needs both `project_id` and optional `token_id`. DBR and KDR **share one counter**.

Full write-up: [`docs/decisions/0002-core-id-chain-gap.md`](../docs/decisions/0002-core-id-chain-gap.md).

### Why telling this honestly matters

Catching a fundamental requirements misread — then correcting it in wave-9+ against real sheets and Viraj’s later answers (APEX/INNER are **client names**, INSUDESIGN is the **service name**; yearly ID reset; no Leads module) — is a stronger engineering signal than pretending the first cut was right. Sanitized summaries had flattened detail; the recovery came from going back to primary sources.

---

## 3. Architecture and key decisions

High-level shape: React SPA → FastAPI → PostgreSQL, with Redis as Celery broker/backend, file storage behind a `StorageBackend` (local default, MinIO opt-in), JWT + RBAC.

Diagrams (built vs target marked): [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).

| Decision | Choice | Why (short) |
|----------|--------|-------------|
| ADR-0001 stack | FastAPI + React/Vite/TS + PostgreSQL + Celery + Compose | Continuity with Python skills; API-first; relational ERP data; one-server deploy |
| Storage | `StorageBackend` protocol | Same call sites for local disk or MinIO without rewriting services |
| Background work | Celery workers (wave-31) | PDF/report export can run async (`?async=true` → poll job) |
| Money | `Decimal(18,2)`, INR default | Exact GST math; no float drift |
| Auth | JWT HS256 + role checks in DB | Internal on-prem; role from DB not from unverifiable JWT claims alone |
| ID generation | Shared `reference_counters` per `(entity_type, year)` | Matches live sheets; yearly reset confirmed by Viraj |

Celery and MinIO are **built** (wave-31), not aspirational. Client Windows Server deploy remains **external** until server facts land.

---

## 4. Engineering rigour

Work was sequenced in **waves** — scoped briefs under `work/wave-N/`, acceptance contracts, and written reports under `work/reports/wave-N/`. Product MVP closed at v1.0.1 (waves 1–31). A later **professional-grade** track (32–39) made quality claims checkable.

| Wave | What it proved | Evidence |
|------|----------------|----------|
| **32** | CI gates are real — removed all `\|\| true` / `continue-on-error` from GitHub workflows; wired pip-audit, npm audit, semgrep; `make verify` | [`work/reports/wave-32/01-real-ci-quality-gates.report.md`](../work/reports/wave-32/01-real-ci-quality-gates.report.md) |
| **33** | Backend coverage raised; overall **86%**; all service modules ≥70%; five former weak services (pdf/quote/import/task/notification) closed | [`work/reports/wave-33/03-remaining-coverage.report.md`](../work/reports/wave-33/03-remaining-coverage.report.md), [`work/reports/COMPLETION-HANDOFF-VERDICT.md`](../work/reports/COMPLETION-HANDOFF-VERDICT.md) |
| **34** | Real frontend Vitest suite; thresholds **60/50/60/60** met; cite **~61%** statements on independent remeasure | [`work/reports/wave-34/02-frontend-page-coverage.report.md`](../work/reports/wave-34/02-frontend-page-coverage.report.md) + verdict |
| **35** | Locust load at 10/50/100/150 users on a **dev machine**; p95 ≈ 29–130 ms; no 5xx after fixes | [`docs/PERFORMANCE.md`](../docs/PERFORMANCE.md) |
| **36** | Prometheus metrics, readiness, optional Sentry | [`docs/operational/OBSERVABILITY.md`](../docs/operational/OBSERVABILITY.md), wave-36 report 02 |
| **37** | Independent adversarial review | **Shipped** — path-traversal + hourly-rate settings fixed; residual RISKs documented | [`work/reports/wave-37/01-independent-review.report.md`](../work/reports/wave-37/01-independent-review.report.md) |
| **38** | Submission package | **Shipped** | wave-38 report |
| **39** | Repo organization | Shipped | |

**Anti-fabrication:** this project documents past over-claims (wrong pass counts, “module X done” when files were missing). Closing rules live in [`work/FINAL-CLOSE/ANTI-FABRICATION.md`](../work/FINAL-CLOSE/ANTI-FABRICATION.md). Metrics in the README and this report use only verified wording (e.g. **not** “no backend module under 70%” globally — nine non-alembic modules remain under that line).

---

## 5. Honest limitations

Pulled from [`SUBMISSION.md`](SUBMISSION.md) §4 and current reality — not sanded off:

1. **Deploy is not company-live.** Viraj confirmed there is **no IT department**; eight server questions remain open (`SEND_IT.md`). Engineering can be complete while production hostname/ports/certs are unknown.
2. **Load numbers are from a development machine**, not the client’s Windows Server (128 GB, VPN-only). Defensible claim: p95 ≈ 29–130 ms at 10–150 users **on this laptop-class stack**.
3. **JWT is HS256**, fine for internal on-prem; RS256 would be needed for third-party token verification.
4. **Coverage is strong, not total.** Backend 86% overall; services ≥70%; some API/repo modules still &lt;70%. Frontend meets configured thresholds at ~61% statements independently.
5. **Backend suite after final-close stabilize:** **565 passed / 0 failed / 1 skipped** (industry re-verify). Frontend **522 / 0**.
6. **Wave-37 residual RISKs (documented, not all fixed):** `/metrics` auth posture; time/finance VIEWER reads vs Meeting 1 matrix (industry-hardening Phase C); import rollback counters; JWT refresh rotation. See wave-37 report.
7. **Out of MVP by client decision:** HR, founder-only finance sheets, satisfaction/complaints, marketing analytics, client portal.
8. **Excel → ERP cutover ownership** is still organizational (who runs the real import at go-live).

Historical note: older SUBMISSION text said Celery/MinIO were unimplemented — **superseded by wave-31**. Current docs mark both **BUILT**.

---

## 6. What was learned

1. **Primary sources beat summaries.** Cleaned meeting notes dropped ID formats, conversion rules, and counter-sharing facts that only reappeared in raw transcripts and spreadsheet headers.
2. **Correcting a misread is deliverable work.** Shipping the generic CRM first was not wasted — it built auth, projects, and money — but naming the gap (ADR-0002) and closing it was the difference between “demo app” and “their system.”
3. **Fake CI teaches the wrong lesson.** Wave-32’s removal of `|| true` made every green check mean something; that credibility compounds into coverage and load claims.
4. **Measure the environment you have.** Publishing 100-user results without a “dev machine” caveat would be another fabrication; with the caveat, the numbers are useful.
5. **Honesty scales better than polish.** Listing open IT questions and standing test debt is what lets a professional evaluator trust the rest.

---

## Appendix — run / read next

```bash
make install && make dev   # UI :3100 · API :8100
```

- Demo: [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md)  
- Handover package: [`SUBMISSION.md`](SUBMISSION.md)  
- Front door: [`../README.md`](../README.md)
