# Advanced Audit Prompt v2 — Comprehensive Codebase Review

> Use for periodic deep audits, pre-submission reviews, or when inheriting a codebase.
> This prompt runs a multi-agent review covering security, correctness, architecture, tests, and maintainability.

---

## Prerequisites

- Working directory: project root
- Git status: clean or only review-related changes
- Test suite: passing (run `pytest tests/ -q --tb=no` first)
- Lint: clean (`ruff check . && npm run lint` in frontend)

---

## Phase 0 — Context Gathering (Run First)

```bash
# Capture baseline metrics
git log -1 --oneline
pytest tests/ --collect-only -q 2>&1 | tail -5
ruff check . --output-format=concise 2>&1 | wc -l
cd src/frontend && npx tsc --noEmit 2>&1 | tail -3
```

Record output in the audit report header.

---

## Phase 1 — Multi-Agent Review (Read-Only)

Run **all** tools below against the **full codebase** (not just a diff). Each tool targets different failure modes.

| Tool / Agent | Target | What It Catches |
|---|---|---|
| **Security Review** | `src/backend/**/*.py` | Auth bypasses, injection, secrets, crypto misuse, RBAC gaps |
| **Code Review (ultra/deep)** | Full repo | Architecture drift, coupling, dead code, convention violations |
| **Silent Failure Hunter** | `src/backend/services/`, `src/backend/workers/` | Swallowed exceptions, empty catch blocks, fallback values masking errors, retry loops without backoff |
| **Type Design Analyzer** | `src/backend/schemas/`, `src/backend/models/` | Types that don't encode invariants (e.g., `status: str` vs enum), missing discriminated unions, `Any` leakage |
| **PR Test Analyzer** | `tests/` | Tests that don't test what they claim, missing edge cases, flaky patterns, test-only code paths |
| **Comment Analyzer** | `src/**/*.py`, `src/**/*.tsx` | Stale comments, misleading docstrings, commented-out code, `TODO` without owner/date |
| **Dependency/Supply Chain** | `requirements.txt`, `package.json` | Known vulnerabilities, unmaintained deps, license conflicts, version pinning |

### Execution Order (Recommended)

1. **Silent Failure Hunter** — Highest signal-to-noise for this codebase
2. **Security Review** — Must-pass for any submission
3. **Type Design Analyzer** — Catches latent bugs in schemas/models
4. **Code Review (ultra)** — Broad architectural view
5. **PR Test Analyzer** — Validates test quality
6. **Comment Analyzer** — Low effort, catches rot
7. **Dependency Audit** — Run `pip-audit` / `npm audit`

### Tool Invocation Pattern

```
# Example for each tool (adapt to your environment)
/security-review src/backend/
/code-review ultra --scope=full
# For pr-review-toolkit agents, invoke via their specific command pattern
```

---

## Phase 2 — Specialized Deep Dives (Manual)

After automated reviews, manually inspect these high-risk areas:

### A. Money & Financial Correctness
- [ ] All monetary fields use `Decimal` / `Numeric(18,2)` — no `float`
- [ ] GST/tax calculations use exact arithmetic, tested with edge cases
- [ ] Rounding policy documented and consistently applied
- [ ] No silent truncation in aggregation queries

### B. Authorization & RBAC
- [ ] Every mutating endpoint has explicit role check
- [ ] Project-scoped resources verify membership (not just global role)
- [ ] No "admin bypass" that skips project membership
- [ ] Rate limits on auth/upload/export endpoints

### C. Data Integrity & Soft-Delete
- [ ] All repositories filter `deleted_at.is_(None)` by default
- [ ] Cascade deletes match business rules (no orphan references)
- [ ] Unique constraints work with soft-delete (partial indexes)
- [ ] Audit log covers all mutating operations

### D. Async / Background Jobs
- [ ] Celery tasks have idempotency keys or natural idempotency
- [ ] Task retries have exponential backoff + max retries
- [ ] Worker healthcheck validates broker + result backend
- [ ] Export jobs record ownership before returning 202

