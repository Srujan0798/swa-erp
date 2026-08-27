---
name: plan-wave
description: Decompose a PRD section into a wave with spec, plan, tasks, and contracts. Use at the start of every wave.
version: 1.0.0
allowed-tools:
  - write_file
  - read_file
  - search_files
  - patch
  - terminal
invocation: agent
subagent: true
---

# plan-wave

## Steps
1. Read `plan/PRD.md` and `plan/ARCHITECTURE.md`
2. Identify which PRD section this wave delivers
3. Write `.specify/specs/wave-N/spec.md` (user stories + acceptance)
4. Write `.specify/specs/wave-N/plan.md` (tech choices, file layout, deps)
5. Decompose into 4–8 tasks in `tasks.md` with dependency graph
6. For each task, draft `contracts/` test files (pytest, playwright, golden, fuzz)
7. Update `plan/EXECUTION.md`

## Heuristics
- One task = one worker session (≤ 2 hours, ≤ 50K tokens worker context)
- If a task is bigger, split it
- Acceptance contracts must exist BEFORE dispatch (TDD-ish)
- Parallel tasks shouldn't share files
