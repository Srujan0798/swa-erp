---
name: next
description: Recommend the next action. Usage /next
---

# /next

## What this does
Looks at project state and recommends the single next action.

## Decision tree
- If active wave has tasks pending dispatch → recommend /dispatch
- If reports await review → recommend /review path
- If all wave tasks merged → recommend /ship
- If wave shipped → recommend /plan for next wave per EXECUTION.md graph
- If blocked → recommend interviewer agent to ask user
