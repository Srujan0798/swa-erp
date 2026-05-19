# OS-Setup — Universal Agentic Project Kickstart

> **What this is.** A single self-sufficient markdown file that turns ANY project brief into a complete, dual-tier agentic project structure. Paste this file + your project details into Claude or Kimi, and you get the entire repo pre-filled, ready to start shipping with OpenCode CLI workers in parallel windows.
>
> **Built from.** Synthesis of 4 deep methodology iterations + 2 dedicated specifications + live research across: Anthropic Skills (agentskills.io), Boris Cherny's Claude Code best practices, Karpathy CLAUDE.md, 12-Factor Agents, Anthropic's 5 canonical patterns, SuperClaude (30 commands), BMAD Method, kmshihab Claude OS pattern, Spec-Kit, Kiro, MCP, A2A, mattpocock skills, OpenClaw, Hermes, Letta, and 40+ tools on the agentskills.io standard.
>
> **Plus the empirical lessons from a real Project 1 (rfq2boq, May 2026):** wave-based execution, root-level CLAUDE/HANDOFF/HIERARCHY docs, evolution discipline via attic/, deliverables-rich output (paper + patent + report + slides + UI + API + CLI), expanded test taxonomy, plural data folders, model versioning.
>
> **Version.** v1.1 — May 2026 (Project 1 lessons absorbed)

---

## 0. How to use this file

1. **Open Claude Code or Kimi.** Either works — they're interchangeable.
2. **Paste this file** at the top of your conversation.
3. **Paste the project brief** (PDF text, one-paragraph scope, or just a goal).
4. **Say**: *"Use OS-Setup to generate the complete project structure for this brief."*
5. The orchestrator creates the entire `<project-name>/` folder with everything described below, **filled in for your specific project**.
6. You open OpenCode CLI windows in parallel, paste task files from `work/`, and start shipping.

---

## 1. The Two-Tier Methodology

```
┌──────────────────────────────────────────────────────────────────┐
│  TIER 1 — ORCHESTRATOR  (Claude OR Kimi, interchangeable)        │
│                                                                  │
│  • Reads project state, specs, reports                           │
│  • Writes task files into work/                                  │
│  • Reviews worker reports                                        │
│  • Merges output, updates state                                  │
│  • One process at a time — single source of truth                │
│  • If Claude is down, switch to Kimi. Same files, same workflow. │
└────────────────────────────┬─────────────────────────────────────┘
                             │ task file (self-contained brief)
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  TIER 2 — WORKERS  (OpenCode CLI in multiple parallel windows)   │
│                                                                  │
│  • Receive ONE self-contained task file                          │
│  • Use their OWN skills (skills.sh / Claude built-in /           │
│    agentskills.io online — NOT this project's orchestrator skills)│
│  • Execute, write code/data/models to repo                       │
│  • Write standardized report to work/reports/                    │
│  • Stateless across tasks; parallel by default                   │
└──────────────────────────────────────────────────────────────────┘
```

**Core rule.** The orchestrator never executes implementation. Workers never plan. The handoff is `work/<wave>/<task>.md` (orchestrator → worker) and `work/reports/<wave>/<task>.report.md` (worker → orchestrator).

**Terminology.** Units of work are called **waves** (preferred) or **slices** (synonym). A wave is a coherent, end-to-end deliverable shipped before the next wave begins. A wave typically breaks into 4–8 tasks dispatched to parallel workers.

---

## 2. The Complete File Structure

