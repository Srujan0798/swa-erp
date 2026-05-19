# Dispatch Protocol — How to write task files

## Rule #1 — Self-contained
Workers (OpenCode CLI) have ZERO project memory. Every task file MUST contain everything needed:
- Files to create, modify, NOT touch
- Inline schemas, examples, sample inputs
- Acceptance criteria (executable, not prose)
- Time + token budget
- Skills the worker should use (from their library, NOT yours)

## Rule #2 — Skills are theirs, not yours
Workers use skills from:
- Their local `skills.sh` library
- Claude built-ins
- agentskills.io online catalog

They do NOT have access to `orchestrator/skills/`. List worker skills by NAME so they can install/lookup.

Common worker skills to list:
- `tdd`, `code-review`, `diagnose`
- `pdf-processing`, `excel-processing`, `web-scraping`
- `api-design`, `database-migration`
- Domain-specific by name

## Rule #3 — Acceptance is executable
Bad: "Make sure it works."
Good: "`pytest tests/wave-1/test_auth.py` exits 0."

Bad: "UI looks nice."
Good: "Playwright test `test_login_flow.py` passes; screenshot matches reference."

## Rule #4 — Files MUST NOT touch
Always list FORBIDDEN paths. Examples:
- Migrations from earlier waves
- Production config
- Other workers' in-flight files

## Rule #5 — Time + token budget
Set realistic budgets. If a task needs >2h or >50k tokens, split it.

## Template structure
See `work/TASK_TEMPLATE.md` for the exact format.

## When the task is ambiguous
Run `agents/interviewer.md` to ask the user — don't dispatch ambiguous briefs to workers.
