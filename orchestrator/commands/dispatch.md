---
name: dispatch
description: Write self-contained task files into work/. Usage /dispatch wave-N
---

# /dispatch

## What this does
For each task in `.specify/specs/wave-N/tasks.md`, produces a self-contained brief in `work/wave-N/`.

## Steps
1. Load tasks list
2. For each task, invoke `skills/write-task-file/SKILL.md`
3. Fill TASK_TEMPLATE with:
   - Inline schemas, examples, sample I/O — no external references
   - Acceptance criteria from `contracts/`
   - Worker-side skills (tdd, code-review, pdf-processing, etc.) — NOT orchestrator skills
   - Files to create + forbidden paths
4. Write to `work/wave-N/0X-task-name.md`

## Output
"{COUNT} task files in work/wave-N/. Paste any into OpenCode CLI to dispatch."
