"""swa-erp boundary adapter for shared karna-decisions System-1 gates.

This is the ONLY module under `src/backend/services/` allowed to import `laya`.
Never call LAYA on money, identity, RBAC, or GST paths — packs are boundary-only
(see packages/karna_decisions/packs.py and docs/decisions/0005).

Router is always constructed with preload=True (standing rule).
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from packages.karna_decisions.gate import (
    DEFAULT_CONF_THRESHOLD,
    DEFAULT_NOUL_GRAY_HI,
    DEFAULT_NOUL_GRAY_LO,
    GateDecision,
    evaluate_answers,
)
from packages.karna_decisions.packs import PACK_IDS, get_pack

logger = logging.getLogger(__name__)

_router: Any = None
_router_lock = threading.Lock()


class LayaBoundaryError(ValueError):
    """Raised when a caller tries to use LAYA outside the allowed boundary."""


def _get_router():
    """Lazy singleton: Router(preload=True) — never default max_loaded=1."""
    global _router
    if _router is not None:
        return _router
    with _router_lock:
        if _router is not None:
            return _router
        from laya import Router

        logger.info("laya_gate: constructing Router(preload=True)")
        _router = Router(preload=True)
        return _router


def _assert_boundary(pack_id: str) -> None:
    if pack_id not in PACK_IDS:
        raise LayaBoundaryError(
            f"pack {pack_id!r} is not on the boundary allow-list; "
            f"allowed: {', '.join(PACK_IDS)}. "
            "LAYA must never gate money, ID, RBAC, or GST paths."
        )


def decide(
    pack_id: str,
    state: Any,
    *,
    conf_threshold: float = DEFAULT_CONF_THRESHOLD,
    noul_gray_lo: float = DEFAULT_NOUL_GRAY_LO,
    noul_gray_hi: float = DEFAULT_NOUL_GRAY_HI,
    risk_max_auto: float | None = None,
) -> GateDecision:
    """Run one boundary pack. Returns GateDecision; escalate → human review."""
    _assert_boundary(pack_id)
    pack = get_pack(pack_id)
    router = _get_router()
    result = router.predict(state, pack["questions"])
    return evaluate_answers(
        result.get("answers") or {},
        routing=result.get("routing") or {},
        pack_id=pack["id"],
        pack_version=pack["version"],
        conf_threshold=conf_threshold,
        noul_gray_lo=noul_gray_lo,
        noul_gray_hi=noul_gray_hi,
        risk_max_auto=risk_max_auto,
    )


def warmup(pack_ids: tuple[str, ...] | list[str] | None = None) -> list[str]:
    """Preload router (idempotent). Returns pack ids confirmed on boundary."""
    ids = list(pack_ids or PACK_IDS)
    for pid in ids:
        _assert_boundary(pid)
    _get_router()
    return ids


__all__ = [
    "DEFAULT_CONF_THRESHOLD",
    "DEFAULT_NOUL_GRAY_HI",
    "DEFAULT_NOUL_GRAY_LO",
    "GateDecision",
    "LayaBoundaryError",
    "decide",
    "warmup",
]
