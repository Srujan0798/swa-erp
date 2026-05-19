# Sub-agent Registry

Dispatch table: intent → agent. Orchestrator spawns these via the Agent tool.

| Intent | Agent | Notes |
|---|---|---|
| "explore the codebase before deciding" | `codebase-explorer` | read-only; separate context; returns summary |
| "review this worker output independently" | `verifier` | unbiased review of acceptance contracts |
| "ask the user a clarifying question" | `interviewer` | uses AskUserQuestion pattern |
| "write a great task brief" | `brief-writer` | specializes in self-contained worker briefs |
| "audit security of recent changes" | `security-reviewer` | OWASP, secrets, auth flows |
| "research a library or pattern" | `deep-research` | web + docs + summary |

## When NOT to spawn an agent
- Trivial reads (just Read tool)
- Single-purpose grep (just Grep)
- Quick formatting check (just Bash)

Agents cost context and time. Use them when independence or focus matters.
