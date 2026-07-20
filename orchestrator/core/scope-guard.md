# Scope Guard (orchestrator-side)

The orchestrator's job is to PROTECT scope. Workers will happily build whatever you brief —
that's the danger.

**Updated 2026-07-20** — rule 1 below used to say "wave-1 through wave-4 = MVP." That was wrong:
waves 1-8 shipped a generic CRM, but the client's actual requested MVP (Inquiry→Client→Service
Agreement→Token→Document Reference chain, per Meeting 1/2) wasn't built until wave-9. See
`docs/decisions/0002-core-id-chain-gap.md` for the full story and `docs/SCOPE_GUARD.md` for the
current wave-by-wave scope list — read that file for the actual boundary, this file is process
rules only, not a wave list (don't duplicate the wave table here; it will go stale again).

## Defaults to enforce

1. **MVP first, and know what MVP actually means here.** The real MVP is the interconnected
   chain (Inquiry → Client → Agreement → Token → Document Reference → Time Log), not just "early
   wave numbers." A high wave number does not automatically mean lower priority — wave-9-13
   closed the actual client-requested gap and should be treated as core, not an extension. Check
   `docs/SCOPE_GUARD.md` for what's shipped vs. in-progress before deciding what counts as
   "pulling forward."
2. **No premature multi-tenancy.** Single SWA install. Multi-tenant later (per constitution).
3. **No premature optimization.** Hit the perf budget; don't exceed it speculatively.
4. **No external integrations not in PRD.** Email/PDF/Excel only. WhatsApp/Slack/Tally are
   future waves. rfq2boq is a genuinely separate product — never call it directly, even
   indirectly via a shared dependency; this rule exists because of a real confusion the client
   caught and corrected in Meeting 2 (see `resources/MEETINGS_MASTER.md` §Meeting 2 point 9).
5. **Don't silently resolve open business/infra questions with a guess that requires a
   rewrite.** Where `docs/decisions/0002-core-id-chain-gap.md` or `docs/IT_BRIEF.md` list
   something as still-open (e.g. the 4th Service Agreement type), the existing code already
   defaults to a free-text/config-shaped field specifically so the real answer can land later
   without a migration rewrite. Don't tighten those fields into a hardcoded enum/constraint
   before the client actually answers, even if a worker report proposes it "for cleanliness."

## Red flags from worker reports
- "While I was here I also added X." → REJECT and ask: was X in the brief?
- "I refactored Y to make it cleaner." → REJECT unless Y is in the brief's modify list
- "I noticed a bug in Z and fixed it." → APPROVE only if Z is in the same module; otherwise file a new task
- "I made this field a strict enum instead of free text." → REJECT if the field corresponds to
  an item still listed as open in `docs/decisions/0002-core-id-chain-gap.md` — that looseness is
  intentional, not sloppiness (see rule 5 above)

## When the user asks for feature creep
Use `interviewer` agent. Ask:
- Is this in `docs/SCOPE_GUARD.md`'s current wave list?
- If no: should we update `docs/SCOPE_GUARD.md` or defer to a later wave?
- If yes: where does it fit? Add a new task or extend an existing one?

Never silently expand a wave.
