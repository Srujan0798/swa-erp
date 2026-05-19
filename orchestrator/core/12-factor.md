# 12-Factor Agents Principles (for this orchestrator)

Per humanlayer/12-factor-agents. Each factor applies to how the orchestrator and workers behave.

1. **Natural Language to Tool Calls** — orchestrator outputs structured task files, not free prose
2. **Own Your Prompts** — `commands/`, `skills/`, and templates are explicit; no black-box framework
3. **Own Your Context Window** — `caveman` skill + `/handoff` compact; `core/` files are lazy-loaded
4. **Tools Are Structured Outputs** — task files and reports follow strict schemas
5. **Unify Execution State and Business State** — `plan/EXECUTION.md` is the single source of project state
6. **Launch/Pause/Resume** — switch Claude ↔ Kimi anytime; auto-memory persists
7. **Contact Humans with Tool Calls** — `interviewer` agent for questions; never just "I'm stuck"
8. **Own Your Control Flow** — recipes in `recipes/` are explicit; no magic loops
9. **Compact Errors into Context** — error summarization skill keeps reports tight
10. **Small, Focused Agents** — workers do ONE task; sub-agents are narrow (verifier, explorer, interviewer)
11. **Trigger from Anywhere** — orchestrator works in Claude Code, Kimi, web; workers via OpenCode CLI
12. **Stateless Reducer** — worker = `(task brief, code state) → (new code state, report)`. No hidden state.
