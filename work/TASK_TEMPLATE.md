# Task — {{TASK_NAME}}

## What to do
{{ONE_PARAGRAPH_GOAL}}

Reference spec: `.specify/specs/wave-{{N}}/spec.md` section {{SECTION}}.

## Files to create / modify
- CREATE: {{PATH_1}}
- CREATE: {{PATH_2}}
- MODIFY: {{PATH_3}}

## Files you must NOT touch
- {{FORBIDDEN_PATH_1}}
- {{FORBIDDEN_PATH_2}}

## Skills to use (from YOUR worker skill library)
- `{{SKILL_NAME_1}}` — install from agentskills.io if not present
- `{{SKILL_NAME_2}}`
- `tdd` — red → green → refactor
- `code-review` — self-review before declaring done

(Note: these are skills your OpenCode CLI / agent has access to.
They are NOT skills from this project's `orchestrator/skills/` folder.)

## The core problem (inline — no external context needed)
{{INLINE_PROBLEM_DESCRIPTION}}

### Inputs available (paste inline)
{{INLINE_SCHEMAS_SAMPLES_EXAMPLES}}

### Edge cases to handle
- {{EDGE_1}}
- {{EDGE_2}}

## Acceptance criteria (executable, not prose)
- [ ] `{{TEST_COMMAND_1}}` passes
- [ ] `{{LINT_COMMAND}}` clean
- [ ] {{BEHAVIORAL_ASSERTION}}

## How to deliver
1. Implement the module + tests
2. Run the acceptance commands above
3. Write report to `work/reports/wave-{{N}}/{{TASK_FILENAME}}.report.md`
4. Use `work/REPORT_TEMPLATE.md`
5. Stop

## Constraints
- Time budget: {{N}} min
- No new dependencies without flagging
- Match existing patterns (see {{EXAMPLE_FILE}})
- Allowed tools: {{TOOLS}}
