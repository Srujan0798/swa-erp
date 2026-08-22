# Ultimate Close Guide — swa-erp Professional Finish

**Status:** AUTHORITATIVE for close-out (2026-08-23)  
**HEAD baseline:** `4050f51` on `origin/main`  
**Intensity:** Full close (user-confirmed)  
**Orchestrator role:** Claude Code executes; human pastes prompts and spot-checks reports.

---

## 0. One-sentence mission

Finish the professional-grade evidence track honestly, package it for evaluators, and declare the engineering project **closed** — without inventing features, without lying about metrics, and without waiting on Viraj’s server answers (those are a separate deploy track).

---

## 1. Reality you must accept before typing

| Fact | Implication |
|---|---|
| Product v1.0.1 is feature-complete | No new modules, no “maybe add HR”, no scope creep |
| Waves 32–36 + 39 are effectively shipped | Don’t re-dispatch them |
| Waves **37 and 38** are the close | Sequence: 37 then 38 — never reverse |
| 5 backend tests fail on 401 vs 403 | Real CI will stay red until fixed |
| TaskCard flake under IST | Don’t claim “all frontend green” until fixed |
| Global “no module &lt;70%” is **false** | Cite overall 86% + services ≥70% + 5 targets |
| Viraj: no IT dept | Deploy waits; code close does not |
| This repo fabricates reports when stuck | Every number needs a command paste |

Read once: `work/reports/COMPLETION-HANDOFF-VERDICT.md`.

---

## 2. Phase map (strict order)

```
PHASE 0  Grounding          — read verdict + this pack; refuse if HEAD ≠ expected
PHASE 1  Hygiene            — ACTIVE / HANDOFF / EXECUTION / CHANGELOG sync
PHASE 2  Stabilize          — 401→403 tests, TaskCard IST, Vitest-in-CI (optional but recommended)
PHASE 3  Wave-37            — adversarial review → triage → confirmed fixes
PHASE 4  Wave-38            — README / ARCHITECTURE / TECHNICAL_REPORT / SUBMISSION / DEMO
PHASE 5  Close seal         — FINAL report, HANDOFF rewrite, optional tag note
```

**Hard rule:** Do not start Phase N+1 until Phase N acceptance criteria pass with pasted command output.

---

## 3. Skills & tooling to actually use

You do **not** need “100+ skills.” You need the **right** ones, fully:

### Always-on (every phase)
- `verification-before-completion` — no DONE without evidence
- `systematic-debugging` — when something fails
- `test-driven-development` — for every confirmed bug fix
- Project kernel: root `Claude.md` / `CLAUDE.md`, `work/WORKER_PROMPT.md` discipline

### Phase 1 — Hygiene
- Plain file edit + git. No agents required.

### Phase 2 — Stabilize
- Backend: pytest, ruff, mypy
- Frontend: vitest, eslint, tsc
- Optional: edit `.github/workflows/ci.yml` to add `npx vitest run`

### Phase 3 — Wave-37 (mandatory tool set from brief)
1. `/code-review ultra` (or deepest available code-review)
2. `/security-review` (or security-focused pass)
3. `pr-review-toolkit:silent-failure-hunter` ← **highest value**
4. `pr-review-toolkit:type-design-analyzer`
5. `pr-review-toolkit:pr-test-analyzer`
6. `pr-review-toolkit:comment-analyzer`
7. `feature-dev:code-reviewer`

Also park-list items to triage even if tools miss them:
- 5× 401-vs-403 auth assertions
- TaskCard `toISOString()` IST flake
- Triplicate priority maps in `task_repo.py`
- Unauthenticated `/metrics` exposure (document RISK if not fixing)

### Phase 4 — Wave-38
- Mermaid for diagrams
- Honest writing from `resources/MEETINGS_MASTER.md` + ADRs
- Optional: artifact/showcase HTML if skill available
- **Every metric** cites `work/reports/wave-N/...`

### Do not waste time on
- Rebuilding MinIO/Celery (already shipped wave-31)
- Re-reading all of `docs/historical/`
- Inventing 40 new process frameworks
- Graphify / skill-count theater that doesn’t change code or evidence

---

## 4. Session strategy (how humans run this)

| Session | Goal | Paste file |
|---|---|---|
| **S1** | Phase 0–2 complete (hygiene + stabilize) | `prompts/PASTE-TO-CLAUDE.md` |
| **S2** | Phase 3 wave-37 complete | `prompts/CONTINUE-SESSIONS.md` §S2 |
| **S3** | Phase 4 wave-38 + Phase 5 close seal | `prompts/CONTINUE-SESSIONS.md` §S3 |

