#!/usr/bin/env python3
"""
evals/run_evals.py — the eval runner.

Runs the wave-43 eval tests (evals/wave_43_evals.py) for N trials, captures
transcripts per trial, and emits:
  - evals/transcripts/<task_id>.trial-<N>.json
  - evals/outcomes/pass@k.json
  - prints a summary table to stdout.

The actual test logic lives in evals/wave_43_evals.py (pytest-based, using the
project's conftest.py fixtures). This runner invokes pytest with -p no:xdist
to avoid parallel-execution deadlocks on the shared test DB schema.

Usage:
  python3 evals/run_evals.py --trials 3
  python3 evals/run_evals.py --task 005 --trials 1
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = Path(__file__).resolve().parent


# Task ID -> pytest node name
TASK_MAP = {
    "001-inquiry-to-client-conversion": "test_001_inquiry_to_client_conversion",
    "002-agreement-token-docref-chain": "test_002_agreement_token_docref_chain",
    "003-rbac-enforcement": "test_003_rbac_enforcement",
    "004-time-log-to-dashboard": "test_004_time_log_to_dashboard",
    "005-invoice-gst-correctness": "test_005_invoice_gst_correctness",
}


def _load_task_ids() -> list[str]:
    """Return ordered task IDs from the YAML specs."""
    tasks_dir = EVALS_DIR / "tasks"
    ids = []
    for f in sorted(tasks_dir.glob("*.task.yaml")):
        import yaml
        with open(f) as fh:
            t = yaml.safe_load(fh)
        ids.append(t["id"])
    return ids


def _run_pytest(task_id: str, trial: int) -> dict:
    """Run one eval task as a pytest test. Returns result dict."""
    test_name = TASK_MAP.get(task_id)
    if not test_name:
        return {
            "task_id": task_id,
            "passed": False,
            "error": f"No pytest test mapped for {task_id}",
            "transcript": [],
            "evidence": "",
        }

    node_id = f"evals/wave_43_evals.py::{test_name}"

    env = dict(os.environ)
    env.setdefault("DATABASE_URL", "postgresql://swa:swa@localhost:5432/swa_erp_test")
    env.setdefault("SECRET_KEY", "test-secret-key")
    env.setdefault("DISABLE_AUTH_RATE_LIMIT", "1")
    env.setdefault("APP_ENV", "test")

    cmd = [
        sys.executable, "-m", "pytest",
        node_id,
        "-v",
        "--confcutdir=tests",
        "-p", "tests.conftest",
        "--timeout=30",
        "-p", "no:xdist",
        "--tb=short",
        "--no-header",
        "-rA",
        "-q",
    ]

    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )

    passed = result.returncode == 0

    # Extract assertion / error from stderr+stdout
    combined = result.stdout + result.stderr
    evidence_lines = []
    for line in combined.split("\n"):
        if line.strip().startswith("assert") or "AssertionError" in line or "ERROR" in line or "FAILED" in line:
            evidence_lines.append(line.strip())

    evidence = "\n".join(evidence_lines[:20]) if evidence_lines else combined[-1500:]

    return {
        "task_id": task_id,
        "passed": passed,
        "evidence": evidence if not passed else "All assertions passed",
        "transcript": [{"pytest_output": combined[:3000]}],
        "returncode": result.returncode,
    }


def write_transcript(task_id: str, trial: int, result: dict) -> None:
    out_dir = EVALS_DIR / "transcripts"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"{task_id}.trial-{trial}.json"
    with open(path, "w") as fh:
        json.dump(result, fh, indent=2, default=str)


def write_outcomes(all_results: list[dict]) -> list[dict]:
    out_path = EVALS_DIR / "outcomes" / "pass@k.json"
    out_path.parent.mkdir(exist_ok=True)

    tasks: dict[str, dict] = {}
    for r in all_results:
        tid = r["task_id"]
        if tid not in tasks:
            tasks[tid] = {"trials": 0, "passes": 0}
        tasks[tid]["trials"] += 1
        if r["passed"]:
            tasks[tid]["passes"] += 1

    summary = []
    for tid, stats in tasks.items():
        ratio = stats["passes"] / stats["trials"] if stats["trials"] > 0 else 0
        summary.append({
            "task_id": tid,
            "pass@k": round(ratio, 3),
            "pass^k": round(ratio, 3),
            "passes": stats["passes"],
            "trials": stats["trials"],
        })

    with open(out_path, "w") as fh:
        json.dump(summary, fh, indent=2, default=str)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Run wave-43 evals")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--task", type=str, default=None)
    args = parser.parse_args()

    task_ids = _load_task_ids()
    if args.task:
        task_ids = [t for t in task_ids if t.startswith(args.task)]

    if not task_ids:
        print("No tasks found in evals/tasks/")
        sys.exit(1)

    print(f"Running {len(task_ids)} eval tasks x {args.trials} trials each")
    print(f"DB: {os.environ.get('DATABASE_URL', 'postgresql://swa:swa@localhost:5432/swa_erp_test')}\n")

    all_results = []
    summary_lines = []

    for task_id in task_ids:
        task_passes = 0
        task_trials = 0
        for trial in range(1, args.trials + 1):
            result = _run_pytest(task_id, trial)
            task_trials += 1
            if result["passed"]:
                task_passes += 1

            write_transcript(task_id, trial, result)
            status = "PASS" if result["passed"] else "FAIL"
            print(f"  [{task_id}] trial {trial}/{args.trials}: {status}")
            if not result["passed"]:
                print(f"    evidence: {result.get('evidence', 'N/A')[:600]}")
            all_results.append(result)

        ratio = task_passes / task_trials if task_trials > 0 else 0
        line = f"{task_id}: {task_passes}/{task_trials} = pass@k {ratio:.0%}, pass^k {ratio:.0%}"
        summary_lines.append(line)

    print("\n" + "=" * 70)
    print("EVAL SUMMARY")
    print("=" * 70)
    for line in summary_lines:
        print(f"  {line}")
    print("=" * 70)

    summary = write_outcomes(all_results)
    print(f"\nOutcomes written to evals/outcomes/pass@k.json")
    overall = sum(1 for s in summary if s["passes"] == s["trials"]) / len(summary) if summary else 0
    print(f"\nOverall deterministic pass rate: {overall:.0%}")
    for s in summary:
        marker = "PASS" if s["pass@k"] == 1.0 else ("WARN" if s["pass@k"] > 0 else "FAIL")
        print(f"  [{marker}] {s['task_id']}: pass@k={s['pass@k']:.0%} pass^k={s['pass^k']:.0%} ({s['passes']}/{s['trials']})")


if __name__ == "__main__":
    main()
