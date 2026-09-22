"""Unit tests for karna-decisions gate (no LAYA weights)."""

from packages.karna_decisions.gate import evaluate_answers
from packages.karna_decisions.packs import PACK_IDS, get_pack, questions_for


def test_pack_ids_match_packs_and_are_boundary():
    assert set(PACK_IDS) == {
        "swa.inbound_email",
        "swa.sheet_row_risk",
        "harness.scope_guard",
        "harness.prompt_guard",
        "controlplane.admission",
    }
    for pid in PACK_IDS:
        pack = get_pack(pid)
        assert pack["id"] == pid
        qs = questions_for(pid)
        assert len(qs) >= 2
        for q in qs.values():
            assert q["type"] in ("choice", "score", "noul")


def test_high_confidence_noul_and_choice_allow():
    d = evaluate_answers(
        {
            "needs_reply": {"type": "noul", "noul": 0.95, "confidence": 0.95},
            "category": {"type": "choice", "choice": "sales", "confidence": 0.92},
        },
        pack_id="swa.inbound_email",
    )
    assert d.allow
    assert d.reasons == []


def test_low_confidence_escalates():
    d = evaluate_answers(
        {"category": {"type": "choice", "choice": "other", "confidence": 0.40}},
        pack_id="swa.inbound_email",
    )
    assert d.escalate
    assert any("low_confidence" in r for r in d.reasons)


def test_noul_gray_band_escalates():
    d = evaluate_answers(
        {"is_phishing": {"type": "noul", "noul": 0.50, "confidence": 0.50}},
        pack_id="swa.inbound_email",
    )
    assert d.escalate
    assert any("noul_gray_band" in r for r in d.reasons)


def test_empty_answers_fail_closed():
    d = evaluate_answers({}, pack_id="harness.prompt_guard")
    assert d.escalate


def test_risk_max_auto_escalates():
    d = evaluate_answers(
        {
            "risk": {"type": "score", "score": 2.8, "confidence": 0.9},
            "admit": {"type": "noul", "noul": 0.9, "confidence": 0.9},
        },
        pack_id="controlplane.admission",
        risk_max_auto=1.5,
    )
    assert d.escalate
    assert any("risk_above_auto" in r for r in d.reasons)


def test_laya_gate_boundary_rejects_unknown_pack():
    from src.backend.services.laya_gate import LayaBoundaryError, _assert_boundary

    try:
        _assert_boundary("money.invoice_approve")
    except LayaBoundaryError:
        pass
    else:
        raise AssertionError("non-boundary pack must be rejected")
    _assert_boundary("swa.inbound_email")
