# Conflict Resolution

When sources of truth disagree, follow this precedence.

## Hierarchy of authority (highest to lowest)

1. **`.specify/memory/constitution.md`** — non-negotiable principles
2. **`docs/decisions/` ADRs** (newest first) — explicit decisions
3. **`plan/PRD.md`** — current product spec
4. **`plan/ARCHITECTURE.md`** — current architecture
5. **`.specify/specs/wave-N/spec.md`** — current wave spec
6. **`CLAUDE.md` / `KIMI.md`** — operating kernel
7. **`orchestrator/core/*.md`** — methodology
8. **`docs/conventions.md`** — code/data conventions
9. **Source code comments** — implementation notes
10. **Worker reports** — historical decisions (lowest authority)

## When two ADRs conflict
- Newer ADR wins
- Older ADR's status changes from "Accepted" to "Superseded by ADR-NNNN"
- Move the superseded ADR to `docs/historical/` ONLY if it's also been REVOKED (different from superseded — almost never)

## When the constitution and an ADR conflict
- Constitution wins
- The ADR must be revised or rejected
- If the team really wants the ADR, amend the constitution first (a separate ADR)

## When code and docs conflict
- The CODE is the current state (it's running)
- The DOCS are the intent
- A drift means someone forgot to update docs OR drift was unauthorized
- Either way: the docs must be updated, OR the code must be reverted to match docs

## When workers disagree across reports
- Latest merged work wins
- If two reports overlap in scope, the orchestrator must reject the later one or revise it

## When the orchestrator has no clear answer
- Spawn `interviewer` agent
- Ask the user
- Document the answer as an ADR

## When in doubt
- Read this file
- Ask
