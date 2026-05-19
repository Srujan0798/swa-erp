# Scope Guard (orchestrator-side)

The orchestrator's job is to PROTECT scope. Workers will happily build whatever you brief — that's the danger.

## Defaults to enforce

1. **MVP first.** Wave-1 through wave-4 = MVP. Don't pull wave-5+ features forward.
2. **No premature multi-tenancy.** Single SWA install. Multi-tenant later (per constitution).
3. **No premature optimization.** Hit the perf budget; don't exceed it speculatively.
4. **No external integrations not in PRD.** Email/PDF/Excel only. WhatsApp/Slack/Tally are future waves.

## Red flags from worker reports
- "While I was here I also added X." → REJECT and ask: was X in the brief?
- "I refactored Y to make it cleaner." → REJECT unless Y is in the brief's modify list
- "I noticed a bug in Z and fixed it." → APPROVE only if Z is in the same module; otherwise file a new task

## When the user asks for feature creep
Use `interviewer` agent. Ask:
- Is this in the current wave's spec?
- If no: should we update spec.md or defer to a later wave?
- If yes: where does it fit? Add a new task or extend an existing one?

Never silently expand a wave.
