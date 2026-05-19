# Context Budget Discipline

Per Boris Cherny's #1 insight: context fills fast; performance degrades.

## Targets
- Always-loaded kernel (CLAUDE.md + KIMI.md + HANDOFF.md + HIERARCHY.md) → keep under 8K tokens combined
- Per-task working context → under 30K tokens
- Total session before /clear → under 100K tokens

## Techniques
1. **Lazy-load core/.** Don't read all of `core/` at startup. Only the files relevant to current task.
2. **@-reference files instead of pasting.** `@plan/PRD.md` lets the agent fetch on demand.
3. **Caveman skill for compression.** When summarizing, run `caveman` skill for ~75% reduction.
4. **Sub-agents for investigation.** Spawn `codebase-explorer` in separate context; receive only the summary.
5. **/clear between waves.** Don't carry wave-1 conversation into wave-2.

## When context is getting full
- Run `/handoff` to write a compact summary to `HANDOFF.md`
- Run `/clear` and start fresh
- Reload only the kernel + relevant spec + recent reports

## Anti-patterns
- Reading every file in src/ at startup
- Quoting whole files when one paragraph would do
- Keeping completed wave conversations active
- Not using sub-agents for exploration
