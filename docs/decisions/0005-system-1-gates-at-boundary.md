# Decision: System-1 Gates at Boundary (LAYA)

## Status
Accepted — infrastructure written; **not yet wired into ERP routers**

## Context
Boundary triage (inbound email, sheet-row risk, scope/prompt guards, low-stakes
admission) benefits from a fast System-1 model. LAYA (`laya==0.3.5`) provides
typed `choice` / `score` / `noul` answers with calibrated confidence in a single
forward pass. Base checkpoints are **near-chance zero-shot** on typed-decisions
(README: ~0.36 vs 0.318 random) — unlabeled accuracy must never be trusted.

## Decision

1. **Boundary only.** LAYA may only run the five packs in
   `packages/karna_decisions/packs.py`:
   `swa.inbound_email`, `swa.sheet_row_risk`, `harness.scope_guard`,
   `harness.prompt_guard`, `controlplane.admission`.
   **Never** money, identity, RBAC, GST, or irreversible ledger paths.
2. **Single import seam.** Under `src/backend/services/`, only `laya_gate.py`
   may `import laya`. Application services call `laya_gate.decide(...)`.
3. **Shared package.** Question packs + escalation logic live in
   `packages/karna_decisions/` (versioned dicts) so every project reuses one
   gate; swa-erp only adapts via `laya_gate.py`.
4. **`Router(preload=True)` always.** Cold load is seconds; language flips at
   `max_loaded=1` rebuild every request. Singleton in `laya_gate._get_router`.
5. **Fail closed.** `evaluate_answers` escalates on: missing answers, missing
   confidence, `confidence < 0.70`, noul in gray band `[0.40, 0.60]`, optional
   `risk_max_auto` score overflow. Escalation ⇒ human, never silent auto-approve.
6. **Graphify mandatory** for LAYA context questions (skill `laya-gate`).
7. **Labeled eval before trust.** EN/HI dry-run only; **hard stop** before any
   ERP router is wired. Eval scaffold: `evals/laya/`.

## Consequences
- Positive: one shared System-1 seam; calibrated escalate path; no LAYA on
  high-stakes ERP writes.
- Negative: dry-run + labeled eval still required; HF_TOKEN unauthenticated
  (confidence buckets with clamped temps are uncalibrated — documented).
- Deferred: wiring `laya_gate.decide` into any API route.

## Standing rules (carry forward)
- ADR slot was 0005 (0001–0004 taken at write time).
- Do not claim LAYA is validated for ERP correctness.

## Verification (run before approving LAYA work)
```bash
.venv-laya/bin/python -c "from laya import Router; Router(preload=True)"
.venv-laya/bin/python -m packages.karna_decisions.selftest   # pure gate logic, no weights
.venv-laya/bin/python scripts/laya_dry_run.py                # EN/HI dry-run → evals/laya/
# Import discipline:
rg -n "^import laya|^from laya" src/backend/services/   # only laya_gate.py
```
