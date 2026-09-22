# ConcernSS — All session concerns (captured, none dropped)

> **Purpose:** Single source of every concern raised in this multi-session effort.
> Emotional weight noted — these were treated as must-not-miss items, not backlog noise.
> Each entry: what you said (intent), why it matters, full intent, completion stance.

**Source note:** Reconstructed from session handoff + decisions on record (this file is
the first time all three deliverables exist together; see also [hybrid-ultimate.md](hybrid-ultimate.md)
and [../handoff3.md](../handoff3.md)). If a concern is missing or misremembered, correct
this file — it is the contract.

---

## A. Cross-harness setup (Claude Code + OpenCode + Cursor)

| # | Concern | Why it matters | Full intent | Status |
|---|---------|----------------|-------------|--------|
| A1 | Build an "ultimate" cross-harness setup across all three harnesses | One setup should work everywhere, not per-tool islands | Claude Code, OpenCode, Cursor all first-class; shared skills/MCP so nothing drifts | **Done** — 3 harnesses wired; 7→4 cleaned (removed codex/kimi-code/gemini/aider) |
| A2 | Reduce harness sprawl (too many half-configured tools) | 7 harnesses = broken configs, dead symlinks, personal bias | Keep only working, actively used harnesses | **Done** — 4 remain; 10 broken symlinks removed, 24 healthy added |
| A3 | Personal/OS bias must not leak into shared config | Settings polluted with machine-specific paths/content | De-personalize shared config; keep only necessary absolute bin paths | **Done** — personal block stripped from `~/.claude/settings.json` |
| A4 | Skills must be healthy everywhere, not just installed | Broken skill = silent failure at runtime | Verify SKILL.md present across all harness skill dirs | **Done** — skills-health **214/214** healthy |
| A5 | Harness audit should show honest score, not inflate | Trust requires real numbers | Run `harness-audit` and fix real gaps only | **Partial** — **27/39**; remaining fails are project-local `.claude/` tailoring, memory persistence, security hooks (documented below, section G) |

## B. MCP integrations (research-backed picks)

| # | Concern | Why it matters | Full intent | Status |
|---|---------|----------------|-------------|--------|
| B1 | MCP format differs per harness — don't hardcode one | Wrong format = silent no-op | Claude user-scope via `claude mcp add --scope user`; OpenCode `"mcp"` key; Cursor `~/.cursor/mcp.json` | **Done** — formats correct per harness |
| B2 | Don't blow the tool budget (3–6 servers / ~40 tools) | Too many tools degrades agent focus | Research consensus respected: skip filesystem, sequential-thinking | **Done** |
| B3 | GitHub MCP must work without relying on deprecated packages | `@modelcontextprotocol/server-github` deprecated | Official GitHub HTTP MCP + stdio bridge | **Done** — `~/.local/bin/github-mcp-bridge` (PAT file → `gh auth token` → `npx mcp-remote`) |
| B4 | GitHub PAT must not be committed or left loose in configs | Credential leak risk | Store at `~/.config/github/pat` chmod 600; reference by path | **Done** — perms `600`; **but PAT was pasted in chat → rotate (see Open item O1)** |
| B5 | swa-erp postgres MCP must be read-only by default | Dev DB safety | `default_transaction_read_only=on` in DSN | **Done** — SELECT ok, CREATE blocked |
| B6 | Project-scope MCP approval requires user action | Cannot self-approve | Run `claude` once inside swa-erp to approve `postgres` | **Blocked (user)** — shows "⏸ Pending approval" |
| B7 | Tavily skip must be documented, not silent | Missing key shouldn't look like a bug | No `TAVILY_API_KEY` → Tavily skipped intentionally | **Done** — documented |
| B8 | Dead `mcp.json` was confusing | Wrong file referenced by role docs | Archive to `docs/historical/mcp.json.deprecated` | **Done** |
| B9 | Duplicate `opencode.jsonc` risked config split-brain | Two configs = which wins? | Archive one; single canonical `opencode.json` | **Done** |
| B10 | Vercel plugin auth is a known pre-existing gap | Not part of this task, don't fake-pass it | Document "Needs authentication" as pre-existing | **Done** |
| B11 | OpenCode MCP: keep to high-value set | Tool budget | github, playwright, context7, ecc-memory, parallel-search | **Done** |
| B12 | Cursor MCP: mirror OpenCode where formats allow | Cross-harness parity | context7, ecc-memory, github, opencode, playwright | **Done** (untestable w/o Cursor running) |
| B13 | Claude user-scope MCP set | Team-repo reuse | github, opencode, ecc-memory; playwright+context7 via plugins | **Done** |
| B14 | JSON validity of all MCP configs | One syntax error kills the file | Validate after every edit | **Done** — all JSON OK this session |
| B15 | exa websearch intermittent 429 | Research quality risk | Tolerate 429, retry | **Known** — tolerated |
| B16 | NEXUS MCP (31 tools) rejected | Tool budget violation | Do not add | **Done** |

