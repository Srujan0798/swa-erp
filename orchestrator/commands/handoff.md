---
name: handoff
description: Compact context into HANDOFF.md for the next session. Usage /handoff
---

# /handoff

## What this does
Writes a compact summary into `HANDOFF.md` so the next Claude/Kimi session can resume in < 5 min.

## Steps
1. Read current conversation history
2. Identify decisions made, files touched, open questions
3. Update HANDOFF.md "Current state" section
4. Update "Open decisions" list
5. Bump "Last dispatched tasks" and "Last completed reports"
6. Suggest /clear to start fresh

## Anti-bloat
Use `skills/caveman/` for 75% token reduction. HANDOFF.md should stay under 200 lines.
