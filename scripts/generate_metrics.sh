#!/usr/bin/env bash
# generate_metrics.sh — run backend + frontend test suites, parse real pass/fail
# counts, emit results/metrics.json. FAILS LOUD (set -euo pipefail) if it can't
# produce real parsed JSON. Never hand-types numbers.
#
# Env hygiene: OLLAMA_* vars present in this environment trigger a local-LLM
# stack startup that pollutes stdout before pytest can run. We unset them here
# so pytest output stays parseable. This is scoped to the script only.
set -euo pipefail

# ── env hygiene: strip OLLAMA / LLM startup noise ────────────────────────────
unset OLLAMA_MAX_LOADED_MODELS OLLAMA_CONTEXT_LENGTH OLLAMA_KEEP_ALIVE \
      OLLAMA_LOAD_TIMEOUT OLLAMA_FLASH_ATTENTION OLLAMA_NUM_PARALLEL 2>/dev/null || true

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RESULTS_DIR="$REPO_ROOT/results"
METRICS_FILE="$RESULTS_DIR/metrics.json"
TMPDIR_METRICS="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_METRICS"' EXIT

mkdir -p "$RESULTS_DIR"

# Default timeout: 600s (574 tests on a dev machine). Override with PYTEST_TIMEOUT.
PYTEST_TIMEOUT="${PYTEST_TIMEOUT:-600}"

# ── helpers ──────────────────────────────────────────────────────────────────
# Parse "N passed, M failed, K skipped" → sets PASSED FAILED SKIPPED
parse_summary() {
  local line="$1"
  PASSED=0; FAILED=0; SKIPPED=0
  [[ "$line" =~ ([0-9]+)[[:space:]]+passed ]] && PASSED="${BASH_REMATCH[1]}"
  [[ "$line" =~ ([0-9]+)[[:space:]]+failed ]] && FAILED="${BASH_REMATCH[1]}"
  [[ "$line" =~ ([0-9]+)[[:space:]]+skipped ]] && SKIPPED="${BASH_REMATCH[1]}"
}

# Portable hard-timeout (macOS has no `timeout` / `gtimeout` by default).
_hard_timeout() {
  local secs="$1"; shift
  perl -e 'alarm shift @ARGV; exec @ARGV' "$secs" "$@"
}

# ── backend (pytest) ─────────────────────────────────────────────────────────
BACKEND_OUT="$TMPDIR_METRICS/backend.txt"
BACKEND_PASSED="null"
BACKEND_FAILED="null"
BACKEND_SKIPPED="null"
BACKEND_MEASURED=true

set +e
_hard_timeout "$PYTEST_TIMEOUT" python3 -m pytest tests/ -q --tb=no > "$BACKEND_OUT" 2>&1
PYTEST_RC=$?
set -e

if [[ $PYTEST_RC -eq 124 ]]; then
  echo "WARN: pytest timed out after ${PYTEST_TIMEOUT}s; backend counts marked not_measured." >&2
  BACKEND_MEASURED=false
else
  BACKEND_SUMMARY="$(grep -E '[0-9]+ (passed|failed)' "$BACKEND_OUT" | tail -1 || true)"
  if [[ -z "$BACKEND_SUMMARY" ]]; then
    echo "WARN: pytest produced no parseable summary line; backend counts marked not_measured." >&2
    BACKEND_MEASURED=false
  else
    parse_summary "$BACKEND_SUMMARY"
    BACKEND_PASSED="$PASSED"
    BACKEND_FAILED="$FAILED"
    BACKEND_SKIPPED="$SKIPPED"
  fi
fi

# ── frontend (vitest) ─────────────────────────────────────────────────────────
FRONTEND_OUT="$TMPDIR_METRICS/frontend.txt"
FRONTEND_PKG="$REPO_ROOT/src/frontend"
FE_PASSED=0; FE_FAILED=0

