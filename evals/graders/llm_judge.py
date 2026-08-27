"""
evals/graders/llm_judge.py — rubric-based grading for subjective evaluation outcomes.

Used ONLY for what the code-based grader cannot judge deterministically: UX clarity,
narrative coherence of audit logs, phrasing of error messages a human reads.

The rubric is explicit and enumerated below. Each criterion is scored 0–2:
  0 = not present / failing
  1 = partial / unclear
  2 = fully satisfactory

A task using the LLM judge must define its own rubric block in
evals/tasks/*.task.yaml (under the `llm_rubric` key). This module provides:
  - LLM_RUBRIC: the default rubric (overridable per-task)
  - score_transcript(transcript_json, rubric) -> dict
  - format_report(scores) -> str

We do NOT call an LLM from here. This module scores pre-collected transcripts
against the rubric. The actual LLM call (if needed) happens in an external reviewer step
or the evals CI job — keeping this importable without network/secrets.
This keeps the grader deterministic and offline-testable.
"""
from __future__ import annotations

from typing import Any


# Default rubric — each criterion scored 0/1/2 by a human or external LLM call.
DEFAULT_RUBRIC: list[dict[str, Any]] = [
    {
        "id": "clarity",
        "name": "Response clarity",
        "description": "The system's final response or error message is unambiguous and actionable for the end user.",
        "score_0": "Message is confusing, contradictory, or missing.",
        "score_2": "Message is clear, uses client-domain language, and tells the user what to do next.",
    },
    {
        "id": "audit_trail",
        "name": "Audit trail completeness",
        "description": "Every user-facing mutation produced an audit_log entry with before/after JSON.",
        "score_0": "No audit entry, or before/after is empty.",
        "score_2": "At least one audit entry per mutation, with non-trivial before/after.",
    },
    {
        "id": "error_helpfulness",
        "name": "Error helpfulness",
        "description": "When the system errored, the error explains the cause and lists recoverable options.",
        "score_0": "Generic 500 / stack trace exposed / no recovery hint.",
        "score_2": "Error names the violated rule, suggests a concrete fix, and uses 4xx (not 5xx).",
    },
]


def score_transcript(
    transcript: dict[str, Any],
    rubric: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Score a single trial transcript against a rubric.

    Args:
        transcript: dict from evals/transcripts/<id>.trial-N.json
        rubric: optional override of DEFAULT_RUBRIC

    Returns:
        dict with per-criterion scores, total, and pass/fail (threshold >= 2*len(rubric))
    """
    rubric = rubric or DEFAULT_RUBRIC
    # In a real LLM-judge setup, this would call the model here.
    # We leave the scoring to the human or an external LLM step; here we just
    # validate the transcript has the expected structure and return a placeholder
    # that a human/LLM step fills in via the 'scores' key.
    scores: dict[str, int] = {}
    notes: dict[str, str] = {}

    # If the transcript already has LLM-assigned scores (from an external step),
    # use them; otherwise mark as "pending human / external LLM".
    llm_scores = transcript.get("_llm_scores", {})
    for crit in rubric:
        key = crit["id"]
        if key in llm_scores:
            scores[key] = llm_scores[key]
            notes[key] = transcript.get("_llm_notes", {}).get(key, "")
        else:
            scores[key] = -1  # pending
            notes[key] = "pending human / external LLM review"

    total = sum(v for v in scores.values() if v >= 0)
    pending = any(v < 0 for v in scores.values())

    passed = (not pending) and (total >= 2 * len(rubric))

    return {
        "scores": scores,
        "notes": notes,
        "total": total,
        "max": 2 * len(rubric),
        "passed": passed,
        "pending": pending,
    }


def format_report(scores: dict[str, Any]) -> str:
    """Format an LLM-judge score dict into a human-readable string."""
    lines = ["## LLM Judge Report", ""]
    for crit in DEFAULT_RUBRIC:
        key = crit["id"]
        s = scores["scores"].get(key, -1)
        n = scores["notes"].get(key, "")
        if s < 0:
            lines.append(f"- **{crit['name']}**: _pending review_ — {n}")
        else:
            lines.append(f"- **{crit['name']}**: {s}/2 — {n}")
    lines.append("")
    lines.append(f"**Total**: {scores['total']}/{scores['max']}")
    lines.append(f"**Passed**: {scores['passed']}")
    if scores["pending"]:
        lines.append("_(pending: requires human or external LLM scoring)_")
    return "\n".join(lines)
