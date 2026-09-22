"""Escalation gate over LAYA system-one answers.

Rules (standing):
- Any answer with confidence < DEFAULT_CONF_THRESHOLD → escalate.
- Any noul in the gray band [DEFAULT_NOUL_GRAY_LO, DEFAULT_NOUL_GRAY_HI] → escalate
  (P(true) near 0.5 is indecision, not a decision).
- Errors / missing answers → escalate (fail closed).
- Gate never auto-approves money, identity, RBAC, GST, or irreversible actions —
  those packs must not be registered; admission pack still escalates high risk.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

DEFAULT_CONF_THRESHOLD = 0.70
DEFAULT_NOUL_GRAY_LO = 0.40
DEFAULT_NOUL_GRAY_HI = 0.60


@dataclass
class GateDecision:
    """Outcome of evaluate_answers(). escalate=True means human required."""

    escalate: bool
    reasons: list[str] = field(default_factory=list)
    answers: dict[str, Any] = field(default_factory=dict)
    routing: dict[str, Any] = field(default_factory=dict)
    pack_id: str = ""
    pack_version: int = 0
    min_confidence: float | None = None

    @property
    def allow(self) -> bool:
        return not self.escalate

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["allow"] = self.allow
        return d


def _conf(ans: dict[str, Any]) -> float | None:
    c = ans.get("confidence")
    if c is None:
        return None
    try:
        return float(c)
    except (TypeError, ValueError):
        return None


def evaluate_answers(
    answers: dict[str, Any],
    *,
    routing: dict[str, Any] | None = None,
    pack_id: str = "",
    pack_version: int = 0,
    conf_threshold: float = DEFAULT_CONF_THRESHOLD,
    noul_gray_lo: float = DEFAULT_NOUL_GRAY_LO,
    noul_gray_hi: float = DEFAULT_NOUL_GRAY_HI,
    risk_max_auto: float | None = None,
) -> GateDecision:
    """Apply confidence + noul gray-band rules. Fail closed on missing data."""
    reasons: list[str] = []
    confs: list[float] = []

    if not answers:
        return GateDecision(
            escalate=True,
            reasons=["no_answers: gate fails closed"],
            routing=dict(routing or {}),
            pack_id=pack_id,
            pack_version=pack_version,
        )

    for qid, ans in answers.items():
        if not isinstance(ans, dict):
            reasons.append(f"{qid}:malformed_answer")
            continue

        c = _conf(ans)
        if c is None:
            reasons.append(f"{qid}:missing_confidence")
        else:
            confs.append(c)
            if c < conf_threshold:
                reasons.append(f"{qid}:low_confidence({c:.3f}<{conf_threshold})")

        if ans.get("type") == "noul" or "noul" in ans:
            p_true = ans.get("noul")
            if p_true is None:
                reasons.append(f"{qid}:missing_noul")
            else:
                try:
                    p = float(p_true)
                except (TypeError, ValueError):
                    reasons.append(f"{qid}:bad_noul")
                else:
                    if noul_gray_lo <= p <= noul_gray_hi:
                        reasons.append(f"{qid}:noul_gray_band({p:.3f})")

        if risk_max_auto is not None and ans.get("type") == "score":
            sc = ans.get("score")
            if sc is not None:
                try:
                    if float(sc) > float(risk_max_auto):
                        reasons.append(f"{qid}:risk_above_auto({float(sc):.3f}>{risk_max_auto})")
                except (TypeError, ValueError):
                    reasons.append(f"{qid}:bad_score")

    return GateDecision(
        escalate=bool(reasons),
        reasons=reasons,
        answers=answers,
        routing=dict(routing or {}),
        pack_id=pack_id,
        pack_version=pack_version,
        min_confidence=min(confs) if confs else None,
    )
