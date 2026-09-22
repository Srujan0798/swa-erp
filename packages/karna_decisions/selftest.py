"""Pure-logic self-test for karna-decisions gate (no model weights).

Run: .venv-laya/bin/python -m packages.karna_decisions.selftest
"""

from __future__ import annotations

import sys

from packages.karna_decisions.gate import evaluate_answers
from packages.karna_decisions.packs import PACK_IDS, get_pack, questions_for


def _ok(cond: bool, msg: str, failures: list[str]) -> None:
    if not cond:
        failures.append(msg)


def main() -> int:
    failures: list[str] = []

    # Packs load and are boundary-only.
    for pid in PACK_IDS:
        pack = get_pack(pid)
        _ok(pack["id"] == pid, f"pack id mismatch {pid}", failures)
        qs = questions_for(pid)
        _ok(len(qs) >= 2, f"{pid}: too few questions", failures)
        for qid, q in qs.items():
            _ok(q.get("type") in ("choice", "score", "noul"), f"{pid}/{qid}: bad type", failures)
            if q["type"] == "choice":
                _ok(bool(q.get("criteria")), f"{pid}/{qid}: choice needs criteria", failures)
            if q["type"] == "score":
                _ok(len(q.get("criteria") or []) >= 2, f"{pid}/{qid}: score needs legend", failures)

    # High confidence noul (clear true/false) → allow.
    d = evaluate_answers(
        {
            "needs_reply": {"type": "noul", "noul": 0.95, "confidence": 0.95},
            "category": {
                "type": "choice",
                "choice": "sales",
                "confidence": 0.92,
                "probabilities": {"sales": 0.92, "other": 0.08},
            },
        },
        pack_id="swa.inbound_email",
        pack_version=1,
    )
    _ok(d.allow, f"expected allow, got {d.reasons}", failures)

    # Low confidence choice → escalate.
    d = evaluate_answers(
        {"category": {"type": "choice", "choice": "other", "confidence": 0.40}},
        pack_id="swa.inbound_email",
    )
    _ok(
        d.escalate and any("low_confidence" in r for r in d.reasons),
        "low conf should escalate",
        failures,
    )

    # Noul gray band → escalate even if confidence field is high.
    d = evaluate_answers(
        {"is_phishing": {"type": "noul", "noul": 0.50, "confidence": 0.50}},
        pack_id="swa.inbound_email",
    )
    _ok(
        d.escalate and any("noul_gray_band" in r for r in d.reasons),
        "gray band should escalate",
        failures,
    )

    # Empty answers → fail closed.
    d = evaluate_answers({}, pack_id="harness.prompt_guard")
    _ok(d.escalate, "empty answers must escalate", failures)

    # risk_max_auto: score above threshold escalates.
    d = evaluate_answers(
        {
            "risk": {"type": "score", "score": 2.8, "confidence": 0.9},
            "admit": {"type": "noul", "noul": 0.9, "confidence": 0.9},
        },
        pack_id="controlplane.admission",
        risk_max_auto=1.5,
    )
    _ok(
        d.escalate and any("risk_above_auto" in r for r in d.reasons),
        "risk overflow should escalate",
        failures,
    )

    if failures:
        print("FAIL")
        for f in failures:
            print(" -", f)
        return 1
    print(f"OK packs={len(PACK_IDS)} gate_rules=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
