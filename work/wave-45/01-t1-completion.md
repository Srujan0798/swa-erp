# Wave-45 Task 01 — Close the remaining T1 gaps + 2026 skills schema

Adaptoid §11 T1 self-check. swa-erp is a strong T1 but 4 root files and several directories are missing, and every `orchestrator/skills/*/SKILL.md` predates the 2026 unified schema.

## Files you own (touch nothing else)
- `AGENTS.md`, `pytest.ini`, `skills.manifest.json`, `skills-lock.json`
- `orchestrator/skills/*/SKILL.md` (frontmatter only — do NOT rewrite skill bodies)
- `docs/waves/`, `docs/interview_runbook.md`
- `prompts/current/`, `prompts/INDEX.md`, `prompts/EXAMPLE_FILLED_TASK.md`
- `tests/{unit,integration,golden,fuzz,security}/.gitkeep`

## The work

### 1. `AGENTS.md`
Cursor/Codex read `AGENTS.md` the way Claude Code reads `CLAUDE.md`. `CLAUDE.md` and `KIMI.md` are already byte-identical here by design. Make `AGENTS.md` a **symlink** to `CLAUDE.md` if the repo tolerates it (check whether the preflight hook and Windows compatibility allow it); otherwise copy it and add a CI check that the three stay identical. State which you chose and why — silent divergence between these files is a real risk.

### 2. `pytest.ini`
`pyproject.toml` already carries pytest config including `--import-mode=importlib` (required for wave-33 test collection). Do **not** duplicate config into two places — that is FM-06 (config revert) waiting to happen. Either create `pytest.ini` as a pointer/minimal file, or document in the report why `pyproject.toml` remains the single source and skip it. Honest skip is acceptable here; silent duplication is not.

### 3. `skills.manifest.json` + `skills-lock.json` (§4.10)
Inventory the skills this project actually depends on. Pin versions. The lock file needs resolved versions + checksums for reproducibility.

### 4. Upgrade skill frontmatter to the 2026 schema (§4.22)
Every `orchestrator/skills/*/SKILL.md` gets `allowed-tools`, `invocation`, and `subagent` fields. Be deliberate:
- read-only skills (`verify-work`, `diagnose`, `zoom-out`, `status-report`) → `subagent: true`, narrow `allowed-tools`
- write skills (`merge-work`, `write-task-file`) → tighter `allowed-tools`, `invocation: both`
**Do not change any skill's body or behaviour** — frontmatter only.

### 5. `docs/waves/`
One `wave-N-brief.md` stub per shipped wave pointing at its real report, plus `wave-N-gotchas.md` where genuine gotchas are already recorded in reports (§4.3). Do not invent gotchas; harvest real ones from `work/reports/`.

### 6. `docs/interview_runbook.md` (§4.15)
Ground the examples in this project's real ambiguities — the four questions Viraj answered (4th agreement type, INSUDESIGN, yearly ID reset, no Leads sheet) are good worked examples of well-framed vs badly-framed questions.

### 7. `prompts/`
`current/` holds the worker prompts actually in use; `INDEX.md` navigates them; `EXAMPLE_FILLED_TASK.md` is a real worked example (use a shipped wave brief). `prompts/archive/` already exists — leave it.

### 8. `tests/` taxonomy
Create the missing subdirectories with `.gitkeep`. **Do not move existing tests** — `tests/wave-N/` is this project's established convention and moving them would break every report reference (FM-03).

## Acceptance criteria
- [ ] `CLAUDE.md`, `KIMI.md`, `AGENTS.md` verified identical — paste the diff/checksum command and result
- [ ] `python3 -c "import json; json.load(open('skills.manifest.json')); json.load(open('skills-lock.json'))"` passes
- [ ] Every `orchestrator/skills/*/SKILL.md` has all three new frontmatter fields — paste a grep count vs file count
- [ ] Skill bodies unchanged: `git diff --stat` shows frontmatter-only edits
- [ ] Full backend + frontend suites unchanged (zero application code touched)

## Deliver
`work/reports/wave-45/01-t1-completion.report.md`. Commit before writing it.

## Constraints
- Time budget: 120 min · commit per numbered item
- If something is better left as-is, write "NOT DONE + why" — an honest skip beats a harmful change