## C. Skills (graphify, ECC, Superpowers, addyosmani)

| # | Concern | Why it matters | Full intent | Status |
|---|---------|----------------|-------------|--------|
| C1 | graphify is the #1 pick — must be present everywhere | Knowledge-graph layer is core | SKILL.md in claude/opencode/agents + cursor | **Done** — 4/4; was missing on Cursor, fixed via `~/.cursor/skills/graphify` symlink |
| C2 | ECC is the backbone ("mainly ECC") | ECC skills + scripts are the operating system of this setup | Keep ECC healthy; don't overwrite `mcp-configs/mcp-servers.json` | **Done** — ECC-managed config left untouched |
| C3 | Superpowers already installed — don't reinstall | Idempotence | Verify presence, skip | **Done** |
| C4 | addyosmani/agent-skills identified, not present | New research pick, intentional install pending | Candidate to implement in next research pass | **Pending** (research pick, not yet installed — next after LAYA) |
| C5 | code-compass noted as candidate | Research pick | Evaluate with addyosmani in one batch | **Pending** (next after LAYA) |
| C6 | No personal-bias content in shared skills | De-personalization | Strip srujansai/SEBI/ControlPlane/Accenture-bias content from shared skill text | **Done** (OS-username absolute paths OK) |

## D. LAYA (System-1 decision gate) — highest-stakes concern

| # | Concern | Why it matters | Full intent | Status |
|---|---------|----------------|-------------|--------|
| D1 | LAYA must be a shared System-1 gate across ALL projects, not SWA-only | Reuse + consistency | One shared pkg `karna-decisions` | **Done** — `packages/karna_decisions/` populated (packs + gate + selftest) |
| D2 | `Router(preload=True)` is mandatory | Cold-start/first-call reliability | Always preload | **Done** — verified; singleton in `laya_gate._get_router` |
| D3 | Never put LAYA on money/ID/RBAC/GST paths | Wrong confident call = financial/security harm | Boundary-only: inbound email, sheet risk, scope guard, prompt guard, admission | **Done** — allow-list in packs + `LayaBoundaryError`; `laya_gate.py` written |
| D4 | Question packs must be versioned dicts | Reproducible decisions | Packs: `swa.inbound_email`, `swa.sheet_row_risk`, `harness.scope_guard`, `harness.prompt_guard`, `controlplane.admission` | **Done** — 5 packs, `version: 1`, selftest + unit tests |
| D5 | `gate.py` must escalate on low confidence / gray band | Uncertainty must never auto-escalate silently or auto-approve | conf < T or noul gray band → human escalate | **Done** — conf < 0.70, noul [0.40, 0.60], fail-closed; 7/7 unit tests |
| D6 | ADR "System-1 gates at boundary" — 0003 taken → use **0005** | Numbering integrity | Write `docs/decisions/0005-*.md` | **Done** — `0005-system-1-gates-at-boundary.md` |
| D7 | No `laya` import under `src/backend/services/*` except `laya_gate.py` | Boundary rule | Enforce via import discipline | **Done** — only `laya_gate.py:43` imports laya |
| D8 | Graphify mandatory for LAYA context | Decision context from graph | Tie laya-gate skill to graphify | **Done** — skill requires `/graphify` first |
| D9 | Base checkpoint near-chance zero-shot → labeled eval set required | Cannot trust unlabeled accuracy | Build labeled eval before trusting | **Done (scaffold)** — `evals/laya/labeled.json` + `run_eval.py`; **0.750 on n=12** (tiny set — expand before trust) |
| D10 | EN/HI dry-run, then STOP before ERP routers | Don't wire into production domain until calibrated | Dry-run only | **Done** — `scripts/laya_dry_run.py` ran; EN→english, HI→multilingual; **hard stop still in force** |
| D11 | `laya==0.3.5` pin | Reproducibility | Pin in `requirements.txt` | **Done** — line 28 |
| D12 | `.venv-laya` isolated venv | Don't pollute main env | uv venv Python 3.11, laya 0.3.5 | **Done** |
| D13 | Router preload warnings: temps out of [0.5,5] on choice:11+ clamped; HF_TOKEN unauthenticated | Confidence uncalibrated on affected buckets | Document; authenticate HF before trusting scores | **Documented** — HF_TOKEN not set (O6) |
| D14 | laya-gate skill for 3 harnesses | Consistent invocation | Skill in claude/opencode/cursor | **Done** — symlinks claude + agents + cursor → opencode skill |
| D15 | laya must never claim ERP correctness | Honest framing | Reports must not say LAYA is validated for ERP | **Standing rule** |

