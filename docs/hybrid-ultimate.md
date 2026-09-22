# Hybrid Ultimate — decisions done + intentions + concerns (merged)

> **Name note:** You asked for a file named around "hybrid ultimate." The *report prose*
> stays honest (no "better than all" claims); the *filename* is yours. Facts below are
> only things actually run or verified this session.
>
> Merges three streams: **Decisions DONE**, **Intentions still open**, and **Concerns**
> (full list with status in [concernSS.md](concernSS.md)). Hand-over in
> [../handoff3.md](../handoff3.md).

---

## 1. Decisions DONE (verified)

### 1.1 Harness set (3 + swa-erp project scope)
- **Kept:** Claude Code, OpenCode, Cursor (+ swa-erp repo-local `.claude/`).
- **Removed:** `~/.codex`, `~/.kimi-code`, `~/.gemini`, `~/.aider`.
- **Symlinks:** 10 broken removed, 24 working added.
- **De-personalized:** personal block stripped from `~/.claude/settings.json`.
- **Evidence:** skills-health **214/214** healthy; harness-audit **27/39** (residuals = section 3).

### 1.2 MCP (research-backed, tool budget respected)
| Harness | Servers |
|---------|---------|
| Claude (user scope) | github, opencode, ecc-memory (+ playwright/context7 via plugins) |
| OpenCode `opencode.json` | github, playwright, context7, ecc-memory, parallel-search |
| Cursor `~/.cursor/mcp.json` | context7, ecc-memory, github, opencode, playwright |
| swa-erp `.mcp.json` | postgres (read-only DSN, `default_transaction_read_only=on`) |

- **GitHub:** official HTTP MCP via stdio bridge `~/.local/bin/github-mcp-bridge`
  (PAT file → `gh auth token` fallback → `npx mcp-remote`). Bridge **PASS**.
- **Skipped by design:** filesystem, sequential-thinking (budget), Tavily (no key),
  NEXUS MCP (31 tools), deprecated `@modelcontextprotocol/server-github`.
- **Hygiene:** dead `mcp.json` → `docs/historical/mcp.json.deprecated`; duplicate
  `opencode.jsonc` archived; all JSON validated.
- **Known non-blocking:** postgres "⏸ Pending approval" (user runs `claude` in swa-erp);
  vercel plugin OAuth pre-existing.

### 1.3 Skills
- **graphify:** 4/4 harnesses (was missing on Cursor → `~/.cursor/skills/graphify` symlink fixed).
- **ECC:** backbone; `~/.config/opencode/mcp-configs/mcp-servers.json` left ECC-managed (untouched).
- **Superpowers:** already installed — not reinstalled.
- **gitleaks v8.30.1:** `.pre-commit-config.yaml` (new commits only).

### 1.4 LAYA slice (implemented; ERP wiring still hard-stopped)
- `.venv-laya`: Python 3.11.15 (uv), `laya 0.3.5`, import OK; pinned in `requirements.txt`.
- `Router(preload=True)` **verified**; singleton in `laya_gate._get_router`; warnings recorded
  (temps clamped on `choice:11+`; `HF_TOKEN` unauthenticated).
- **`packages/karna_decisions/`** populated: 5 versioned packs + `gate.py`
  (escalate conf < 0.70, noul gray band [0.40, 0.60], fail closed) + `selftest.py`.
- **`src/backend/services/laya_gate.py`** — sole services importer of `laya`; boundary
  allow-list rejects non-boundary packs (`LayaBoundaryError`).
- **ADR-0005** `docs/decisions/0005-system-1-gates-at-boundary.md`.
- **Skill `laya-gate`** → claude + agents + cursor (symlinks to opencode); Graphify-first rule.
- **Dry-run ran:** `scripts/laya_dry_run.py` → `evals/laya/dry_run_report.json`
  (EN→english, HI→multilingual routing correct; escalate on all smoke samples).
- **Labeled eval scaffold:** `evals/laya/labeled.json` + `run_eval.py` →
  **accuracy 0.750 on n=12** (tiny hand set — expand before trusting; hard stop stands).
- **Unit tests:** `tests/unit/test_laya_gate_rules.py` — **7/7 passed**.
- Standing rules locked: boundary-only (never money/ID/RBAC/GST); Graphify mandatory;
  EN/HI dry-run done → **STOP before ERP routers** (no API wiring).

### 1.5 swa-erp wave track (context, not this task's focus)
- Waves 1–51 each accounted once, all SHIPPED (ACTIVE vs ARCHIVE no orphans).
- ADR-0003 soft-delete matrix, ADR-0004 API versioning+idempotency (as-built: header +
  Postgres `idempotency_keys`, 422 not 409) on record.
- Dirty tree (deps.py, frontend pkgs, e2e specs, etc.) left untouched — not ours.

---

## 2. Intentions STILL OPEN (next work)

### 2.1 LAYA slice — DONE (ERP wiring still open by design)
1. ✅ Populate `packages/karna_decisions/` — 5 versioned packs.
2. ✅ `gate.py` + `src/backend/services/laya_gate.py`.
3. ✅ ADR `docs/decisions/0005-system-1-gates-at-boundary.md`.
4. ✅ `laya==0.3.5` → `requirements.txt`.
5. ✅ laya-gate skill for 3 harnesses (Graphify-backed).
6. ⚠️ Labeled eval scaffold written; **0.750 / n=12** — expand set before trusting.
7. ✅ EN/HI dry-run ran → **HARD STOP still in force** before any ERP router wiring.

### 2.2 New research picks (after LAYA)
- **addyosmani/agent-skills** — 0/10 present; install chosen skills.
- **code-compass** — evaluate in same batch; accept/reject with reason.
- Then honest final report (no "ultimate" claims in prose).

### 2.3 ECC audit residuals (section 3) — fix real gaps only, not score-chasing.

---

## 3. Concerns (summary — full detail in concernSS.md)

- **79 tracked concerns** across: harness (A), MCP (B), skills (C), LAYA (D),
  honesty/de-personalization (E), wave hygiene (F), audit residuals (G), open items (H).
- **Emotional core:** nothing dropped; every row has why / full intent / stance.
- **Open items needing you:**
  - **O1** Rotate GitHub PAT (was in chat) → `~/.config/github/pat` (600).
  - **O2** Approve swa-erp `postgres` MCP (`claude` once in repo).
  - **O3** 195 historical secrets — separate remediation (gitleaks covers new commits).
  - **O4/O5/O6** optional: Tavily key, Vercel OAuth, HF_TOKEN for LAYA.
- **harness-audit 27/39 residuals:**
  - **G1** project-local `.claude/` tailoring (hooks/commands/skills/settings) in swa-erp.
  - **G2** durable memory (`docs/decisions/` exists; audit also wants `.claude/memory.md` or `docs/adr/` path).
  - **G3** project-local hook settings (prompt/tool guardrails).
  - **G4** don't chase the number — only fix real gaps.

---

## 4. One-line status

**Setup wired (3 harnesses, MCP, skills); LAYA slice implemented + selftest/unit tests green
+ EN/HI dry-run done (eval n=12 acc 0.75 — expand set); ERP router wiring still hard-stopped;
research picks (addyosmani, code-compass) + audit residuals open; PAT rotate + postgres approve still yours.**