```
<project-name>/
├── README.md                          # entry point + how to run
├── CLAUDE.md                          # ★ ROOT — auto-loaded by Claude Code (Boris pattern)
├── KIMI.md                            # ★ ROOT — IDENTICAL to CLAUDE.md (interchangeable)
├── HANDOFF.md                         # ★ ROOT — switching sessions/orchestrators
├── HIERARCHY.md                       # ★ ROOT — repo map + ownership
├── HOW_TO_RUN.md                      # the dual-tier workflow in plain language
├── CHANGELOG.md                       # version history
├── CONTRIBUTING.md                    # how to contribute
├── OS_SETUP.md                        # ← this file, kept for reference + regeneration
│
├── .claude/                           # ★ MINIMAL — Boris's rule, don't over-build
│   └── settings.local.json            # permissions, MCP, auto-mode
│
├── orchestrator/                      # TIER 1 apparatus (deep, lazy-loaded)
│   ├── ROLE.md                        # how the orchestrator thinks + works
│   │
│   ├── core/                          # lazy-loaded governance
│   │   ├── identity.md                # who the orchestrator is on this project
│   │   ├── dispatch-protocol.md       # how to write task files
│   │   ├── review-protocol.md         # how to review worker reports
│   │   ├── 12-factor.md               # 12-factor agent principles
│   │   ├── 5-patterns.md              # Anthropic's 5 canonical patterns
│   │   ├── karpathy-rules.md          # think → simplify → surgical → goal-driven
│   │   ├── governance.md              # T0/T1/T2/T3 risk tiering
│   │   ├── context-budget.md          # token discipline
│   │   └── scope-guard.md             # what's IN scope vs OUT
│   │
│   ├── commands/                      # slash commands — START SMALL, GROW AS NEEDED
│   │                                  # Required minimum (10):
│   │   ├── plan.md                    # /plan — wave → spec/plan/tasks
│   │   ├── dispatch.md                # /dispatch — write task files
│   │   ├── review.md                  # /review — check a report
│   │   ├── merge.md                   # /merge — integrate output
│   │   ├── ship.md                    # /ship — close a wave
│   │   ├── status.md                  # /status — current state
│   │   ├── next.md                    # /next — what to do next
│   │   ├── handoff.md                 # /handoff — compact context
│   │   ├── audit.md                   # /audit — deep check
│   │   └── reflect.md                 # /reflect — meta-review
│   │                                  # Add domain-specific later (don't pre-build 30):
│   │                                  # /operator /optimizer /find-skills /fact-checker
│   │                                  # /prompt-master /decision-toolkit /mcp-builder
│   │                                  # /process-interviewer /second-brain /routines
│   │                                  # /party-mode /humanizer /front-end-slides
│   │                                  # /os-setup /os-operator /os-optimiser
│   │                                  # /team-os /business-os /os-mcp
│   │
│   ├── skills/                        # ORCHESTRATOR-only skills (planning, dispatching)
│   │                                  # Each follows agentskills.io spec:
│   │   ├── write-task-file/SKILL.md   # ★ key skill — self-contained briefs
│   │   ├── plan-wave/SKILL.md         # PRD → wave → tasks
│   │   ├── review-report/SKILL.md     # verify report vs spec
│   │   ├── merge-work/SKILL.md        # safe integration
│   │   ├── triage/SKILL.md            # categorize incoming
│   │   ├── to-prd/SKILL.md            # discussion → PRD
│   │   ├── to-issues/SKILL.md         # PRD → waves
│   │   ├── status-report/SKILL.md     # weekly status format
│   │   ├── diagnose/SKILL.md          # systematic debug guidance
│   │   ├── verify-work/SKILL.md       # Boris's #1 rule
│   │   ├── zoom-out/SKILL.md          # broader context
│   │   └── caveman/SKILL.md           # 75% token reduction
│   │
│   ├── agents/                        # sub-agents the orchestrator spawns
│   │   ├── REGISTRY.md                # intent → agent dispatch table
│   │   ├── codebase-explorer.md       # read-only investigation (Boris)
│   │   ├── verifier.md                # evaluator-optimizer reviewer
│   │   ├── interviewer.md             # asks user before major decisions
│   │   ├── brief-writer.md            # specializes in task file production
│   │   └── (add per-domain: pm, architect, security-reviewer, deep-research)
│   │
│   ├── hooks/                         # deterministic auto-actions
│   │   ├── session-start.sh           # load project state
│   │   ├── pre-tool-use.sh            # gate destructive ops (T0-T3)
│   │   ├── mcp-security-gate.sh       # whitelist MCP calls
│   │   ├── block-secrets.sh           # prevent secret commits
│   │   ├── block-destructive.sh       # rm -rf, force-push, hard-reset
│   │   ├── post-merge-format.sh       # auto-format after merge
│   │   └── stop.sh                    # save state on exit
│   │
│   ├── recipes/                       # parameterized YAML workflows
│   │   ├── new-wave.yaml              # plan → dispatch → review → merge → ship
│   │   ├── bugfix.yaml                # reproduce → fix → verify
│   │   └── (add per project)
│   │
│   ├── rules/                         # path-scoped rules (loaded only for matching files)
│   │   ├── python.md
│   │   ├── typescript.md
│   │   ├── security.md
│   │   └── docs.md
│   │
│   ├── memory/                        # auto-memory + MEMORY.md index
│   │   └── MEMORY.md
│   │
│   └── scripts/                       # validate.sh, context-budget-report.sh
│
├── work/                              # ★ THE BRIDGE — orchestrator writes, workers read
│   ├── TASK_TEMPLATE.md               # format every task file follows
│   ├── REPORT_TEMPLATE.md             # format every worker report follows
│   ├── WORKER_PROMPT.md               # universal prefix for any worker
│   │
│   ├── wave-1/
│   │   ├── 01-<task-name>.md
│   │   ├── 02-<task-name>.md
│   │   └── ...
│   ├── wave-2/
│   ├── wave-3/
│   │
│   └── reports/                       # worker reports back here
│       ├── wave-1/
│       │   └── 01-<task-name>.report.md
│       └── wave-2/
│
├── .specify/                          # Spec-driven (Spec-Kit + Kiro)
│   ├── memory/
│   │   └── constitution.md            # project principles + non-negotiables
│   ├── steering.md                    # custom AI rules
│   └── specs/
│       └── wave-N/
│           ├── spec.md                # WHAT (functional, user stories)
│           ├── plan.md                # HOW (tech stack, decisions)
│           ├── tasks.md               # ordered task breakdown
│           └── contracts/             # executable acceptance (pytest/Gherkin/OpenAPI)
│
├── plan/                              # 3 LIVING strategic docs (high-level only)
│   ├── PRD.md                         # objective / user / scope / MVP / non-goals / success
│   ├── ARCHITECTURE.md                # modules / data flow / state / failure points
│   └── EXECUTION.md                   # wave graph / dependency order / current status
│
├── docs/                              # ★ EXPANDED (Project 1 lessons)
│   ├── waves/                         # per-wave briefs (small, focused)
│   ├── decisions/                     # ADRs — one file per major decision
│   ├── historical/                    # superseded docs (don't delete — archive)
│   ├── runbook.md                     # operational guide
│   ├── conventions.md                 # code/data/naming conventions
│   ├── conflict_resolution.md         # when sources disagree
│   ├── deployment.md
│   ├── SCOPE_GUARD.md                 # IN vs OUT of scope
│   └── api.md                         # API contracts
│
├── prompts/                           # ★ EVOLVING prompts (Project 1 wave pattern)
│   ├── current/                       # actively used worker prompts
│   ├── archive/                       # superseded prompts (kept for reference)
│   ├── wave-2/                        # wave-specific overrides
│   └── wave-3/
│
├── attic/                             # ★ ARCHIVE — old/superseded work, never deleted
│
├── deliverables/                      # ★ MULTI-OUTPUT (Project 1 pattern)
│   ├── paper/                         # academic paper draft + figures
│   ├── patent/                        # patent draft + claims
│   ├── report/                        # technical report
│   ├── slides/                        # presentation deck
│   └── demo/                          # demo videos, screenshots
│
├── src/                               # actual code (workers write here)
│   └── (per-domain modules — orchestrator decides layout)
│
├── tests/                             # ★ EXPANDED TAXONOMY (Project 1)
│   ├── unit/
│   ├── integration/
│   ├── e2e/                           # end-to-end scenarios
│   ├── golden/                        # known-good fixtures
│   ├── fuzz/                          # property-based + fuzzing
│   ├── performance/                   # perf budgets
│   └── security/                      # security tests
│
├── data/                              # ★ PLURAL (Project 1 pattern, if data-heavy)
│   ├── raw/                           # untouched source
│   ├── samples/                       # small demo set
│   ├── synthetic/                     # generated data
│   ├── annotations/                   # labeled data
│   ├── gold/                          # ground truth
│   ├── ontology/                      # domain vocab/schema
│   └── (per-domain folders: rates/, real_<domain>/, etc.)
│
├── models/                            # ★ VERSIONED (if ML project)
│   ├── <model-name>-v1/
│   ├── <model-name>-v2/
│   └── <model-name>-final/
│
├── schema/                            # JSON Schema / Pydantic definitions
├── config/                            # runtime config
├── scripts/                           # automation utilities
├── ui/                                # if project has a UI
├── deployment/                        # IaC, k8s manifests
├── resources/                         # reference materials (knowledge_base, transcripts)
│
├── logs/                              # runtime logs
├── results/                           # experiment outputs
│
├── mcp.json                           # MCP server declarations
├── Makefile                           # make demo/test/lint/format/ship/dispatch/review
├── Dockerfile
├── docker-compose.yml                 # sandbox for worker execution
├── pyproject.toml                     # modern Python packaging (or package.json for Node)
├── requirements.txt
├── .pre-commit-config.yaml            # pre-commit hooks
├── .env.example                       # template; never commit .env
├── .gitignore
├── .dockerignore
└── .github/
    └── workflows/
        ├── ci.yml                     # acceptance + lint + test
        ├── test.yml                   # comprehensive test matrix
        ├── security.yml               # security scanning
        ├── perf_regression.yml        # performance budgets
        └── train_on_data.yml          # if ML — model training pipeline
```

