# Anthropic's 5 Canonical Patterns (when to pick which)

Per Anthropic "Building Effective Agents."

## 1. Prompt Chaining
Sequential LLM calls, each processing the previous output.
**Use for:** linear pipelines where each step needs the prior result.
**In this project:** rare. Most work is orchestrator → worker, not chain-of-LLM.

## 2. Routing
Classify input, dispatch to specialized prompt/path.
**Use for:** task types vary (backend vs frontend vs DB migration).
**In this project:** `agents/REGISTRY.md` routes by intent — backend tasks → Python skill bundle; frontend → TS skill bundle.

## 3. Parallelization
Run subtasks simultaneously or repeat for diverse outputs.
**Use for:** independent tasks within a wave; multiple workers.
**In this project:** DEFAULT. Most wave tasks dispatch in parallel to OpenCode windows.

## 4. Orchestrator-Workers
Central LLM breaks tasks, delegates to workers.
**Use for:** unpredictable problem spaces, multi-file changes.
**In this project:** ALWAYS. This is the core pattern. Orchestrator = Claude/Kimi; workers = OpenCode CLI.

## 5. Evaluator-Optimizer
One LLM generates, another evaluates iteratively.
**Use for:** quality matters more than speed; clear eval criteria.
**In this project:** `verifier` sub-agent reviews worker output; revisions iterate until acceptance contracts pass.

## When NOT to use multiple agents
Anthropic's warning: "Start with simple prompts, add agents only when simpler fails."
- Trivial bug fixes → don't /plan or /dispatch; just edit
- Single-file refactors → one worker session, no orchestration
- Clear, small change → ask the human
