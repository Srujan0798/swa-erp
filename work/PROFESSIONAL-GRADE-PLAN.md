# Professional-Grade Plan — waves 32-38

**Context:** this is an **industry internship submission**, evaluated by professionals against a
production bar — not a "does it run" demo. The product works (417 tests pass, core chain
verified). The gap is **evidence quality and engineering rigor**, not features.

**Measured baseline (2026-08-11, verified by running it — not claimed):**

| Dimension | Actual now | Target |
|---|---|---|
| Backend coverage | **82%** (`pdf_service` 17%, `quote_service` 21%, `task_service` 58%, `notification_service` 50%, `import_service` 65%) | ≥85% overall, **no module <70%** |
| Frontend tests | **2 test files / 128 source files** (~0%) | ≥60% on hooks + critical components |
| CI enforcement | **Every gate is `\|\| true`** — ruff, black, mypy, pytest, npm lint, pip-audit, npm audit, plus `continue-on-error: true`. **CI cannot fail.** | Real gates, merge-blocking |
| Type safety | mypy configured but **never enforced** (`\|\| true` since day 1) | `mypy --strict` gating |
| SAST / secrets / supply chain | **never run** | semgrep clean, triaged |
| "100+ concurrent users" | **claimed in docs, never tested** | load-tested with published numbers |
| Observability | structured logs only | metrics + error tracking |
| E2E | 7 Playwright tests | critical paths covered |
| Independent review | none | multi-agent review, findings closed |

## The central problem to fix first

**A CI that cannot fail is worse than no CI** — it produces a green badge that means nothing. Any
reviewer who opens `.github/workflows/ci.yml` sees `|| true` on every line and correctly
concludes the quality signals are theater. **Wave-32 fixes this before anything else**, because
every later wave's evidence depends on gates that actually gate.

## Wave map (dependency-ordered)

```
32  CI/CD hardening + real quality gates        ← MUST BE FIRST (everything depends on it)
     │
     ├── 33  Backend coverage: close weak modules to ≥85%
     ├── 34  Frontend test suite: 2 → real coverage      } can run in parallel
     └── 35  Performance + load validation (prove 100 users)
     │
     ├── 36  Observability (metrics, error tracking)
     │
     └── 37  Independent multi-agent review  ← after 33/34/35 land (reviews the real thing)
              │
              └── 38  Professional submission package  ← LAST (packages verified reality)
```

## Capabilities to actually use (previously unused)

| Wave | Tool/skill | Why |
|---|---|---|
| 32 | `semgrep` MCP (`get_semgrep_sast_findings`, `_secrets_`, `_supply_chain_`) | Real SAST — ruff is a linter, not a security scanner |
| 33 | `superpowers:test-driven-development` | Disciplined coverage work, not test-padding |
| 34 | `frontend-design`, Vitest + React Testing Library | Component testing done properly |
| 35 | `locust` (**already in requirements.txt, never used**) | Load-test the 100-user claim |
| 37 | `/code-review ultra`, `/security-review`, `pr-review-toolkit` agents (silent-failure-hunter, type-design-analyzer, pr-test-analyzer) | Independent adversarial review |
| 38 | Artifacts (publishable HTML), `dataviz`, `design` | A submission showcase, not a markdown dump |

## Non-negotiable standards for every wave

1. **No `|| true`, no `continue-on-error`, no skipped assertions** to make something pass.
2. **Every number in a report must come from a command run that session**, with output pasted.
   This project has a documented history of self-reported passes that weren't real.
3. **A truthful "NOT DONE + blockers" beats a green report that hides a failure.**
4. Commit your work with git before writing your report.
5. Run the full suite before claiming done — and check `ps aux | grep pytest` first; this suite
   produces false mass-failures under concurrent runs (see `docs/PROJECT_HISTORY.md`).

## What this plan does NOT do

- Add features. The feature set is complete and client-confirmed. This is entirely about
  engineering quality, evidence, and presentation.
- Touch the client's data or deployment. Server deploy is blocked on Viraj (no IT dept) and is
  outside this plan.
