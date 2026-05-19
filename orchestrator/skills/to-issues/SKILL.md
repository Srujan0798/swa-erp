---
name: to-issues
description: Decompose a PRD section into vertical-slice waves. Each wave ships an end-to-end demo.
---

# to-issues

## Heuristics for waves
- Vertical slices, not horizontal layers (avoid "DB-only wave" or "API-only wave")
- Each wave ends with a demo: working feature for a user
- 4–8 tasks per wave
- 1–2 weeks of calendar time per wave with parallel workers
- Dependencies expressed in `plan/EXECUTION.md` graph
- First wave = Foundation (auth, infra) — not a "feature" wave but enables them

## Output
- Updated `plan/EXECUTION.md` with the new wave nodes
- Optional preview spec for each wave (stub in `.specify/specs/wave-N/spec.md`)
