# Wave-40 Task 02 — Metrics script fix (commit `9c35821`) — Verification Report

- HEAD at verification: `8652036` (`feat(security): METRICS_REQUIRE_AUTH flag, default True`)
- Verified commit: `9c358213b6199a10437b253e54dc7c61d9e672a4` — `fix(wave-40): generate_metrics.sh + EXECUTION.md commit column` (Tue Sep 15 2026)
- Worker scope: report-only, no code changes made.

## 1. What `9c35821` claimed

```
- Create scripts/generate_metrics.sh: runs pytest + vitest, parses output, writes results/metrics.json. Fails loud on error. Handles OLLAMA env pollution and macOS (no timeout command). Marks backend not_measured on timeout.
- Add Commit column to plan/EXECUTION.md (39/39 waves now have commit hash or explicit — marker)
- Add Makefile targets: metrics, verify-truth
- Create .github/workflows/docs_sync.yml
- Fix validators: handle null/not-measured values; accept — as explicit no-commit marker
- Mark historical reports metrics-exempt (stale coverage numbers at time of writing)
```

## 2. Verification — script exists, parses, wiring present

- `ls scripts/generate_metrics.sh` → exists.
- `bash -n scripts/generate_metrics.sh` → `syntax OK` (no output = parse pass under `set -euo pipefail` script).
- Script header (RAW, first 15 lines) confirms the claimed design:
```bash
#!/usr/bin/env bash
# generate_metrics.sh — run backend + frontend test suites, parse real pass/fail
# counts, emit results/metrics.json. FAILS LOUD (set -euo pipefail) if it can't
# produce real parsed JSON. Never hand-types numbers.
...
set -euo pipefail
```
- OLLAMA env hygiene (`unset OLLAMA_*`) and portable hard-timeout via `perl alarm` (macOS has no `timeout`) both present in the script body — matches commit message claims.
- `Makefile:55` → `metrics:` target exists. `.github/workflows/docs_sync.yml` → exists. `plan/EXECUTION.md` contains a Commit column (`grep -c "Commit"` → 1; header-level match).

## 3. Verification — full script output: NOT MEASURED

Running `scripts/generate_metrics.sh` executes the entire backend pytest suite (~36 min measured previously) plus the frontend vitest suite, against the shared `swa_erp_test` DB other agents were using concurrently. A full run was therefore out of scope: it would have taken longer than the task budget and risked corrupting concurrent workers' test state. Per project rule, honest NOT MEASURED — no `results/metrics.json` numbers are asserted in this report. (Note: `93696da` later regenerated `results/metrics.json` with real counts; that file is that commit's evidence, not this report's.)

## 4. Before/after

- Before `9c35821`: no automated metrics pipeline; `plan/EXECUTION.md` had no Commit column; validators choked on null/`—` values.
- After: `scripts/generate_metrics.sh` + `make metrics` / `make verify-truth` + `docs_sync.yml` + Commit column all present at HEAD (verified above).

## 5. DoD checklist

- [x] `scripts/generate_metrics.sh` exists and passes `bash -n`
- [x] Fail-loud (`set -euo pipefail`), OLLAMA hygiene, macOS portable timeout all present in script body
- [x] `make metrics` target and `docs_sync.yml` workflow exist
- [x] `plan/EXECUTION.md` has Commit column
- [ ] End-to-end script run producing `results/metrics.json` — NOT MEASURED + reason (full-suite runtime + shared DB contention; see §3)

## 6. Residual risks

1. Script correctness under real timeout/failure paths (e.g. `not_measured` fallback) is unexercised by this report — the owning agent should paste one real `make metrics` run.
2. `results/metrics.json` currently in the tree was written by a different commit (`93696da`); do not attribute its numbers to `9c35821`.