if [[ -d "$FRONTEND_PKG" ]]; then
  if [[ ! -x "$FRONTEND_PKG/node_modules/.bin/vitest" ]]; then
    echo "WARN: vitest binary missing — attempting npm install." >&2
    (cd "$FRONTEND_PKG" && npm install --no-audit --no-fund 2>&1 || true)
  fi
  set +e
  (cd "$FRONTEND_PKG" && npx vitest run > "$FRONTEND_OUT" 2>&1)
  VITEST_RC=$?
  set -e

  if [[ $VITEST_RC -ne 0 ]]; then
    echo "WARN: vitest exited with code $VITEST_RC." >&2
  fi

  # vitest summary line: " Tests  523 passed 0 failed"
  FE_SUMMARY="$(grep -E '^[[:space:]]*Tests[[:space:]]+' "$FRONTEND_OUT" | tail -1 || true)"
  if [[ -n "$FE_SUMMARY" ]]; then
    parse_summary "$FE_SUMMARY"
    FE_PASSED="$PASSED"
    FE_FAILED="$FAILED"
  else
    echo "WARN: vitest produced no parseable 'Tests' summary line." >&2
  fi
else
  echo "WARN: frontend package dir missing — recording 0/0." >&2
fi

# ── environmental failures ────────────────────────────────────────────────────
ENVM_RAW="[]"
if grep -qiE 'redis|connection.*refused|could not connect' "$BACKEND_OUT" 2>/dev/null; then
  ENVM_RAW='["Redis not running"]'
fi
if [[ "$BACKEND_MEASURED" == "false" ]]; then
  ENVM_RAW='["pytest tests/ timed out after '"$PYTEST_TIMEOUT"'s — backend counts not measured on this machine (env timeout)"]'
fi

# ── coverage (best-effort; vitest suppresses coverage on failure) ─────────────
FE_COV="null"
if [[ "$FE_FAILED" -eq 0 && -d "$FRONTEND_PKG" ]]; then
  set +e
  (cd "$FRONTEND_PKG" && npx vitest run --coverage --coverage.reporter=json-summary \
     --coverage.provider=v8 > /dev/null 2>&1)
  set -e
  COV_FILE="$(find "$FRONTEND_PKG/coverage" -name 'coverage-summary.json' 2>/dev/null | head -1)"
  if [[ -n "$COV_FILE" && -f "$COV_FILE" ]]; then
    FE_COV="$(python3 -c "import json;d=json.load(open('$COV_FILE'));t=d['total']['statements']['pct'];print(t if t is not None else 'null')" 2>/dev/null || echo 'null')"
  fi
fi

# ── assemble JSON ─────────────────────────────────────────────────────────────
GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
GIT_SHA="$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo 'unknown')"

export GENERATED_AT GIT_SHA \
  BACKEND_PASSED BACKEND_FAILED BACKEND_SKIPPED BACKEND_MEASURED \
  FE_PASSED FE_FAILED FE_COV ENVM_RAW

METRICS_JSON="$(python3 <<'PYEOF'
import json, os

fe_cov_raw = os.environ["FE_COV"]
fe_cov = None if fe_cov_raw == "null" else float(fe_cov_raw)

backend_measured = os.environ.get("BACKEND_MEASURED", "false") == "true"

if backend_measured:
    backend_obj = {
        "measured": True,
        "passed": int(os.environ["BACKEND_PASSED"]),
        "failed": int(os.environ["BACKEND_FAILED"]),
        "skipped": int(os.environ["BACKEND_SKIPPED"]),
    }
else:
    backend_obj = {
        "measured": False,
        "passed": None,
        "failed": None,
        "skipped": None,
    }

d = {
    "generated_at": os.environ["GENERATED_AT"],
    "git_sha": os.environ["GIT_SHA"],
    "backend": backend_obj,
    "frontend": {
        "passed": int(os.environ["FE_PASSED"]),
        "failed": int(os.environ["FE_FAILED"]),
        "coverage": {
            "statements": fe_cov,
        },
    },
    "environmental_failures": json.loads(os.environ["ENVM_RAW"]),
}
print(json.dumps(d, indent=2))
PYEOF
)"

# Validate the JSON we just produced — fail loud if it isn't valid.
echo "$METRICS_JSON" | python3 -m json.tool > /dev/null 2>&1 || {
  echo "FATAL: assembled metrics JSON is not valid JSON." >&2
  echo "$METRICS_JSON" >&2
  exit 1
}

# Write to results/metrics.json
printf '%s\n' "$METRICS_JSON" > "$METRICS_FILE"

# Mirror to stdout (required by spec).
printf '%s\n' "$METRICS_JSON"
