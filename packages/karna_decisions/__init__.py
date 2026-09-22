"""karna-decisions — shared System-1 boundary gates (LAYA-backed).

One package for every project. Never import `laya` from application services
except through `src.backend.services.laya_gate` (swa-erp boundary rule).
"""

from packages.karna_decisions.gate import (
    DEFAULT_CONF_THRESHOLD,
    DEFAULT_NOUL_GRAY_HI,
    DEFAULT_NOUL_GRAY_LO,
    GateDecision,
    evaluate_answers,
)
from packages.karna_decisions.packs import (
    PACK_IDS,
    get_pack,
    questions_for,
)

__all__ = [
    "DEFAULT_CONF_THRESHOLD",
    "DEFAULT_NOUL_GRAY_HI",
    "DEFAULT_NOUL_GRAY_LO",
    "PACK_IDS",
    "GateDecision",
    "evaluate_answers",
    "get_pack",
    "questions_for",
]
