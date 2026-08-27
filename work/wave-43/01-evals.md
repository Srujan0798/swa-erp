# Wave-43 Task 01 — evals/ as a first-class directory (Anthropic Jan 2026)

Adaptoid v1.3 SOTA (§4.23–4.24). This repo has tests but **no evals**. Tests check code paths; evals check whether the *system does the job the client asked for*. For an internship submission this is a genuine differentiator — most submissions have neither.

## Files you own (touch nothing else)
- `evals/README.md`
- `evals/tasks/*.task.yaml` (≥5)
- `evals/graders/{code_based.py,llm_judge.py,human_review_template.md}`
- `evals/{trials,transcripts,outcomes,reports}/` (with `.gitkeep`)
- `.github/workflows/evals.yml` (the ONLY workflow file you may touch)

## Ground truth
- Stack: FastAPI + SQLAlchemy 2 + Postgres backend; React 18 + Vite frontend; Playwright already configured (`playwright.config.ts`, `tests/e2e/`).
- Seeded demo users exist (see `make seed-demo` / `scripts/`); reference IDs follow `SWA-{year}-{TYPE}-{seq:03d}`.
- The evals must target the **client's real workflow**, not toy cases.

## The work

### 1. `evals/README.md`
Per §4.24: state the framework choice (Harbor / Braintrust / Phoenix — or a plain pytest harness if those aren't available; justify honestly), the metrics (**pass@k** and **pass^k**), the workflow, and the anti-patterns.

### 2. At least 5 eval tasks (`evals/tasks/NNN-*.task.yaml`, schema in §4.23)
Cover the chain that actually matters to the client:
- `001-inquiry-to-client-conversion` — including the ambiguous-match branch (existing client vs new)
- `002-agreement-token-docref-chain` — IDs generate in correct format and sequence, no gaps, no collisions
- `003-rbac-enforcement` — each role sees exactly what it should; a Viewer cannot mutate
- `004-time-log-to-dashboard` — a logged entry surfaces correctly in aggregates
- `005-invoice-gst-correctness` — GST computed correctly, money stays `Decimal(18,2)`

Each needs: input/initial state, agent execution steps, **outcome verification** (what environmental state counts as success — not "looks right"), grader, and trials count.

### 3. Graders
- `code_based.py` — deterministic asserts against DB/API state. This is the primary grader; prefer it.
- `llm_judge.py` — rubric grading for anything genuinely subjective. Keep the rubric explicit.
- `human_review_template.md` — for what neither can judge.

### 4. `.github/workflows/evals.yml`
Runs the code-based evals against a seeded stack. Non-blocking at first (`continue-on-error` is acceptable HERE and only here, because evals are new and flaky-by-nature until tuned) — **but say so explicitly in the README**, so nobody mistakes it for a real gate. This repo has a documented history of fake CI gates; do not create another one silently.

### 5. Record real results
Run the evals. Write `evals/reports/2026-08-28-baseline.md` with actual pass@k / pass^k figures. Save transcripts to `evals/transcripts/`.

## Acceptance criteria
- [ ] `find evals -type f` shows README + ≥5 tasks + 3 graders + the workflow — paste it
- [ ] The code-based grader actually runs and produces real pass/fail — paste output
- [ ] `evals/reports/2026-08-28-baseline.md` contains measured numbers, not projections
- [ ] README states plainly that evals.yml is non-blocking and why
- [ ] Anti-patterns section written (§4.24 / §6.9)

## Deliver
`work/reports/wave-43/01-evals.report.md`. Commit before writing it.

## Constraints
- Time budget: 180 min · commit per grader/task group
- Zero application-code changes unless an eval reveals a genuine bug — if it does, report it, don't silently fix