---

## 3. The Adapt-to-Any-Project Mechanism

When you paste this file + your project brief, the orchestrator does the following:

### Step 1 — Read the brief, fill in variables

| Variable | Source | Example |
|---|---|---|
| `{{PROJECT_NAME}}` | Brief title / domain | `rfq-to-boq`, `email-classifier` |
| `{{PROJECT_GOAL}}` | One-line from brief | "Convert RFQ PDFs to structured BOQ" |
| `{{DOMAIN}}` | Inferred from brief | NLP / web / data pipeline / ML research |
| `{{TECH_STACK}}` | Inferred + asked if ambiguous | Python/FastAPI/Postgres or Node/React/Postgres |
| `{{MVP_DEFINITION}}` | First wave scope | "Ingest one PDF, output one BOQ row" |
| `{{WAVES}}` | Decomposition | 4–8 waves, ordered by dependency |
| `{{ENTITIES}}` | Domain model | Material / Quantity / Standard / etc. |
| `{{SUCCESS_METRICS}}` | Acceptance | F1 ≥ 0.85, end-to-end < 60s, etc. |
| `{{RISKS}}` | Risk register | OCR noise, scope omission, etc. |
| `{{MCP_SERVERS}}` | Domain-relevant | web app: playwright; data: serena; research: tavily, context7 |
| `{{HAS_MODELS}}` | ML project? | If yes, create `models/` with versioning |
| `{{HAS_UI}}` | User-facing? | If yes, create `ui/` with assets |
| `{{HAS_DELIVERABLES}}` | Academic/research output? | Create relevant `deliverables/` subfolders |
| `{{HAS_DATA}}` | Data-heavy? | If yes, expanded `data/` taxonomy |

### Step 2 — Generate filled files (in this order)

1. Create folder structure from §2
2. Write `plan/PRD.md` (objective / user / scope / MVP / non-goals / success metrics)
3. Write `plan/ARCHITECTURE.md` (modules + flows + failure points)
4. Write `plan/EXECUTION.md` (wave graph with deps + order)
5. Write `.specify/memory/constitution.md` with project principles
6. For each wave N: write `.specify/specs/wave-N/{spec,plan,tasks,contracts}`
7. Write root `CLAUDE.md` (and copy to `KIMI.md`) — short, project-tuned (Boris rule)
8. Write root `HANDOFF.md` — how to switch orchestrator sessions
9. Write root `HIERARCHY.md` — repo map + ownership of each folder
10. Customize `orchestrator/skills/`, `agents/`, `rules/`, `recipes/` for the domain
11. Generate first wave's task files in `work/wave-1/*.md`
12. Write `README.md`, `HOW_TO_RUN.md`, `CHANGELOG.md`, `CONTRIBUTING.md`
13. Write `Makefile`, `requirements.txt` (or `package.json`), `pyproject.toml`, `mcp.json`
14. Write `.github/workflows/{ci,test,security,perf_regression}.yml` (+ `train_on_data.yml` if ML)
15. Write `.pre-commit-config.yaml`, `Dockerfile`, `docker-compose.yml`, `.env.example`
16. Print: "Setup complete. Open OpenCode CLI windows and paste work/wave-1/01-*.md to start."

### Step 3 — Ongoing customization

- Each new wave: `/plan wave-N` regenerates specs
- Each new task: `/dispatch` produces updated briefs
- New decisions: written as ADRs in `docs/decisions/`
- Old patterns: moved to `attic/`, `docs/historical/`, or `prompts/archive/` — **never deleted**
- Drift: detected via `orchestrator/hooks/post-merge-format.sh` + `scripts/validate.sh`

---

## 4. Templates

### 4.1 — `CLAUDE.md` (ROOT, short, Boris-compliant)

