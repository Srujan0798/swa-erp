---
name: status
description: Print current project state. Usage /status
---

# /status

## What this does
Compact summary of where the project is.

## Outputs
- Active wave (from HANDOFF.md)
- Tasks: in-progress / pending / merged / total (from EXECUTION.md)
- Open reports awaiting review (count files in work/reports/wave-N/)
- Recent merges (last 5 entries in CHANGELOG.md [Unreleased])
- Latest ADRs (3 newest in docs/decisions/)
- Test health (CI status if available)
- Risk register: any T2/T3 items pending?
