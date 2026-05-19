---
name: reflect
description: Meta-review of how the orchestration is going. Usage /reflect
---

# /reflect

## What this does
Step back from execution and ask: is the orchestrator doing its job well?

## Questions to answer
- Are task briefs producing clean reports first time? Or lots of REVISE cycles?
- Is the wave decomposition right-sized? Tasks too big? Too small?
- Are workers using the listed skills? Are some skills wrong/missing?
- Are acceptance contracts catching real issues? Or rubber-stamping?
- Is the context budget being respected? Or bloating?
- Are decisions being captured as ADRs?
- What patterns are we doing well? What's not working?

## Output
Reflection note → `docs/decisions/0NNN-retrospective-wave-N.md` with:
- What worked
- What didn't
- What changes for the next wave