```markdown
# {{PROJECT_NAME}} — Orchestrator Kernel

You are the project orchestrator. Full role in `orchestrator/ROLE.md`.

## Project goal
{{PROJECT_GOAL}}

## Tech stack
{{TECH_STACK}}

## Code style
- {{STYLE_RULE_1}}
- {{STYLE_RULE_2}}

## Workflow rules (Karpathy + 12-Factor + Boris)
- Think before coding: state assumptions, ask if ambiguous
- Simplicity first: if 200 lines could be 50, rewrite
- Surgical changes: touch only what the request requires
- Verify your work: tests / screenshots / expected outputs are the contract
- /clear between unrelated tasks
- Plan → code → verify; never skip plan for changes touching multiple files

## You ORCHESTRATE — you don't execute
- Implementation goes to OpenCode CLI workers
- You write task files into `work/<wave>/`
- You review reports in `work/reports/<wave>/`
- You merge approved output

## Project-specific commands
- `make demo` — end-to-end demo
- `make test-wave wave=N` — test one wave
- `make dispatch wave=N` — regenerate task files
- `make ship wave=N` — close wave pipeline

## Where things live
- Strategy: `plan/{PRD,ARCHITECTURE,EXECUTION}.md`
- Specs: `.specify/specs/wave-N/`
- Apparatus: `orchestrator/{commands,skills,agents,hooks,recipes,rules}/`
- Bridge: `work/wave-N/` (briefs) → `work/reports/wave-N/` (reports)
- Outputs: `src/`, `tests/`, `models/`, `deliverables/`
- Archives: `attic/`, `docs/historical/`, `prompts/archive/`

## Patterns (Anthropic's 5 canonical)
Default: orchestrator-workers (dispatch to OpenCode).
Investigation: spawn sub-agent (codebase-explorer).
Long reviews: evaluator-optimizer (verifier agent).

## Verification
Every wave has acceptance criteria in `.specify/specs/wave-N/contracts/`. These are RUNNABLE.
Never approve a worker report without running its acceptance commands.

## Hand-off
If switching sessions or orchestrator (Claude ↔ Kimi), read `HANDOFF.md` first.
```

### 4.2 — `HANDOFF.md` (ROOT, for session/orchestrator switching)

```markdown
# Handoff Protocol

## Why this file exists
Switching orchestrators (Claude ↔ Kimi) or starting a fresh session shouldn't require re-explaining the project. This file lets the new session catch up in < 5 minutes.

## Current state (kept up-to-date)
- Active wave: wave-N
- Status: see `plan/EXECUTION.md`
- Last dispatched tasks: list in `work/wave-N/`
- Last completed reports: list in `work/reports/wave-N/`
- Open decisions: see `docs/decisions/` (most recent files)

## Where to start a new session
1. Read this file
2. Read `CLAUDE.md` (kernel)
3. Read `plan/EXECUTION.md` (current wave status)
4. Read most recent ADR in `docs/decisions/`
5. Run `/status` to see live state

## When you've just merged a wave
Update this file: bump active wave, summarize what shipped, note open issues.

## When switching Claude → Kimi (or vice versa)
- No file changes needed
- Both read root CLAUDE.md (Kimi treats KIMI.md as alias)
- Same workflow, same commands

## When onboarding a worker (rare — workers should be stateless)
Workers DON'T read this file. Their task brief in `work/<wave>/` is self-contained.
```

### 4.3 — `HIERARCHY.md` (ROOT, repo map + ownership)

```markdown
# Repository Hierarchy

## Top-level map
| Path | Owner | Purpose |
|---|---|---|
| `CLAUDE.md`, `KIMI.md` | orchestrator | always-loaded kernel |
| `HANDOFF.md`, `HIERARCHY.md` | orchestrator | session continuity |
| `plan/` | orchestrator | strategy (3 living docs) |
| `.specify/` | orchestrator | spec-driven contracts |
| `orchestrator/` | orchestrator | commands, skills, agents, hooks |
| `work/` | orchestrator (write) / workers (read) | task bridge |
| `work/reports/` | workers (write) / orchestrator (read) | report bridge |
| `src/` | workers | production code |
| `tests/` | workers | test code |
| `models/` | workers + CI | trained model artifacts |
| `data/` | workers + scripts | datasets |
| `deliverables/` | orchestrator + workers | paper/patent/report/slides |
| `docs/` | orchestrator | reference + decisions + runbook |
| `prompts/` | orchestrator | evolving worker prompt history |
| `attic/` | nobody (frozen) | superseded work |
| `scripts/`, `config/`, `schema/` | workers + orchestrator | utilities |
| `.github/workflows/` | CI | automated checks |

## Wave numbering
Waves are sequential: wave-1, wave-2, ... Don't skip numbers. Cancelled waves get archived in `attic/cancelled-wave-N/`.

## Naming conventions
- Folders: kebab-case (e.g., `wave-1/`, `data-ingest/`)
- Files: snake_case for code, kebab-case for markdown
- Skills, commands, agents: kebab-case matching the directory

## What goes in attic/
- Old plans superseded by new architecture decisions
- Failed experiments (kept for "we tried this and it didn't work because...")
- Prompt versions from earlier waves
- Anything that's no longer in the live flow but worth referencing
```

### 4.4 — `orchestrator/ROLE.md`

