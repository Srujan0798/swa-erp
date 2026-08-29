# Dispatch Plan — remaining work to submission

> Written 2026-08-29 by the orchestrator. Every finding below was independently verified
> against the code in this repo, not carried forward from a worker report. **10 tasks,
> 6 rounds.** Dispatch rounds in order; tasks *within* a round have disjoint file sets and
> are safe to run in parallel (FM-13).

## Why the order matters

**Wave-49 must go first.** It changes `get_db()` — the session lifecycle every backend
change depends on. If the wave-48 tasks land first and then 49 changes commit semantics
underneath them, all of 48's verification is invalidated and has to be redone.

**Wave-51 must go last.** It re-measures every number in the front-door docs. Run it
before the others land and its numbers are stale within a day — the FM-12 failure this
repo has already hit.

---

## Round 1 — critical fix + two disjoint independents

| Task | Brief | Touches | Budget |
|---|---|---|---|
| **49-01** ⚠️ CRITICAL | [`work/wave-49/01-transaction-atomicity.md`](wave-49/01-transaction-atomicity.md) | `db/session.py`, `services/inquiry_service.py`, core-chain repos | 150 min |
| 40-02 | [`work/wave-40/02-metrics-script-fix.md`](wave-40/02-metrics-script-fix.md) | `scripts/`, `plan/EXECUTION.md` | 90 min |
| 48-05 | [`work/wave-48/05-frontend-loading-states-and-bundle-splitting.md`](wave-48/05-frontend-loading-states-and-bundle-splitting.md) | `src/frontend/` only | 90 min |

Three agents, zero file overlap: backend-core ‖ scripts/docs ‖ frontend.

**49-01 is the single most important task in this plan.** The core
Inquiry→Client→Project chain — the exact workflow the client asked for — can leave
orphaned rows on a partial failure. 21 of 25 repository files commit independently
mid-request. Verify its atomicity test genuinely fails on the old code before accepting.

---

## Round 2 — narrow backend, parallel

| Task | Brief | Touches | Budget |
|---|---|---|---|
| 48-02 | [`work/wave-48/02-pagination-idempotency.md`](wave-48/02-pagination-idempotency.md) | `api/compliance.py`, `api/sustainability_metrics.py`, idempotency layer | 90 min |
| 48-03 | [`work/wave-48/03-token-security-hygiene.md`](wave-48/03-token-security-hygiene.md) | `main.py` (CSP), `services/auth_service.py` | 90 min |

---

## Round 3 — service-layer logging (alone)

| Task | Brief | Touches | Budget |
|---|---|---|---|
| 48-04 | [`work/wave-48/04-service-layer-logging.md`](wave-48/04-service-layer-logging.md) | all 30 `services/*.py` | 90 min |

Wide blast radius across every service file — nothing else runs alongside it.

---

## Round 4 — production hardening (alone)

| Task | Brief | Touches | Budget |
|---|---|---|---|
| 48-01 | [`work/wave-48/01-production-hardening.md`](wave-48/01-production-hardening.md) | 26 routers, `core/rate_limit.py`, several services, frontend error boundary + a11y | 150 min |

Also wide, and overlaps 48-04's service files — must follow Round 3, not share it.

---

## Round 5 — deferred RISK closure, parallel

| Task | Brief | Touches | Budget |
|---|---|---|---|
| **50-01** 🆕 | [`work/wave-50/01-deferred-security-risks.md`](wave-50/01-deferred-security-risks.md) | `api/jobs.py`, `workers/`, `main.py`, `core/config.py` | 150 min |
| **50-02** 🆕 | [`work/wave-50/02-deterministic-test-suite.md`](wave-50/02-deterministic-test-suite.md) | `tests/`, `conftest.py`, CI workflow | 90 min |

Both briefs are new (written 2026-08-29) and close gaps nothing else covered:

- **50-01** closes two wave-37 RISKs that were deferred and never revisited. Both
  re-verified live this session: `api/jobs.py` authorizes by role only and never uses
  the bound `current_user` — **any PM can read or download any other user's export**
  (`grep user_id workers/*.py` → 0 hits, no ownership recorded anywhere). And
  `main.py:111` serves `/metrics` with no auth, justified by a network perimeter
  nobody has confirmed.
