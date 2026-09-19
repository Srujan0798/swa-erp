# Wave-32 Task 01 — Make CI real (remove all fake gates) + add security scanning

**THIS WAVE RUNS FIRST AND ALONE.** Every later wave's evidence depends on gates that actually
gate. Do not dispatch 33-38 until this lands.

## The problem (measured, not hypothetical)

`grep -n "|| true\|continue-on-error" .github/workflows/*.yml` returns **11 hits**:
- `ci.yml`: ruff, black, mypy, pytest, npm lint — all `|| true`
- `security.yml`: pip-audit, npm audit — `|| true`; plus one `continue-on-error: true`
- `test.yml`: unit, integration, contract tests — all `|| true`

**The CI is physically incapable of failing.** A green badge means nothing. Any professional
reviewer who opens these files sees this immediately and discounts every quality claim.

Additionally: `mypy` is configured in `pyproject.toml` but has been `|| true` since day one, so
the codebase has **never** been type-checked in anger.

## Files to modify
- `.github/workflows/ci.yml`, `security.yml`, `test.yml`
- `pyproject.toml` — coverage config + thresholds
- `Makefile` — add `make verify` running the same gates locally (so devs catch it pre-push)

## Files you must NOT touch
- Application code under `src/` — **except** the minimum needed to make mypy pass (see below).
  This is a CI/tooling wave, not a refactor wave.
- Tests — if a test fails once gates are real, that's a finding to report, not something to
  delete or skip.

## The work

### 1. Remove every `|| true` and `continue-on-error`
Make each gate genuinely fail the build. Expect this to go red immediately — **that is the
point**. Then fix what it surfaces, in this order of preference:
1. Fix the underlying issue.
2. If it's a rule genuinely inappropriate for this codebase (e.g. `B008` on FastAPI's `Depends`
   idiom), add a **scoped, commented** ignore in config — never a blanket suppression.
3. If something can't be fixed in this wave's budget, **report it as a known failure with a
   plan** — do not restore `|| true` to hide it.

### 2. Enforce mypy
Start with `mypy src/backend/` non-strict and gating. Fix what appears. Then attempt
`--strict`; if strict produces an unreasonable volume for one wave, **enable strict per-module**
starting with `core/`, `services/`, `models/` and record the remaining modules as a follow-up
list in your report. Document the chosen setting in `pyproject.toml` with a comment.

### 3. Coverage gates
Backend coverage measured today is **82%**. Configure `pytest-cov` (already installed) with:
- `--cov=src/backend --cov-report=term-missing --cov-report=xml`
- `--cov-fail-under=82` initially (lock in today's number so it can't regress)
Wave-33 raises the floor to 85 after closing weak modules. **Do not set it to 85 now** — that
would fail the build for work wave-33 hasn't done yet.

### 4. Real security scanning (currently zero)
Use the **semgrep MCP tools** — these are available to you and have never been run on this repo:
- `get_semgrep_sast_findings` — code vulnerabilities
- `get_semgrep_secrets_findings` — committed credentials
- `get_semgrep_supply_chain_findings` — vulnerable dependencies

Triage every finding into: **fixed**, **false positive (with reason)**, or **accepted risk (with
reason)**. Add a semgrep step to `security.yml` that gates on high/critical. Also make
`pip-audit` and `npm audit` real (remove their `|| true`) — triage the same way.

### 5. `make verify`
One command running the full gate set locally, identical to CI, so failures are caught before
push. Wire it into the docs (`docs/runbook.md`, `CONTRIBUTING.md`).

## Acceptance criteria
- [ ] `grep -rn "|| true\|continue-on-error" .github/workflows/` returns **zero** hits
- [ ] Deliberately break something trivial (e.g. add an unused import), push to a scratch branch,
      and **confirm CI actually goes red** — paste the evidence. Then revert. This is the single
      most important check in this wave: prove the gates work.
- [ ] `mypy src/backend/` passes at the documented setting
- [ ] `python3 -m pytest tests/ -q --cov=src/backend --cov-fail-under=82` passes
- [ ] Semgrep SAST + secrets + supply-chain run; every finding triaged in the report
- [ ] `make verify` passes locally and runs the same gates as CI
- [ ] Full suite still **417 passed / 6 skipped / 0 failed** minimum

## Deliver
Report → `work/reports/wave-32/01-real-ci-quality-gates.report.md`. Must include: the before/after
`|| true` count, the CI-actually-fails proof, the mypy setting chosen and why, full semgrep
triage table, and any known failures you're handing forward with a plan. Commit before writing.

## Constraints
- Time budget: 150 min
- **Never** restore a `|| true` to make something pass
- Allowed: file edit, git, gh, pytest, ruff, mypy, semgrep MCP, npm
