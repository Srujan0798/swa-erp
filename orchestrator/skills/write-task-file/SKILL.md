---
name: write-task-file
description: Produce self-contained worker task briefs that require zero project context to execute. Use when dispatching work to OpenCode CLI workers. Critical skill for orchestrator-workers pattern.
---

# write-task-file

## When to use
After /plan produces tasks.md, dispatch each task by writing a self-contained brief in `work/<wave>/`.

## Steps
1. Read the task entry in `.specify/specs/wave-N/tasks.md`
2. Identify:
   - Files to create / modify / forbidden
   - Acceptance criteria (executable)
   - Domain context the worker needs INLINE
3. Inline relevant schemas, examples, sample I/O — do NOT reference external files
4. List worker-side skills (tdd, code-review, domain-specific) — NOT orchestrator skills
5. Set time + token budget
6. Use `work/TASK_TEMPLATE.md` format
7. Write to `work/wave-N/0X-task-name.md`

## Anti-patterns to avoid
- Referencing `orchestrator/skills/` — workers can't see them
- "Look at the spec for details" — inline what's needed
- Vague acceptance criteria — must be runnable
- Combining multiple tasks into one brief

## Quality checklist
- [ ] A new contractor could execute with ONLY the task file
- [ ] Acceptance commands are runnable
- [ ] Forbidden paths explicit
- [ ] Worker skills listed by name (so they can install/lookup)