## E. Honesty / framing / de-personalization (emotional core)

| # | Concern | Why it matters | Full intent | Status |
|---|---------|----------------|-------------|--------|
| E1 | No "ultimate / better than all" claims in reports | Trust + intellectual honesty | User may *name* their file "hybrid ultimate"; reports stay factual | **Standing rule** — hybrid doc name OK, report prose honest |
| E2 | No srujansai / SEBI / ControlPlane / Accenture bias in shared content | Portable, non-identifying setup | De-personalize | **Done** |
| E3 | Absolute bin paths with OS username are acceptable | Practical necessity | Don't strip functional paths | **Done** |
| E4 | Do not fabricate test results / wave numbers | Truth hierarchy: code/tests > docs | Cite only run evidence | **Standing** |
| E5 | 195 historical secrets in git history — flag, don't hide | Security reality | gitleaks wired for future; history remediation = separate task | **Flagged** (Open O3) |
| E6 | PAT exposure flagged, not buried | You care about real risk | Recommend rotation | **Flagged** (Open O1) |

## F. Repo / wave hygiene (swa-erp ERP track)

| # | Concern | Why it matters | Full intent | Status |
|---|---------|----------------|-------------|--------|
| F1 | Waves 1–51 all accounted for exactly once | Orchestration integrity | ACTIVE.md vs ARCHIVE.md no orphans | **Done** — all SHIPPED |
| F2 | Soft-delete matrix must match code | Data integrity | ADR-0003 + conventions.md agree | **Done** |
| F3 | API versioning + idempotency shipped shape differs from original proposal — document as-built | Docs shouldn't lie | ADR-0004 records shipped header + Postgres store | **Done** |
| F4 | Redis rejected for idempotency (must survive flush) | Correctness | Postgres `idempotency_keys` | **Done** |
| F5 | 422 chosen over 409 for idempotency body-mismatch | Match API validation family | Documented in ADR-0004 | **Done** |
| F6 | Audit log immutable (no soft-delete) | Regulatory | Migration 0041 | **Done** |
| F7 | Document deleted_at deliberately removed (0026) — never re-add | Two delete mechanisms compete | Documented | **Done** |
| F8 | Dirty working tree not from this task | Don't touch unrelated WIP | `deps.py`, frontend package files, e2e specs, SustainabilityPage, playwright.config.ts, root `package.json` left alone | **Respected** |
| F9 | Frontend coverage threshold 60% (60.46% at wave-51) | Quality bar | Don't regress | **Standing** |
| F10 | External blockers must not stall engineering | Viraj server facts, Excel freeze | Document as external | **Standing** (HANDOFF.md) |

## G. ECC harness-audit residual (27/39)

| # | Concern | Why it matters | Full intent | Status |
|---|---------|----------------|-------------|--------|
| G1 | No project-local `.claude/` tailoring in swa-erp | Tool-coverage score | Add hooks/commands/skills/settings scoped to repo | **Pending** |
| G2 | No durable project memory file (`.claude/memory.md` / `docs/adr/`) | Memory persistence score | Add memory + ADRs (ADRs exist under `docs/decisions/`, audit wants `docs/adr/` path or memory.md) | **Pending** |
| G3 | No project-local hook settings for prompt/tool guardrails | Security-guardrail score | Add `.claude/settings.json` hooks | **Pending** |
| G4 | Don't chase score for its own sake | Only fix real gaps | | **Standing** |

## H. Open / blocked items

| # | Item | Action needed | Owner |
|---|------|---------------|-------|
| O1 | Rotate GitHub PAT (was pasted in chat) | New PAT → `~/.config/github/pat` (600), update bridge | **User** |
| O2 | Approve project `postgres` MCP | Run `claude` once inside swa-erp | **User** |
| O3 | 195 historical secrets in git history | Separate remediation task (gitleaks already in pre-commit for new commits) | Future work |
| O4 | Tavily | Add `TAVILY_API_KEY` if web-search MCP desired | User (optional) |
| O5 | Vercel plugin OAuth | Auth when needed | User (optional) |
| O6 | HF_TOKEN for LAYA | Authenticate to silence HF warning / any gated assets | User (optional) |

---

**Count:** 5 (A) + 16 (B) + 6 (C) + 15 (D) + 6 (E) + 10 (F) + 4 (G) + 6 (H) = **68 tracked concerns**
(plus sub-items folded into rows above; reconstructed set — correct any row rather than assuming completeness.
**Post-refinement note:** intentionally excludes transient skill-scan / glob-loop session noise that
was not part of the heartfelt concern set; those remain out of scope.)