### E. Frontend-Backend Contract
- [ ] OpenAPI types match frontend TypeScript interfaces
- [ ] Pagination envelope consistent across all list endpoints
- [ ] Error response shape standardized (RFC 7807 or similar)
- [ ] No `any` in API client layer

---

## Phase 3 — Findings Triage

For **every** finding from Phases 1-2, classify:

| Verdict | Criteria | Action |
|---|---|---|
| **CONFIRMED BUG** | Reproducible failure, violates spec/contract | Write failing test → fix → verify |
| **RISK** | Not a bug today; fragile, undocumented assumption, or tech debt | Document in `RISKS.md` with mitigation |
| **FALSE POSITIVE** | Tool misunderstanding, intentional design, already mitigated | Document specific reason in report |

### Triage Rules
- **No auto-accept**: Verify each finding against actual code
- **No auto-reject**: "Not applicable" requires specific evidence
- **Reviewer fallibility**: Tools hallucinate; this codebase has seen false claims (e.g., "file doesn't exist" when it does, "4 files fixed" when 0 were)
- **Time-box**: Max 30 min per finding for triage

---

## Phase 4 — Fix & Verify (CONFIRMED BUGs Only)

For each CONFIRMED BUG:
1. Write a **failing test first** (regression test)
2. Run test → confirm failure
3. Apply minimal fix
4. Run test → confirm pass
5. Run full suite → no regressions
6. Run lint/typecheck → clean

**Do not** fix RISKs in this wave unless trivial and tested.

---

## Phase 5 — Report Generation

Generate `audit-report-<date>.md` with:

### Header
```
# Audit Report — <project> — <date>
Git: <commit-hash> (<branch>)
Baseline: <pytest count> tests, <ruff issues> lint, <tsc errors> type
```

### Findings Table
| ID | Tool | File:Line | Severity | Verdict | Summary |
|---|---|---|---|---|---|
| A-01 | silent-failure-hunter | services/export_service.py:340 | HIGH | CONFIRMED BUG | Empty except catches Celery retry |

### Triage Summary
| Verdict | Count |
|---|---|
| CONFIRMED BUG | N |
| RISK | N |
| FALSE POSITIVE | N |

### Fixes Applied
| ID | Test Added | Fix Summary | Verification |
|---|---|---|---|
| A-01 | tests/test_export_retry.py::test_retry_on_transient_error | Added specific exception handling | pytest -xvs tests/test_export_retry.py ✓ |

### Risks Documented
| ID | Description | Mitigation | Owner |
|---|---|---|---|
| R-01 | Notification service commits in list() | Add explicit read-only mode | @backend-lead |

### Metrics
- Test suite: `<count>` passed, `<count>` failed
- Coverage: `X%` (backend), `Y%` (frontend)
- Lint: clean / `N` issues
- Typecheck: clean / `N` errors

---

## Anti-Fabrication Rules (Non-Negotiable)

1. **Real output only** — Paste actual command output, not summaries
2. **One test suite at a time** — Concurrent pytest = deadlocks = false results
3. **No inflated claims** — "100% complete", "no module <70%", "65.86% frontend" require fresh run evidence
4. **Cite evidence** — Every metric references a report path or command output
5. **Zero unexplained dismissals** — Every rejected finding has a specific, verifiable reason

---

## Usage

```bash
# In a fresh session:
cat prompts/advanced-audit-v2.md
# Follow Phase 0 → Phase 5 sequentially
# Commit report when done
```

---

## Version History

| Version | Date | Changes |
|---|---|---|
| v1 | 2026-08 | Initial (wave-37) |
| v2 | 2026-09 | Added Phase 0 metrics, Phase 2 deep dives, anti-fabrication rules, findings table template |

---

## Related Files

- `docs/decisions/0003-soft-delete-exceptions.md` — Soft-delete model coverage
- `docs/decisions/0004-api-versioning-idempotency.md` — API versioning target state
- `docs/ARCHITECTURE.md` — Current architecture baseline
- `work/wave-37/01-independent-review.md` — Original wave-37 prompt (v1 basis)