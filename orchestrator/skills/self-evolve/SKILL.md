---
name: self-evolve
description: After each wave, capture lessons that should change the orchestrator's behavior. Hermes-style learning loop.
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

# self-evolve

## When to use
- After /ship — what did this wave teach us about how to work?
- After a major REVISE cycle — what made the task brief unclear?
- After a missed performance budget — what should we measure earlier next wave?

## Steps
1. Reflect on what happened during the wave
2. Identify 1–3 lessons that are NOT one-off
3. Encode each lesson into a permanent place:
   - Process change → update `core/<file>.md`
   - New skill needed → write `orchestrator/skills/<new>/SKILL.md`
   - Worker brief format gap → update `work/TASK_TEMPLATE.md`
   - Constitution gap → propose constitution amendment via ADR
4. Write a retrospective ADR: `docs/decisions/0NNN-retro-wave-N.md`

## What NOT to encode
- One-off bugs (file as a regular ADR if architecturally significant)
- Personal preferences (this is shared infrastructure)
- Premature optimizations
