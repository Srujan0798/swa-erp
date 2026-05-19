# Karpathy CLAUDE.md Rules (always-on)

Per Andrej Karpathy's CLAUDE.md observations.

## 1. Think before coding
- State assumptions explicitly rather than silently guessing
- Present multiple interpretations when ambiguity exists
- Push back when warranted — if a simpler approach exists, say so
- Stop and ask when confused (use `interviewer` agent)

## 2. Simplicity first
- Build only what was requested
- No speculative features
- No abstractions for unused future needs
- No error handling for impossible scenarios
- If 200 lines could be 50, rewrite
- Senior engineer test: would they call this overcomplicated?

## 3. Surgical changes
- Touch only what the request requires
- Don't refactor unbroken code
- Don't reformat adjacent lines
- Remove only imports/variables YOUR changes orphaned
- Match existing style even if you'd prefer differently

## 4. Goal-driven execution
- Transform tasks into verifiable success criteria
- Write tests first, then make them pass
- State brief plans with step-by-step verification
- LLMs are exceptionally good at looping until they meet specific goals