```markdown
# Orchestrator Role

## Identity
You are the project orchestrator for {{PROJECT_NAME}}. You don't write production code yourself. You plan, dispatch, review, and merge.

## What you do
1. Read project state: `plan/`, `docs/`, `work/reports/`, `src/`
2. Decide next wave or task
3. Write self-contained task files into `work/<wave>/` — workers have ZERO project context, so briefs must be complete
4. Review worker reports against acceptance criteria — RUN the commands, don't just read prose
5. Merge approved output via `/merge`
6. Update `plan/EXECUTION.md` status
7. Archive superseded work to `attic/` — never delete

## What you don't do
- Don't write feature code yourself (workers handle this)
- Don't pre-emptively read every file in `src/` (use `agents/codebase-explorer.md` for investigation)
- Don't approve reports without running acceptance commands
- Don't delete old work — move to `attic/`

## How you write task files
See `core/dispatch-protocol.md`. Briefs MUST be self-contained — workers have zero project memory.

## How you review reports
See `core/review-protocol.md`. Run acceptance commands; check decisions; merge or revise.

## Tools you use
- Slash commands in `commands/`
- Skills in `skills/`
- Sub-agents in `agents/`
- MCP servers from `../mcp.json`
- Auto-memory in `memory/MEMORY.md`
```

### 4.5 — `work/TASK_TEMPLATE.md`

```markdown
# Task — {{TASK_NAME}}

## What to do
{{ONE_PARAGRAPH_GOAL}}

Reference spec: `.specify/specs/wave-{{N}}/spec.md` section {{SECTION}}.

## Files to create / modify
- CREATE: {{PATH_1}}
- CREATE: {{PATH_2}}
- MODIFY: {{PATH_3}}

## Files you must NOT touch
- {{FORBIDDEN_PATH_1}}
- {{FORBIDDEN_PATH_2}}

## Skills to use (from YOUR worker skill library)
- `{{SKILL_NAME_1}}` — install from agentskills.io if not present
- `{{SKILL_NAME_2}}`
- `tdd` — red → green → refactor
- `code-review` — self-review before declaring done

(Note: these are skills your OpenCode CLI / agent has access to.
They are NOT skills from this project's `orchestrator/skills/` folder.)

## The core problem (inline — no external context needed)
{{INLINE_PROBLEM_DESCRIPTION}}

### Inputs available (paste inline)
{{INLINE_SCHEMAS_SAMPLES_EXAMPLES}}

### Edge cases to handle
- {{EDGE_1}}
- {{EDGE_2}}

## Acceptance criteria (executable, not prose)
- [ ] `{{TEST_COMMAND_1}}` passes
- [ ] `{{LINT_COMMAND}}` clean
- [ ] {{BEHAVIORAL_ASSERTION}}

## How to deliver
1. Implement the module + tests
2. Run the acceptance commands above
3. Write report to `work/reports/wave-{{N}}/{{TASK_FILENAME}}.report.md`
4. Use `work/REPORT_TEMPLATE.md`
5. Stop

## Constraints
- Time budget: {{N}} min
- No new dependencies without flagging
- Match existing patterns (see {{EXAMPLE_FILE}})
- Allowed tools: {{TOOLS}}
```

### 4.6 — `work/REPORT_TEMPLATE.md`

```markdown
# Report — {{TASK_NAME}}

## Result
[ DONE | BLOCKED | PARTIAL | FAILED ]

## What I did
- Created {{PATH}} ({{N}} lines)
- Modified {{PATH}}

## Acceptance checks
- [x] {{CHECK_1}} — passed (evidence: ...)
- [x] {{CHECK_2}} — passed
- [ ] {{CHECK_3}} — failed (reason: ..., recommendation: ...)

## Decisions I made
- Chose {{A}} over {{B}} because {{REASON}}
- Skipped {{C}} because {{REASON}}

## Tests run
- `{{CMD}}` → {{RESULT}}

## Issues / blockers
{{NONE_OR_DETAIL}}

## Recommended next task
{{IF_APPLICABLE}}

## Time / tokens / model
{{N}} min / {{M}} tokens / {{MODEL}}
```

### 4.7 — `work/WORKER_PROMPT.md` (universal prefix)

```markdown
You are a coding worker agent. You execute ONE task per session.

## Your tier
You are Tier 2 (Worker). The orchestrator is Tier 1 (Claude or Kimi) and lives elsewhere.

## Your rules
1. The task file you're given is SELF-CONTAINED. You don't need to read anything outside it.
2. If the task file says "Files you must NOT touch," respect that absolutely.
3. Use the skills listed in the task file. They are YOUR skills (from your CLI's skill library, agentskills.io online, or built-in), not the orchestrator's.
4. Acceptance criteria are executable. Run them. Don't claim DONE without passing.
5. Write your report using the REPORT_TEMPLATE format.
6. Stop after writing the report. Do not invent additional work.

## Skills you may need (install from agentskills.io if missing)
- `tdd` — test-driven development
- `code-review` — self-review before submit
- `diagnose` — systematic debug
- Domain-specific: `pdf-processing`, `web-scraping`, `api-design`, etc.

## Now read the task file that follows this prompt and execute it.
```

### 4.8 — `Makefile`

```makefile
.PHONY: help demo test lint format ship dispatch review

help:
	@echo "Orchestrator commands:"
	@echo "  make demo               — end-to-end demo"
	@echo "  make test               — run all tests"
	@echo "  make test-wave wave=N   — test one wave"
	@echo "  make lint               — lint all code"
	@echo "  make format             — auto-format"
	@echo "  make dispatch wave=N    — regenerate task files for wave N"
	@echo "  make ship wave=N        — final integration + PR for wave N"

demo:
	@echo "Customize: run the end-to-end pipeline on a sample input"

test:
	pytest tests/ -v

test-wave:
	pytest tests/wave-$(wave)/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

dispatch:
	@echo "Open Claude Code or Kimi and run: /dispatch wave-$(wave)"

ship:
	@echo "Open Claude Code or Kimi and run: /ship wave-$(wave)"

archive:
	@echo "Move superseded work into attic/. Don't delete."
```

### 4.9 — `mcp.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "{{PROJECT_PATH}}"]
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp"],
      "env": {"TAVILY_API_KEY": "${TAVILY_API_KEY}"}
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

