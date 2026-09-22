"""Property tests (hypothesis) for pure core logic.

No DB, no network — fast and deterministic. Targets: money math,
input validation, hashing, IP sanitization, reference-ID format.
"""

import re
from decimal import Decimal

from hypothesis import given, settings
from hypothesis import strategies as st

from src.backend.db.repositories.audit_repo import _sanitize_ip
from src.backend.services.idempotency_service import hash_request
from src.backend.services.invoice_service import _compute_totals
from src.backend.services.time_service import _validate_hours

REF_RE = re.compile(r"^SWA-\d{4}-[A-Z]+-\d{3,}$")


@given(
    items=st.lists(
        st.fixed_dictionaries(
            {
                "quantity": st.decimals(min_value="0.25", max_value="1000", places=2),
                "rate": st.decimals(min_value="0.01", max_value="100000", places=2),
            }
        ),
        min_size=1,
        max_size=10,
    ),
    tax_rate=st.sampled_from([Decimal("0"), Decimal("5"), Decimal("12"), Decimal("18")]),
)
@settings(max_examples=50)
def test_invoice_totals_properties(items, tax_rate):
    subtotal, tax_amount, total, gst_percent, gst_amount = _compute_totals(items, tax_rate)
    assert subtotal == sum((i["quantity"] * i["rate"] for i in items), Decimal("0"))
    assert gst_percent == tax_rate
    assert gst_amount == (subtotal * tax_rate / Decimal("100")).quantize(Decimal("0.01"))
    assert tax_amount == gst_amount
    assert total == subtotal + gst_amount
    assert total >= 0


@given(hours=st.integers(min_value=1, max_value=96).map(lambda n: Decimal(n) * Decimal("0.25")))
def test_valid_hours_accepted(hours):
    _validate_hours(hours)  # must not raise


@given(hours=st.decimals(min_value="24.25", max_value="100", places=2))
def test_hours_over_24_rejected(hours):
    import pytest
    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        _validate_hours(hours)


@given(
    method=st.sampled_from(["POST", "PATCH"]),
    path=st.sampled_from(["/api/projects/1/invoices", "/api/invoices/2/status"]),
    body=st.text(max_size=200),
)
def test_idempotency_hash_deterministic_and_sensitive(method, path, body):
    assert hash_request(method, path, body) == hash_request(method, path, body)
    assert len(hash_request(method, path, body)) == 64
    if body:
        assert hash_request(method, path, body) != hash_request(method, path, body + "x")


@given(ip=st.ip_addresses(v=4).map(str))
def test_valid_ips_preserved(ip):
    assert _sanitize_ip(ip) == ip


@given(bad=st.sampled_from(["testclient", "unknown", "", "999.999.999.999", "proxy-host", None]))
def test_invalid_ips_nulled(bad):
    assert _sanitize_ip(bad) is None
