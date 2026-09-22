# handoff3.md — Session handover (cross-harness + LAYA + concerns)

> Third-generation handoff. Read order: this file → [docs/hybrid-ultimate.md](docs/hybrid-ultimate.md)
> → [docs/concernSS.md](docs/concernSS.md). Older context: `HANDOFF.md` (repo waves/external blockers).

---

## 1. What this session was about

1. Build a research-backed **cross-harness agent setup** (Claude Code + OpenCode + Cursor):
   graphify, ECC, MCP servers, de-personalized, honest framing.
2. Wire **LAYA** as a shared **System-1 decision gate** across projects — implement to the max.
3. Capture **every concern** you raised (emotional, must-not-miss) in deliverable docs, then
   sort/fix against the merged list.

## 2. What is DONE (trust this)

- 3 harnesses configured; 4 legacy harness dirs deleted; 10 broken symlinks cleaned.
- MCP wired + verified per harness (formats correct, JSON valid, GitHub bridge PASS).
- skills-health **214/214**; graphify **4/4** (Cursor gap fixed); Superpowers not reinstalled.
- gitleaks in pre-commit; dead/duplicate config files archived.
- `.venv-laya` + `laya 0.3.5` + `Router(preload=True)` verified; warnings documented.
- **Three deliverables exist:** `docs/concernSS.md`, `docs/hybrid-ultimate.md`, this file.
- **LAYA slice written:** packs + gate + `laya_gate.py` + ADR-0005 + skill + dry-run +
  labeled eval scaffold + 7/7 unit tests; import discipline verified (only `laya_gate.py`).
- Dirty tree in swa-erp (deps.py, frontend, e2e, Makefile, etc.) **left untouched** — not part of this work.

## 3. What is NOT done (next agent starts here)

### Priority 1 — LAYA slice — **DONE** (see checkboxes below; ERP wiring still hard-stopped)
### Priority 2 — Research picks
- [x] `packages/karna_decisions/` — 5 versioned packs + `gate.py` + `selftest.py`.
- [x] `src/backend/services/laya_gate.py` (sole services `laya` importer; boundary allow-list).
- [x] `docs/decisions/0005-system-1-gates-at-boundary.md`.
- [x] `laya==0.3.5` in `requirements.txt`.
- [x] laya-gate skill → claude + agents + cursor (Graphify-backed; source: `~/.config/opencode/skills/laya-gate`).
- [x] Labeled eval scaffold `evals/laya/` — dry-run + `run_eval.py` ran (**acc 0.750, n=12** — expand before trust).
- [x] Unit tests `tests/unit/test_laya_gate_rules.py` **7/7**; pure selftest OK; ruff/black clean.
- [x] EN/HI dry-run ran → **hard stop** before ERP routers (no API wiring — by design).
- Rules: `Router(preload=True)` always; **no** laya on money/ID/RBAC/GST; only
  `laya_gate.py` may import laya under `src/backend/services/`.
- Remaining LAYA work: expand labeled set → re-run eval → only then consider ERP boundary wiring;
  optional `HF_TOKEN` (O6).

### Priority 2 — Research picks
- [ ] addyosmani/agent-skills (0/10 present) — install chosen.
- [ ] code-compass — evaluate, accept/reject with reason.
- [ ] Honest final report (prose: no "ultimate/better-than-all"; filename may say ultimate).

### Priority 3 — ECC audit residuals (real gaps only)
- [ ] swa-erp project-local `.claude/` (hooks/commands/skills/settings).
- [ ] Durable memory path the audit expects (`.claude/memory.md` or `docs/adr/` alias).
- [ ] Project-local prompt/tool guardrail hooks.

### LAYA follow-on (not blocking research)
- [ ] Expand `evals/laya/labeled.json` well past n=12; re-run `run_eval.py`.
- [ ] Only after eval holds: consider wiring `laya_gate.decide` at a non-money ERP boundary.

## 4. User-blocked (do not fake-complete)

| ID | Action |
|----|--------|
| O1 | **Rotate GitHub PAT** (exposed in chat) → `~/.config/github/pat` mode 600; bridge reads `GITHUB_PAT_FILE` |
| O2 | Approve swa-erp **postgres** MCP: run `claude` once inside the repo |
| O3 | 195 historical secrets — separate remediation task |
| O4–O6 | Optional: `TAVILY_API_KEY`, Vercel OAuth, `HF_TOKEN` (LAYA) |

## 5. How to verify before claiming done

```bash
node ~/.config/opencode/scripts/skills-health.js     # expect 214/214 (or better)
node ~/.config/opencode/scripts/harness-audit.js     # 27/39 → improve only real gaps
python -c "import json; [json.load(open(p)) for p in [
  '~/.config/opencode/opencode.json','~/.cursor/mcp.json',
  '<repo>/.mcp.json']]"                             # all configs parse
# LAYA:
.venv-laya/bin/python -c "from laya import Router; Router(preload=True)"
.venv-laya/bin/python -m packages.karna_decisions.selftest   # OK packs=5
python3 -m pytest tests/unit/test_laya_gate_rules.py -q      # 7 passed
rg -n 'from laya|import laya' src/backend/services/          # only laya_gate.py
```

- Run any acceptance commands cited in ADR-0005 / gate tests before approving LAYA work.
- Do not report wave numbers or test passes you did not run.

## 6. Standing rules (carry forward)

1. Honesty: facts/tests > docs; no fabricated results; no "ultimate" claims in report prose.
2. De-personalize shared content; OS-username absolute paths OK.
3. LAYA never touches money/ID/RBAC/GST; escalate on low confidence.
4. Tool budget ~3–6 MCP/harness; Graphify mandatory for LAYA context.
5. Archive, don't delete (repo: `attic/`, `docs/historical/`, `prompts/archive/`).
6. Don't commit unless asked; don't touch unrelated dirty files.
