---
name: zoom-out
description: When stuck in details, request broader context. Re-read PRD, ARCHITECTURE, EXECUTION before deciding.
version: 1.0.0
allowed-tools:
  - read_file
  - search_files
  - terminal
invocation: agent
subagent: true
---

# zoom-out

## When to use
- You've been debating a small detail for > 10 minutes
- A worker keeps producing REVISE-worthy reports on the same task
- You're not sure if a feature is in scope
- The wave is taking longer than planned

## Steps
1. Stop. /clear if needed.
2. Re-read `plan/PRD.md` (objective, scope, non-goals)
3. Re-read `plan/ARCHITECTURE.md` (where does this fit?)
4. Re-read `plan/EXECUTION.md` (what wave are we in? what's the goal?)
5. Re-read current wave's `spec.md` + `plan.md`
6. Ask: is the current debate even relevant to shipping this wave?

## Output
A 1-paragraph "here's where we are and what matters next" note, then resume work.