- **50-02** is why an evaluator cloning this repo currently sees **2 red failures** on a
  clean `pytest` run. Both are environmental (Redis down → `/readyz` correctly 503s), but
  nothing in the output says so, and there is no skip guard
  (`grep skipif` on both files → 0 hits). This converts them into self-explaining skips
  without weakening a single assertion.

---

## Round 6 — final re-seal (alone, last)

| Task | Brief | Touches | Budget |
|---|---|---|---|
| **51-01** 🆕 | [`work/wave-51/01-final-reseal-and-submission.md`](wave-51/01-final-reseal-and-submission.md) | all front-door docs, `SUBMISSION.md`, `results/metrics.json` | 180 min |

Re-measures everything, reconciles every doc, refreshes the submission package, rewrites
the seal. **Writes no product code** — if it finds a bug it reports it rather than fixing
it, so its own numbers don't go stale mid-wave.

---

## Totals

**6 rounds · 10 tasks · ~19.5 agent-hours · ~13.5 h wall-clock** with the parallelism above.

---

## Standing rules for every dispatch

These are not boilerplate — each one traces to a documented failure in
[`HALL_OF_SHAME.md`](../HALL_OF_SHAME.md).

1. **One worktree per wave.** Two agents in one worktree has already corrupted this repo
   once (entry #6). One branch, one agent, one worktree.
2. **Never accept a report's numbers.** Re-run the command yourself before merging.
   Six-plus fabricated or non-reproducing reports have been caught in this project —
   including a "562 passed" that was the *collected* count, and a FINAL-CLOSE sealed on
   a green that showed 7 failures on re-run.
3. **"NOT MEASURED" is always accepted; a fabricated pass never is.** Every brief says
   this explicitly. Hold the line on it.
4. **Watch for stalls.** Double-sample `%CPU` ~5s apart (macOS single-sample is a
   lifetime average and misleads), and check real file mtimes in the worktree — not the
   log's mtime, which tee-buffering can freeze for over an hour while work continues.
   Kill and relaunch on a *different* model if genuinely stalled.
5. **One shared test DB.** `tests/conftest.py:28` hardcodes `swa_erp_test`. Two pytest
   processes against it produce spectacular fake failures (mass errors, or a suite
   "finishing" in under 10s). Check `ps aux | grep pytest` before and after any run;
   discard and retry anything with that signature.
6. **Working free models:** `mimo-v2.5-free`, `hy3-free`,
   `nemotron-3.5-lightning-free`. `deepseek-v4-flash-free` was removed from the catalog
   entirely — it is not coming back.
7. **Git may look stuck when it isn't.** The preflight hook is slow; `git commit`/`push`
   can appear to hang at 45–60s and still have succeeded. Check `git log --oneline -1`
   before retrying, and retry with a 90–100s timeout, unpiped.

---

## What is NOT in this plan, and why

- **External blockers** — server facts / deploy, Excel freeze date, client-box load test.
  All three sit with Viraj. No engineering work unblocks them; see
  [`HANDOFF.md`](../HANDOFF.md).
- **Still-open RISKs deliberately left open** — SF-6/7 import savepoints, SEC-08 document
  write roles, and the remaining ~18 repositories doing mid-request commits. Each needs
  careful TDD and is larger than a hardening pass. They stay listed as open in
  `BACKLOG.md`; wave-51 keeps them visible in the submission rather than quietly
  dropping them.
- **SEC-04/05 (time/finance read RBAC)** — re-checked 2026-08-29 and **not a defect**:
  `api/time_entries.py` already gates reads with `require_role(Role.PM)`. It is a product
  call for Viraj, not engineering work. Left alone deliberately.
- **Async export UI wiring** — Celery retries and `GET /api/jobs/{id}` all work, but no
  frontend references them. A dormant integration, not a bug. Backlogged, not scheduled.
