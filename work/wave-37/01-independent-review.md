# Wave-37 Task 01 — Independent adversarial review (multi-agent)

**Depends on waves 32, 33, 34, 35 landing.** Reviewing before those land wastes the review on
code that's about to change. Verify their reports exist first.

## Why this wave exists

Everything reviewed so far has been reviewed by the same orchestrator that planned it. That's a
structural blind spot. For an industry submission, the codebase should survive **adversarial
review by reviewers that did not write it** — and this project has specialised review tooling
that has never once been used.

## The tooling to actually use (all previously unused)

Run **all** of these — they find different classes of problem:

| Tool | Finds |
|---|---|
| `/code-review ultra` | Deep multi-agent cloud review of the branch |
| `/security-review` | Security-specific pass over the diff |
| `pr-review-toolkit:silent-failure-hunter` | Swallowed exceptions, bad fallbacks, errors that vanish |
| `pr-review-toolkit:type-design-analyzer` | Types that don't encode their invariants |
| `pr-review-toolkit:pr-test-analyzer` | Tests that don't actually test what they claim |
| `pr-review-toolkit:comment-analyzer` | Comments that lie about the code (comment rot) |
| `feature-dev:code-reviewer` | General correctness/convention pass |

**`silent-failure-hunter` is the highest-value one here.** This codebase has a documented history
of exactly that failure mode: a rate limiter that silently 429'd the whole test suite, a
`soft_delete()` that hard-deleted, CI gates that couldn't fail, a financial PDF that fabricated
numbers from a hardcoded ratio. Point it at the whole backend, not just recent changes.

## Scope
Review the **full codebase**, not just a diff — this is a submission audit, not a PR review.
Prioritise:
1. `src/backend/services/` — business logic, money handling, the core chain
2. `src/backend/api/` — RBAC enforcement, input validation
3. `src/backend/db/repositories/` — query correctness, N+1, soft-delete consistency
4. `src/frontend/src/hooks/` + core-chain components

## Files you must NOT touch (during the review phase)
Nothing. **This is a read-and-report wave.** Fixes come after triage — see below.

## Process

### Phase 1 — Review (read-only)
Run every tool above. Collect all findings into one deduplicated list.

### Phase 2 — Triage
For each finding, classify honestly:
- **CONFIRMED BUG** — reproduce it; write a failing test that demonstrates it
- **RISK** — not a bug today, but fragile (document it)
- **FALSE POSITIVE** — state why, specifically; don't dismiss with "not applicable"

**Reviewers are not automatically right.** This project has already seen agents assert things
that weren't true (a worker's todo list claiming 4 files were fixed when they weren't; a report
claiming a test file didn't exist when it did). Verify every finding against the actual code
before accepting or rejecting it.

### Phase 3 — Fix (only what triage confirmed)
Fix CONFIRMED BUGs, each with a regression test. Leave RISKs documented. If a fix is too large
for this wave, file it clearly rather than half-doing it.

## Acceptance criteria
- [ ] All 7 tools run; report states what each was pointed at and what it returned
- [ ] Every finding triaged with an explicit verdict + reasoning (a table)
- [ ] Every CONFIRMED BUG has a **failing-test-first** fix — show the test failing before the fix
- [ ] Full suite green afterwards, coverage not reduced
- [ ] `ruff`, `mypy`, frontend `tsc`/`eslint` all still clean (wave-32's real gates)
- [ ] **Zero unexplained dismissals** — every rejected finding has a specific reason

## Deliver
Report → `work/reports/wave-37/01-independent-review.report.md`: full findings table, triage
verdicts, fixes with evidence, and an honest "what we chose not to fix and why." Commit before
writing.

## Constraints
- Time budget: 240 min (largest wave — it's running 7 review passes plus fixes)
- **Do not suppress a finding to make the report look clean.** A report with 12 honestly-triaged
  findings is stronger evidence of rigour than one claiming zero issues.
- Allowed: all review tooling, file edit, git, pytest, ruff, mypy, npm