### 4.10 — `pyproject.toml` (for Python projects)

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{{project-name}}"
version = "0.1.0"
description = "{{PROJECT_GOAL}}"
authors = [{name = "Your Name"}]
requires-python = ">=3.11"
license = {text = "MIT"}

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.black]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --tb=short"

[tool.mypy]
python_version = "3.11"
strict = true
```

### 4.11 — `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.10
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: detect-private-key
  - repo: local
    hooks:
      - id: block-secrets
        name: Block accidental secret commits
        entry: orchestrator/hooks/block-secrets.sh
        language: script
```

### 4.12 — `.github/workflows/ci.yml`

```yaml
name: CI
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11"}
      - run: pip install ruff black mypy
      - run: ruff check src/ tests/
      - run: black --check src/ tests/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11"}
      - run: pip install -r requirements.txt
      - run: pytest tests/unit tests/integration -v

  acceptance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11"}
      - run: pip install -r requirements.txt
      - run: pytest .specify/specs/*/contracts/ -v
```

### 4.13 — Sub-agent template (`orchestrator/agents/verifier.md`)

```markdown
---
name: verifier
description: Independent review of worker output against acceptance criteria. Reads code with no bias toward what was just written.
tools: Read, Grep, Glob, Bash
model: opus
---

You are an independent code reviewer. The orchestrator dispatched a task. A worker reported DONE. Your job:

1. Read the task file in `work/<wave>/<task>.md`
2. Read the report in `work/reports/<wave>/<task>.report.md`
3. Read the code the worker wrote
4. Run every acceptance command yourself
5. Look for:
   - Code that LOOKS right but doesn't actually meet criteria
   - Hidden assumptions
   - Missing edge cases from the task brief
   - Style mismatches against `orchestrator/rules/`
6. Output: APPROVED with notes, OR REVISE with specific issues

You are NOT biased toward approving — you're the independent gate.
```

### 4.14 — `README.md` template

```markdown
# {{PROJECT_NAME}}

{{ONE_LINE_GOAL}}

## Quick start

```bash
git clone <repo>
cd {{PROJECT_NAME}}
pip install -r requirements.txt
make demo
```

## How this project is built

Two-tier agentic workflow:
- **Orchestrator** = Claude Code or Kimi (interchangeable). Plans and reviews.
- **Workers** = OpenCode CLI in parallel windows. Execute self-contained task briefs.

See `HOW_TO_RUN.md` for the workflow.

## Repository map

See `HIERARCHY.md`.

## Status

See `plan/EXECUTION.md` for wave progress.

## Deliverables

- Code: `src/`
- Tests: `tests/`
- Models: `models/` (if applicable)
- Paper: `deliverables/paper/`
- Report: `deliverables/report/`
- Slides: `deliverables/slides/`
- Patent: `deliverables/patent/` (if applicable)
```

### 4.15 — `HOW_TO_RUN.md` template

```markdown
# How to Run This Project

## Open the orchestrator
Either:
- Open Claude Code in this directory (auto-loads `CLAUDE.md`), OR
- Open Kimi in this directory (auto-loads `KIMI.md`)

Both work the same way. Pick whichever is up.

## Start work
```text
/status              → see current state
/next                → ask orchestrator what to work on next
/plan wave-N         → decompose wave N into tasks
/dispatch wave-N     → write task files into work/wave-N/
```

## Dispatch to workers
Open OpenCode CLI windows (one per task you want in parallel).
In each window:
1. Paste contents of `work/WORKER_PROMPT.md`
2. Then paste contents of one task file from `work/wave-N/`
3. Worker executes, writes code to repo, writes report to `work/reports/wave-N/`

## Review and merge
Back in the orchestrator:
```text
/review work/reports/wave-N/0X-task.report.md
/merge  work/reports/wave-N/0X-task.report.md
```

## Ship a wave
When all tasks in a wave are merged:
```text
/ship wave-N
```
Runs integration tests, opens a PR, updates `plan/EXECUTION.md`.

## Switching orchestrator
If Claude is down, open Kimi in the same directory. Read `HANDOFF.md`. Same workflow.

## Evolving the project
- New decisions → write ADR in `docs/decisions/`
- Superseded plans → move to `docs/historical/`
- Superseded prompts → move to `prompts/archive/`
- Anything no longer in flow but worth keeping → `attic/`
- **Never delete. Always archive.**
```

### 4.16 — `CHANGELOG.md` template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Initial OS-Setup-generated structure.

## [0.1.0] — {{DATE}}
### Added
- Wave-1 initial implementation
```

### 4.17 — `CONTRIBUTING.md` template

```markdown
# Contributing

## Workflow
This project uses the dual-tier agentic flow:
- Plan/review via Claude Code or Kimi (the orchestrator)
- Execute via OpenCode CLI workers (parallel windows)

## To add a feature
1. Open the orchestrator: `claude` (or Kimi equivalent)
2. Run `/next` to see what wave is active
3. Run `/plan wave-N` if starting a new wave
4. Run `/dispatch wave-N` to write task files
5. Open OpenCode CLI windows, paste task files, execute
6. Workers write reports → orchestrator reviews → /merge

## Code style
- Python: black + ruff (configured in pyproject.toml)
- Tests required for any new code
- No new dependencies without an ADR in `docs/decisions/`

## Commits
- Conventional Commits format
- Reference wave/task: `feat(wave-2): add PDF ingestion`
- Co-authored-by lines welcome but not required

## Don't do this
- Don't delete files. Archive to `attic/`.
- Don't write feature code in the orchestrator session — that's worker work.
- Don't bypass acceptance commands — they are the contract.
```

### 4.18 — `docs/SCOPE_GUARD.md` template

```markdown
# Scope Guard

What's IN scope vs OUT, written defensively to prevent scope creep.

## IN scope
- {{IN_1}}
- {{IN_2}}

## OUT of scope
- {{OUT_1}}
- {{OUT_2}}

## Out for now (maybe later)
- {{LATER_1}}
- {{LATER_2}}

## When in doubt
Ask the orchestrator to interview you. If a feature isn't in this list, it doesn't get built without updating this file first.
```

### 4.19 — `docs/conventions.md` template

```markdown
# Conventions

## Code
- {{LANGUAGE}}: see `pyproject.toml` (or `package.json`)
- Tests: pytest with `tests/{unit,integration,e2e,golden,fuzz,performance,security}/`

## Data
- Raw data: `data/raw/` (never modified)
- Processed: `data/<purpose>/`
- Annotated: `data/annotations/`
- Gold (ground truth): `data/gold/`
- Synthetic: `data/synthetic/`

## Models (if ML)
- `models/<name>-v<N>/` for each version
- `models/<name>-final/` for the shipped one
- Each contains: `config.json`, `weights.bin`, `README.md` (training notes)

## Naming
- Folders: kebab-case
- Python: snake_case
- Markdown files: kebab-case for docs, SCREAMING_CASE for top-level (README, CLAUDE, HANDOFF, HIERARCHY)
```

---

## 5. Workflow Loops

### 5.1 — The wave lifecycle

```
PRD → [orchestrator] /plan wave-N
    → .specify/specs/wave-N/{spec,plan,tasks,contracts}
    → [orchestrator] /dispatch wave-N
    → work/wave-N/01...0K-task.md (one per task)
    → [human] paste each into a separate OpenCode CLI window
    → [workers, parallel] execute, write code, write report
    → work/reports/wave-N/0X-task.report.md
    → [orchestrator] /review work/reports/wave-N/0X.report.md
    → APPROVE: /merge → integrate into src/
    → REVISE: rewrite task file → redispatch
    → REJECT: /rollback → re-plan, move bad work to attic/
    → (loop until all tasks merged)
    → [orchestrator] /ship wave-N
    → final integration test, PR opened, EXECUTION.md updated
    → CHANGELOG.md bumped
    → next wave
```

### 5.2 — Tooling per phase

| Phase | Orchestrator does | Worker does | Human does |
|---|---|---|---|
| Plan | /plan, writes specs | — | Approves plan if it looks right |
| Dispatch | /dispatch, writes briefs | — | Reviews briefs (sanity check) |
| Execute | — | Reads brief, writes code, writes report | Opens OpenCode windows, pastes briefs |
| Review | /review, runs acceptance | — | Confirms APPROVE/REVISE |
| Merge | /merge, integrates | — | — |
| Ship | /ship, final tests + PR | — | Reviews PR, hits merge |
| Archive | Move superseded → `attic/` | — | — |

---

## 6. Quality Gates

### 6.1 — Risk tiering (kmshihab pattern)

| Tier | Examples | Gate |
|---|---|---|
| T0 — Auto | Read files, run tests, lint | Execute immediately |
| T1 — Log + proceed | Write to src/, modify tests | Log the action, proceed |
| T2 — Await approval | Add dependencies, change CI, modify migrations | Pause, ask human |
| T3 — Block | rm -rf, force-push, delete branch | Block unconditionally |

Enforced by `orchestrator/hooks/pre-tool-use.sh`.

### 6.2 — MCP security gate

`orchestrator/hooks/mcp-security-gate.sh` validates every MCP tool call against the whitelist in `mcp.json`. Unknown servers/methods are blocked.

### 6.3 — Acceptance verification

Boris's #1 rule: every task has executable acceptance. The `verifier` sub-agent runs these independently before approval.

### 6.4 — CI enforcement

`.github/workflows/ci.yml` re-runs all acceptance commands on every push. Failed CI blocks merge.

### 6.5 — Evolution discipline (Project 1 lesson)

- **Never delete.** Move to `attic/`, `docs/historical/`, or `prompts/archive/`.
- **Number waves sequentially.** Cancelled waves → `attic/cancelled-wave-N/`.
- **ADRs for decisions.** Each major decision = one file in `docs/decisions/`.
- **CHANGELOG.md tracks visible changes.** Each wave ships → bump entry.
- **HIERARCHY.md stays accurate.** Update when folder structure changes.

---

## 7. Multi-Output Deliverables (Project 1 lesson)

Many projects ship more than code. Plan for these from day 1 if relevant:

```
deliverables/
├── paper/         # academic paper draft, figures, references
├── patent/        # patent draft + claims + prior-art search
├── report/        # technical report (15–25 pages typical)
├── slides/        # 12–15 slide deck
└── demo/          # demo videos, screenshots, recordings
```

Each gets a wave assigned to it. Example: `wave-9-final-report` produces `deliverables/report/`. Don't leave deliverables to the last minute.

---

## 8. Customization Checklist (when applying to a project)

When the orchestrator runs this OS-Setup on a fresh project, it fills in:

- [ ] `{{PROJECT_NAME}}` — folder name + project name in README
- [ ] `{{PROJECT_GOAL}}` — one-liner in README + CLAUDE.md
- [ ] `{{DOMAIN}}` — drives skill selection + folder layout
- [ ] `{{TECH_STACK}}` — drives Makefile, requirements.txt, pyproject.toml, rules/
- [ ] `{{MVP_DEFINITION}}` — first wave scope
- [ ] `{{WAVES}}` — 4–8 waves in `plan/EXECUTION.md`
- [ ] `{{ENTITIES}}` — domain model in `plan/ARCHITECTURE.md`
- [ ] `{{SUCCESS_METRICS}}` — in `plan/PRD.md`
- [ ] `{{RISKS}}` — risk register (in PRD or separate)
- [ ] `{{MCP_SERVERS}}` — domain-relevant servers in `mcp.json`
- [ ] `{{HAS_MODELS}}` — if yes, create `models/` with versioning convention
- [ ] `{{HAS_UI}}` — if yes, create `ui/` with assets
- [ ] `{{HAS_DELIVERABLES}}` — paper/patent/report/slides folders
- [ ] `{{HAS_DATA}}` — expanded `data/` taxonomy
- [ ] First wave's task files in `work/wave-1/`

---

## 9. Open Standards This Setup Respects

| Standard | Where it lives |
|---|---|
| **agentskills.io** (40+ tool standard) | `orchestrator/skills/*/SKILL.md` with YAML frontmatter |
| **MCP** (universal tool protocol) | `mcp.json` at root |
| **A2A** (agent-to-agent, optional) | Add when agents from different providers communicate |
| **Spec-Kit SDD** (constitution + specs + plan + tasks) | `.specify/` directory |
| **Kiro steering** | `.specify/steering.md` |
| **ADRs** | `docs/decisions/*.md` |
| **Conventional Commits** | enforced via `.pre-commit-config.yaml` |
| **Twelve-Factor App + Agents** | `orchestrator/core/12-factor.md` |
| **Keep a Changelog** | `CHANGELOG.md` |
| **Semantic Versioning** | tagged releases |

---

## 10. What Each Iteration Contributed

| Iteration | What it added | Where it lives now |
|---|---|---|
| #1 — Basic 3-folder split | plan/docs/prompts | merged into `plan/` + `docs/` + `prompts/archive` |
| #2 — 4 plan docs + specs | spec-driven discipline | `.specify/specs/` + 3 living `plan/` docs |
| #3 — Skills primitive | agentskills.io, CLAUDE.md auto-loaded | root `CLAUDE.md` + `orchestrator/skills/` |
| #4 — 12-Factor + 5 patterns + Spec-Kit | governance + canonical patterns | `orchestrator/core/` |
| #5 — Big fish (SuperClaude + BMAD + kmshihab + commands) | Full Claude OS pattern | `orchestrator/commands/` + `agents/` + `hooks/` + `recipes/` + `rules/` |
| Dedicated #1 — Dual-tier | orchestrator vs workers separation | `orchestrator/` + `work/` |
| Dedicated #2 — Simplified | One orchestrator (Claude/Kimi interchangeable), workers = OpenCode CLI, task files in work/ | THIS structure |
| **v1.1 — Project 1 lessons** | wave terminology, root CLAUDE/HANDOFF/HIERARCHY, attic/, deliverables/, expanded tests/, plural data/, models/ versioning, prompts/wave-N/ | All integrated above |

---

## 11. Final Self-Check Before Using

When the orchestrator finishes generating a project from this OS-Setup, it confirms:

- [ ] Root: `CLAUDE.md`, `KIMI.md` (identical content), `HANDOFF.md`, `HIERARCHY.md`, `README.md`, `HOW_TO_RUN.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `Makefile`, `mcp.json`, `requirements.txt` (or `package.json`), `pyproject.toml` (if Python), `.pre-commit-config.yaml`, `.gitignore`, `.env.example`, `Dockerfile`, `docker-compose.yml`
- [ ] `.claude/settings.local.json` exists (minimal)
- [ ] `orchestrator/` has: `ROLE.md`, `core/` (≥6 files), `commands/` (≥10 files), `skills/` (≥10 SKILL.md), `agents/` (≥4 files), `hooks/` (≥6 scripts), `recipes/` (≥1 YAML), `rules/` (per stack), `memory/MEMORY.md`, `scripts/`
- [ ] `work/` has: `TASK_TEMPLATE.md`, `REPORT_TEMPLATE.md`, `WORKER_PROMPT.md`, `wave-1/` with task files, `reports/wave-1/` exists
- [ ] `.specify/memory/constitution.md` reflects project principles
- [ ] `.specify/specs/wave-1/` has `spec.md` + `plan.md` + `tasks.md` + `contracts/`
- [ ] `plan/` has filled `PRD.md`, `ARCHITECTURE.md`, `EXECUTION.md` (no placeholders)
- [ ] `docs/` has: `decisions/`, `historical/`, `runbook.md`, `conventions.md`, `SCOPE_GUARD.md`
- [ ] `prompts/` has: `current/`, `archive/`
- [ ] `attic/` exists (empty initially)
- [ ] `deliverables/` has relevant subfolders (paper/patent/report/slides as applicable)
- [ ] `tests/` has: `unit/`, `integration/`, `e2e/`, `golden/`, `fuzz/`, `performance/`, `security/`
- [ ] `data/` has relevant subfolders (raw/, samples/, etc.) if data-heavy
- [ ] `models/` exists with versioning convention (if ML)
- [ ] `src/` exists with skeleton modules per architecture
- [ ] `.github/workflows/` has: `ci.yml`, `test.yml`, `security.yml` (+ `train_on_data.yml` if ML)
- [ ] No `{{PLACEHOLDER}}` remains in any committed file
- [ ] First wave is ready to dispatch

If any check fails, the setup is incomplete. Fix before declaring ready.

---

## 12. Invocation

To use this file for a new project:

```text
[Paste OS_SETUP.md into Claude Code or Kimi]

Project brief:
"""
<paste project PDF text or scope here>
"""

Use OS-Setup v1.1 to generate the complete project structure.
Use the methodology in OS_SETUP.md. Apply Project 1 lessons (wave terminology,
root CLAUDE/HANDOFF/HIERARCHY, attic/, deliverables/, expanded tests/, plural data/).
Fill all placeholders with project-specific content. Create the folder structure,
write all files, ask me only when you genuinely need a decision I haven't given you.

When done, print:
1. The folder you created
2. The first wave's task files ready to dispatch
3. The exact command to open in Claude Code or Kimi to start
```

---

## End of OS-Setup v1.1

This file is the single source of truth for the dual-tier agentic project setup. Update this file (not the generated project) when the methodology evolves. Generated projects are downstream — they get rebuilt from a new OS-Setup version.
