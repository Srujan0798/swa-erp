---
name: plan
description: Decompose a wave into spec + plan + tasks files. Usage /plan wave-N
---

# /plan

## What this does
Reads or writes `.specify/specs/wave-N/spec.md` (creating it from `plan/PRD.md` if missing).
Produces:
- `.specify/specs/wave-N/plan.md` — technical plan, file layout, dependencies
- `.specify/specs/wave-N/tasks.md` — ordered task breakdown (4–8 tasks)
- `.specify/specs/wave-N/contracts/` — executable acceptance tests

## Steps
1. Read or write spec.md (functional, user stories, success criteria)
2. Pick technical approach from `plan/ARCHITECTURE.md`
3. Decompose into tasks — each task is one OpenCode worker session
4. For each task, define files, acceptance, skills, constraints
5. Write contracts as runnable pytest/playwright tests
6. Update `plan/EXECUTION.md` wave graph

## Output
"Wave N planned. {COUNT} tasks ready. Run /dispatch wave-N to write task files."
