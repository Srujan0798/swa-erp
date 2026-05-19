---
name: diagnose
description: Systematic debug guidance when a worker report is BLOCKED or tests are failing in unclear ways.
---

# diagnose

## Steps
1. Read the error message FULLY — don't skim
2. Reproduce in isolation: minimal failing test
3. Bisect: which commit / file / function introduced the issue?
4. Check the obvious:
   - Is the right DB up?
   - Is .env loaded?
   - Did migrations apply?
   - Is the right Python venv active?
5. Check the data flow:
   - Frontend → API: open browser devtools
   - API → DB: enable SQLAlchemy echo
   - DB query: run it in psql directly
6. If still stuck: spawn `codebase-explorer` to map the call path
7. Document the fix as an ADR if the bug class is likely to recur
