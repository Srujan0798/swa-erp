# Task Categories C01–C12

High-level buckets for the final close. Every piece of work maps to exactly one category.

---

## C01 — Ground truth & anti-fabrication
Establish what is real before changing anything. Includes reading the living verdict, refusing fabricated pass counts, and naming the current HEAD.

**Protocols:** P01, P02  
**Exit:** Next phase chosen with evidence.

---

## C02 — Tracker / handoff sync
Make `ACTIVE.md`, `HANDOFF.md`, `EXECUTION.md`, `CHANGELOG.md` match git so the next human/agent is not lied to by Aug-11 “complete” language.

**Protocols:** P03, P04  
**Exit:** Docs describe professional-grade track honestly.

---

## C03 — Backend suite honesty
Turn “real CI” into “green real CI.” Fix the standing 401/403 mismatch; re-run full suite solo; keep ≥85% coverage.

**Protocols:** P05, P06  
**Exit:** `pytest tests/ -q` → 0 failed.

---

## C04 — Frontend suite honesty
Kill the TaskCard timezone flake; re-measure coverage; stop citing 65.86% from an old report.

**Protocols:** P07, P08  
**Exit:** vitest 0 failed; thresholds met on a fresh run.

---

## C05 — CI wiring
Frontend unit tests must be merge-blocking like backend tests already are.

**Protocols:** P09  
**Exit:** `ci.yml` runs vitest without `|| true`.

---

## C06 — Client-facing doc truth
Correct forwardable docs that still say MinIO/Celery are unbuilt. Do not re-blast client WhatsApp.

**Protocols:** P10  
**Exit:** Viraj architecture overview is accurate.

---

## C07 — Adversarial review
Independent multi-tool review of the full codebase. This is the credibility wave for internship evaluation.

**Protocols:** P11–P14  
**Exit:** Wave-37 report with triage table on main.

---

## C08 — Confirmed-bug fixes
Only fix what triage proves. TDD. Includes optional priority-map consolidation.

**Protocols:** P15 (and fixes inside P13)  
**Exit:** Each CONFIRMED BUG closed with regression test.

---

## C09 — Submission packaging
Make the repo legible to a professional in 10 minutes: README, architecture, technical report, SUBMISSION, demo script.

**Protocols:** P17–P19  
**Exit:** Wave-38 report + claim audit.

---

## C10 — Close seal & archive
One final report; trackers SHIPPED; push; declare engineering closed.

**Protocols:** P20  
**Exit:** `FINAL-CLOSE.report.md` exists and is true.

---

## C11 — External deploy (non-blocking)
Viraj / server facts / Excel migration ownership / client-box load test. Tracked but **does not block** engineering close.

**Artifacts:** `deliverables/SEND_IT.md`, `docs/INSTALL_NO_IT.md`, `MASTER-FLOW.md`  
**Exit:** Explicit “external” section in FINAL-CLOSE.report.md — not more code.

---

## C12 — Explicit non-goals
Banned for this close:
- New product modules
- Re-dispatching waves 32–36/39
- 5,000-line process novels
- Claiming production-live
- Graphify/skill-count for show
- Re-asking Viraj open-ended architecture questions

**Exit:** None of these appear in commits or reports.
