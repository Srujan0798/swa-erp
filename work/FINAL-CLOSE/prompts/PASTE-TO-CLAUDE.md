# PASTE THIS ENTIRE FILE into a new Claude Code session

Working directory must be: `/Users/srujansai/Desktop/swa-erp`

---

You are the **close-out orchestrator and executor** for **swa-erp**.

## Mission (user-confirmed)

**Full close** the project for internship submission end-to-end:

1. Hygiene (trackers / handoff truth)
2. Stabilize (green suites: 401/403 + TaskCard IST flake + Vitest-in-CI)
3. Wave-37 independent adversarial review + triage + confirmed fixes
4. Wave-38 professional submission package
5. Close seal (`FINAL-CLOSE.report.md`) + push

Product features are already done (v1.0.1, waves 1–31). Do **not** add features. Do **not** invent new waves. Do **not** wait on Viraj server answers to close engineering.

## Read first (in order) — then execute

1. `work/FINAL-CLOSE/README.md`
2. `work/FINAL-CLOSE/ULTIMATE-CLOSE-GUIDE.md`
3. `work/FINAL-CLOSE/ANTI-FABRICATION.md`
4. `work/FINAL-CLOSE/PROTOCOLS.md`
5. `work/FINAL-CLOSE/TASK-CATEGORIES.md`
6. `work/FINAL-CLOSE/DEFINITION-OF-DONE.md`
7. `work/reports/COMPLETION-HANDOFF-VERDICT.md` (living truth)
8. `work/wave-37/01-independent-review.md`
9. `work/wave-38/01-submission-package.md`

Also load and **use** these skills/workflows as needed: `verification-before-completion`, `systematic-debugging`, `test-driven-development`, `requesting-code-review` / code-review agents, `pr-review-toolkit` agents (especially **silent-failure-hunter**), `feature-dev:code-reviewer`, frontend vitest patterns, and any `/security-review` / `/code-review` available in this environment. Prefer real tools over theater. Skill-count bragging is banned.

## Current verified baseline (do not “rediscover” by rewriting history)

- `origin/main` @ **`4050f51`** (wave-33 finish pushed)
- Backend independent: **5 failed / 557 passed / 1 skipped, TOTAL 86%**
- Failures are the standing **401-vs-403** auth assertions (FastAPI `HTTPBearer` → 403 with no header)
- All `services/*.py` ≥70%; **global** “no module &lt;70%” is **FALSE**
- Frontend thresholds met independently (~**61%** stmts); **TaskCard** flakes under IST because of `toISOString()` UTC
- Waves 32–36+39 effectively shipped; **37 and 38 not started**
- `ACTIVE.md` / `HANDOFF.md` still stale (Aug-11 / IN-FLIGHT lies)
- Viraj overview still wrongly says MinIO/Celery unbuilt

## Execute phases in order — Protocols P01→P20

### Phase 0 — Grounding
Run **P01, P02**. Print HEAD + next phase.

### Phase 1 — Hygiene
Run **P03, P04, P10**. Commit docs. No `src/` changes except if P10 is docs-only (it is).

### Phase 2 — Stabilize
Run **P05, P06, P07, P08, P09** (P09 recommended — do it).  
Target: backend **0 failed**, frontend **0 failed**, vitest in CI.

### Phase 3 — Wave-37
Run **P11 → P12 → P13 → P14** (+ **P15** if triage agrees).  
Follow `work/wave-37/01-independent-review.md` exactly. Use all 7 review tools listed there (or document skips).  
Report → `work/reports/wave-37/01-independent-review.report.md`

### Phase 4 — Wave-38
Run **P17 → P18 → P19**.  
Follow `work/wave-38/01-submission-package.md`.  
Every metric must cite a wave report path. Forbidden inflated claims (see ANTI-FABRICATION).

### Phase 5 — Close seal
Run **P20**. Write `work/reports/FINAL-CLOSE.report.md`. Update ACTIVE/HANDOFF to SHIPPED. Push `origin/main`.

## Non-negotiable rules

1. **No fabricated reports.** Paste real command output. This repo’s workers have lied before.
2. **One pytest at a time.** Concurrent suite = mass deadlocks → not a code verdict.
3. **Never claim** “100% complete”, global “no module &lt;70%”, or frontend 65.86% without a fresh run.
4. **Do not re-blast** `SEND_IT.md` / `SEND_VIRAJ.md` to the client.
5. **Do not start wave-38 before wave-37 report exists.**
6. Surgical commits; push when a phase is verified.
7. If blocked, write NOT DONE + blocker — never fake green.

## What to say at the end

Only after DEFINITION-OF-DONE.md A–E are true:

> Engineering close complete for internship submission. Deploy remains external (Viraj / no IT dept). Evidence: `work/reports/FINAL-CLOSE.report.md`.

Until then, say which phase/protocol is incomplete.

## Start now

Begin Phase 0. Do not ask permission between protocols inside a phase. Ask only if HEAD has unexpected dirty state or a review tool is completely unavailable.
