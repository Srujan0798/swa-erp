# FINAL-CLOSE — Ultimate Project Close Pack

> **Role:** Single entry for finishing the professional-grade track and closing
> swa-erp as an internship submission. Part of the front-door set after
> [README.md](../../README.md) → this pack when the goal is **close, not build**.

## What this is

The product (waves 1–31, v1.0.1) is **feature-complete**.  
The professional-grade evidence track (waves 32–39) is **mostly done**.  
This pack finishes the last mile and **closes** the project.

**Chosen intensity (user-confirmed):** Full close  
`hygiene → fix flakes → wave-37 adversarial review → wave-38 submission package → DONE`

## Start here (human)

1. Read [`ULTIMATE-CLOSE-GUIDE.md`](ULTIMATE-CLOSE-GUIDE.md) once (15–20 min).
2. Open a **new Claude Code session** in `/Users/srujansai/Desktop/swa-erp`.
3. Paste **exactly** [`prompts/PASTE-TO-CLAUDE.md`](prompts/PASTE-TO-CLAUDE.md).
4. When a session ends mid-phase, paste from [`prompts/CONTINUE-SESSIONS.md`](prompts/CONTINUE-SESSIONS.md).
5. Do **not** invent new waves. Do **not** re-ask Viraj the 8 server questions.

## Files in this pack

| File | Purpose |
|---|---|
| [`ULTIMATE-CLOSE-GUIDE.md`](ULTIMATE-CLOSE-GUIDE.md) | Master plan, phases, categories, DoD |
| [`PROTOCOLS.md`](PROTOCOLS.md) | 20 executable protocols (P01–P20) |
| [`TASK-CATEGORIES.md`](TASK-CATEGORIES.md) | 12 high-level task categories |
| [`ANTI-FABRICATION.md`](ANTI-FABRICATION.md) | Hard rules from this project's lie history |
| [`DEFINITION-OF-DONE.md`](DEFINITION-OF-DONE.md) | When you may say "closed" |
| [`prompts/PASTE-TO-CLAUDE.md`](prompts/PASTE-TO-CLAUDE.md) | Session-1 starter (copy entire file) |
| [`prompts/CONTINUE-SESSIONS.md`](prompts/CONTINUE-SESSIONS.md) | Session-2+ resume prompts |
| [`../reports/COMPLETION-HANDOFF-VERDICT.md`](../reports/COMPLETION-HANDOFF-VERDICT.md) | Living truth table (as-of 2026-08-23) |

## What is already done (do not redo)

- Waves **32, 33, 34, 35, 36 (code+02), 39** — landed on `origin/main` @ `4050f51`
- Backend independently verified: **5 failed / 557 passed / 1 skipped, 86%**
- Frontend thresholds met (~61% stmts independent); 1 TaskCard flake known
- Product features + Viraj data answers locked
- Push of wave-33 finish already done

## What remains (only this)

1. Status-doc hygiene (`ACTIVE.md`, `HANDOFF.md`, …)
2. Stabilize (401-vs-403 tests, TaskCard IST flake, optional Vitest-in-CI)
3. **Wave-37** independent review
4. **Wave-38** submission package
5. Say closed — with honest external deploy caveat (Viraj / no IT dept)

## Anti-pattern ban

- Do **not** create 30–40 empty “protocol” files for theater.
- Do **not** claim “100% complete” while 37/38 are undone.
- Do **not** claim global “no module &lt;70%” (false; only the 5 wave-33 targets + all `services/` are proven).
- Do **not** cite frontend **65.86%** — use independent ~**61%** or a fresh paste.
- Do **not** re-blast `SEND_IT.md` / `SEND_VIRAJ.md` to the client group.
