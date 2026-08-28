# Human Review Template — Wave-43 Evals

Use this template ONLY when the code-based grader cannot determine pass/fail
(e.g. "is the error message helpful to a human user?"). The code-based grader
is always authoritative for behavioral correctness (status codes, DB state,
Decimal arithmetic). This template is for the residual subjective layer.

---

## Trial under review
- **Task ID**: `_____`
- **Trial**: `#` of `#`
- **Timestamp**: `_____`
- **Transcripts**: `evals/transcripts/<task_id>.trial-<N>.json`

## Rubric

Score each criterion 0–2. **0 = failing / absent**, 1 = partial, 2 = fully satisfactory.

### 1. Response clarity
> The system's final response or error message is unambiguous and actionable.

| Score | Meaning |
|-------|---------|
| 0 | Message is confusing, contradictory, or missing entirely |
| 1 | Message is understandable but requires domain guesswork or lacks a next step |
| 2 | Clear, uses client-domain language (e.g. "SWA-2026-INQ-003"), tells the user what to do next |

**Notes:**

### 2. Audit trail completeness
> Every user-facing mutation produced an `audit_log` entry with before/after JSON.

| Score | Meaning |
|-------|---------|
| 0 | No audit entry, or before/after is empty |
| 1 | Audit entry exists but before/after JSON is sparse |
| 2 | At least one audit entry per mutation, with non-trivial before/after |

**Notes:**

### 3. Error helpfulness
> When the system errored, the error explains the cause and lists recoverable options.

| Score | Meaning |
|-------|---------|
| 0 | Generic 500 / stack trace exposed / no recovery hint |
| 1 | Error names the rule but no concrete fix or wrong status code |
| 2 | Names the violated rule, suggests a concrete fix, uses 4xx (not 5xx) |

**Notes:**

## Overall verdict
- **Code-based grader**: PASS / FAIL / (see transcript)
- **Human score**: ___ / 6
- **Final**: PASS (≥4) / FAIL (<4)
- **Recommendation**: 

---

Reviewer: `___________________  Date: _________`
