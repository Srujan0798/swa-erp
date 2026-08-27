# evals/ — System correctness evals for swa-erp

> Wave-43 Task 01. These are **evaluations**, not tests. Tests check code paths;
> evals check whether the *system does the job the client asked for*.

## Status (2026-08-28)

- ✅ `evals/` scaffolded: README + 5 task specs + 3 graders + workflow + run harness.
- ✅ Code-based grader runs and produces real pass/fail (see `evals/reports/2026-08-28-baseline.md`).
- ⚠️ `.github/workflows/evals.yml` is **intentionally non-blocking** (`continue-on-error: true`).
  This is documented here and in the workflow header. Evals are new and flaky-by-nature
  until tuned; they are NOT a real gate. See "Anti-patterns" below.

## Framework choice

We use a **plain pytest harness** (`evals/graders/code_based.py` + `evals/run_evals.py`).

We did **not** use Harbor / Braintrust / Phoenix. Justification (honest):
- This is an early-stage internship submission. The team does not yet have a shared
  eval-platform account, a persistent eval DB, or secrets management for an external
  service. Standing up one now would consume the entire wave-43 time budget and
  would need an ADR (constitution §35: new dependencies need justification).
- The app already runs real pytest against a real Postgres (see `tests/conftest.py`).
  Reusing that stack — `ASGITransport` + HTTpx + the existing `db_session` fixture —
  means evals exercise the *actual running application*, not a stub. That is more
  honest than a hosted platform we can't maintain.
- All eval tasks run **in-process** via FastAPI's `AsyncClient(ASGITransport)`. No
  server needs to be started. No network. This makes them runnable from `make` or CI
  with only a Postgres service container.

## Metrics

- **pass@k** — fraction of tasks that pass on a single attempt, k trials run.
  `pass@k = num_passing / k`. We run 3 trials per task by default (`DEFAULT_TRIALS=3`).
- **pass^k** — fraction of trials that pass, i.e. consistency across repeats with
  fresh DB state per trial. `pass^k = total_passes / total_trials`.
  (The caret notation `pass^k` here means "k-shot consistency", not exponentiation.)

A task with `pass@k = 1.0, pass^k = 1.0` is both correct and deterministic.
A task with `pass@k = 0.0` has a genuine bug or gap.
A task with `0 < pass@k < 1` is **flaky** and must be investigated (constitution §31).

## Workflow

1. `evals/tasks/NNN-*.task.yaml` — one file per client-facing workflow scenario.
   Schema: `id, name, description, input, agent_steps, verification, grader, trials`.
2. `evals/graders/code_based.py` — deterministic asserts against DB + API state.
   Primary grader. Each task's `grader` references a function here by name.
3. `evals/graders/llm_judge.py` — rubric-based grading for subjective outcomes only.
4. `evals/graders/human_review_template.md` — template for things neither can judge.
5. `evals/run_evals.py` — the runner. Loads `tests/conftest.py` fixtures, runs each
   task N times, collects pass/fail, writes `evals/transcripts/<id>.trial-N.json`
   and appends to `evals/outcomes/pass@k.json`.
6. `evals/reports/<date>-baseline.md` — the results report with measured numbers.

Run locally:
```
cd /Users/srujansai/Desktop/swa-erp-worktrees/w43
pytest -x evals/graders/code_based.py -q
# or the full harness:
python3 evals/run_evals.py --trials 3
```

Requires a Postgres at `postgresql://swa:swa@localhost:5432/swa_erp_test`
(same as the existing test DB — see `.env.example`).

## Anti-patterns (§4.24 / §6.9)

These are the traps that produce "fake CI gates" — exactly the failure mode this
repo had before wave-32 sealed it. Each must be avoided:

1. **Asserting on UI text instead of state.** "Looks right" ≠ "is right". Every
   code-based grader asserts on DB rows, API return payloads, or Decimal arithmetic.
   No `assert "GST" in response.text` — use `assert inv["gst_amount"] == Decimal("18.00")`.
2. **Flaky ordering assumptions.** List endpoints are paginated + ordered by
   `created_at DESC`. Graders never assume row position; they filter by a known key.
3. **Silent float money.** `0.1 + 0.2 != 0.3`. All money checks use `Decimal` and
   `.quantize(Decimal("0.01"))`.
4. **Non-deterministic reference IDs.** `generate_reference_id` uses a postgres
   `ON CONFLICT` counter (real ID). Graders validate the format regex
   `^SWA-\d{4}-[A-Z]+-\d{3}$` and sequence monotonicity — never assert an exact ID.
5. **RBAC as "status code not 500".** A Viewer getting 500 instead of 403 is a bug,
   not a pass. We assert the *exact* 403 and that the DB row is absent.
6. **Evals as a shipping gate.** The evals workflow file is `continue-on-error: true`.
   The README, the workflow header, and this section state it explicitly. Nobody
   mistakes it for a real block.
7. **Grader coupled to implementation, not contract.** If the service renames a
   field, the grader should fail loudly (schema), not silently pass on a stale path.
   Graders import the same Pydantic schemas the API returns.
8. **One trial = proof by anecdote.** A single green run is not evidence. We run
   3 trials per task and report `pass^k`. 1/3 passing is a flaky-failure signal,
   not a "mostly works" win.

## Directories

```
evals/
├── README.md                 (this file)
├── tasks/
│   ├── 001-inquiry-to-client-conversion.task.yaml
│   ├── 002-agreement-token-docref-chain.task.yaml
│   ├── 003-rbac-enforcement.task.yaml
│   ├── 004-time-log-to-dashboard.task.yaml
│   └── 005-invoice-gst-correctness.task.yaml
├── graders/
│   ├── code_based.py         (deterministic — primary)
│   ├── llm_judge.py          (rubric — subjective only)
│   └── human_review_template.md
├── run_evals.py              (harness: runs tasks N times, writes outcomes)
├── trials/
│   └── .gitkeep
├── transcripts/
│   └── .gitkeep
├── outcomes/
│   └── .gitkeep
└── reports/
    ├── .gitkeep
    └── 2026-08-28-baseline.md
```
