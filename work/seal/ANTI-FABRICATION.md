# Anti-Fabrication Protocol (non-negotiable)

This repository has a **documented history** of agents claiming work that did not exist. Closing the project with one more fake green report would destroy the value of waves 32–36.

---

## Hard bans (never write these)

1. **“100% complete”** while wave-37 or wave-38 is unfinished, or while suite is red.
2. **“562 passed”** (or any collected count presented as passed).
3. **“0 failed”** when the 5 auth tests still fail.
4. **“No module under 70%”** as a **global** backend claim (false — 9+ non-alembic modules still under).
5. **Frontend 65.86%** without a fresh `vitest --coverage` paste from this session.
6. **“CI cannot fail / all green”** if workflows or suite disagree.
7. **“MinIO not built” / “Celery not wired”** after wave-31.
8. Inventing test file paths that `ls` does not show.
9. Marking todos DONE when the file was never edited.
10. Running wave-38 metrics from memory of wave-33/34 reports.

---

## Required form for every metric

```text
CLAIM: <number>
COMMAND: <exact command>
OUTPUT: <paste or cite report path + commit>
DATE: <ISO date>
```

If you cannot fill OUTPUT, delete the CLAIM.

---

## Historical incidents to remember

| Wave | Lie | Correction |
|---|---|---|
| 33-01 | Claimed wave-33 test files + coverage | Files missing → NOT DONE + redo |
| 36-02 | “458 passed, 0 fail” | Still 5 standing failures |
| 33-03 | “562 passed” | 557 passed + 5 failed |
| 22 | Todo said 4 RBAC files fixed | Untouched until orchestrator fixed |
| 23 | PDF numbers from hardcoded ratio | Real calculation required |
| 15 | “pytest already broken on main” | Suite was green |

---

## Concurrent pytest rule

If you see mass `DeadlockDetected` / `UniqueViolation` / hundreds of ERRORS:
- **Do not** conclude the code is broken.
- Kill other pytest/opencode test runners.
- Re-run **once** solo.
- Only then trust the number.

---

## Report honesty template line

Every close report must include:

> Independent verification: command run this session. Failures listed by node id. Coverage from this run’s TOTAL line. Known pre-existing issues: none / listed.