If a session dies mid-phase: use the **resume** block in CONTINUE-SESSIONS — never restart from Phase 0 if commits already landed.

Cap concurrent heavy work: **one** full pytest at a time (this suite dies under concurrent runners — documented in `docs/PROJECT_HISTORY.md`).

---

## 5. Communication rules (what to say / not say)

### To Claude (orchestrator)
- Give phases, acceptance commands, forbidden claims.
- Demand pasted output. Reject “looks good.”

### To Viraj / client group
- **Do not** re-send long IT questionnaires.
- Only if asked: point to `docs/INSTALL_NO_IT.md` and wait.
- Fix `deliverables/handover/ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` **before** anyone forwards it (MinIO/Celery lies).

### In submission copy
- Allowed: “engineering complete for internship submission; company deploy blocked on server facts owned by Viraj.”
- Forbidden: “100% complete,” “production live,” “no module under 70%,” “CI always green” (until 5 auth tests fixed).

---

## 6. Category → Phase → Protocol index

See [`TASK-CATEGORIES.md`](TASK-CATEGORIES.md) and [`PROTOCOLS.md`](PROTOCOLS.md).

| Cat | Name | Phase | Protocols |
|---|---|---|---|
| C01 | Ground truth & anti-fabrication | 0 | P01, P02 |
| C02 | Tracker / handoff sync | 1 | P03, P04 |
| C03 | Backend suite honesty | 2 | P05, P06 |
| C04 | Frontend suite honesty | 2 | P07, P08 |
| C05 | CI wiring | 2 | P09 |
| C06 | Client-facing doc truth | 1–2 | P10 |
| C07 | Adversarial review | 3 | P11–P14 |
| C08 | Confirmed-bug fixes | 3 | P15, P16 |
| C09 | Submission packaging | 4 | P17–P19 |
| C10 | Close seal & archive | 5 | P20 |
| C11 | External deploy (non-blocking) | parallel | (reference only) |
| C12 | Explicit non-goals | all | (ban list) |

---

## 7. Acceptance commands (canonical)

Run from repo root. Solo. No other pytest.

```bash
# Backend
python3 -m pytest tests/ -q --cov=src/backend --cov-report=term
ruff check src/backend/
black --check src/backend/
mypy src/backend/ --explicit-package-bases

# Frontend
cd src/frontend && npx vitest run --coverage && npx tsc --noEmit && npx eslint . --ext ts,tsx --max-warnings 0 && cd ../..
```

**Pass bar after Phase 2:**
- Backend: **0 failed** (the old 5 must be fixed), coverage still ≥85% overall, the five wave-33 targets still ≥70%
- Frontend: **0 failed**, thresholds ≥60/50/60/60

**Pass bar after Phase 3:** same + wave-37 report exists with triage table.

**Pass bar after Phase 4:** same + wave-38 artifacts exist + every metric in README/SUBMISSION has a source path.

---

## 8. Deliverables checklist (close seal)

- [ ] `work/ACTIVE.md` marks 32–36, 39 SHIPPED; 37/38 SHIPPED after done
- [ ] `HANDOFF.md` rewritten for post-professional-grade close (not Aug-11 v1.0.1-only)
- [ ] `work/reports/wave-37/01-independent-review.report.md`
- [ ] `work/reports/wave-38/01-submission-package.report.md`
- [ ] Updated `README.md`, `docs/ARCHITECTURE.md`, `deliverables/TECHNICAL_REPORT.md`, `deliverables/SUBMISSION.md`, `deliverables/DEMO_SCRIPT.md`
- [ ] `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` no longer lies about MinIO/Celery
- [ ] `work/reports/FINAL-CLOSE.report.md` — one-page seal with HEAD, dates, commands, remaining external blockers
- [ ] All commits pushed to `origin/main`

---

## 9. Stop conditions (declare blocked, don’t fake)

Stop and report NOT DONE if:
- Full suite cannot run because another pytest holds the DB
- A review tool is unavailable — document which, continue with the others, do not invent findings
- Coverage drops below 85% after fixes
- Wave-38 would need numbers that were never measured

---

## 10. After close — what remains forever external

1. Viraj (or nominee) answers 8 server facts  
2. Deploy via `docs/INSTALL_NO_IT.md`  
3. Excel freeze + `make import-real` ownership  
4. Client Windows Server load test  

These are **not** reasons to keep coding. They are deploy ops.
