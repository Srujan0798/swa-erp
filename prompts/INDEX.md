# Prompts — SWA ERP worker prompts

> **Role:** Navigation for worker prompts actually in use. Part of the front-door set.

## Structure

```
prompts/
├── current/          # worker prompts actually in use (read these first)
│   └── WORKER_PROMPT.md   # the worker agent instruction set
├── archive/          # superseded prompt versions (never re-used)
└── INDEX.md          # this file
```

## Current prompts

### `current/WORKER_PROMPT.md`
The worker agent instruction set. Every OpenCode CLI worker reads this first, then reads one task
file from `work/wave-N/`. Defines the worker's tier, rules, and which skills they may use.

**Always read this first** before reading any task file.

## Archived prompts

Superseded prompt versions live in `prompts/archive/`. They are never re-used — if a prompt is
updated, the new version goes in `current/` and the old one is archived here with a date stamp.

## Adding a new prompt

1. Write the prompt in `prompts/current/`
2. Add a row to this INDEX.md
3. If replacing an existing prompt, move the old one to `prompts/archive/` with a date stamp
4. Don't delete — archive

## Prompt template

Worker task briefs use `work/TASK_TEMPLATE.md`. That template is not a prompt itself — it's the
structure every task file follows.
