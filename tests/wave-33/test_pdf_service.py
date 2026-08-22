"""Wave 33 — pdf_service coverage (REDO).

Real behavior tests for src.backend.services.pdf_service:
PDF generation, metadata rendering, line items, totals, terms, signature
block, and the date/decimal formatting helpers.
"""
from __future__ import annotations

import io
from datetime import datetime
from decimal import Decimal

from pypdf import PdfReader

from src.backend.services.pdf_service import (
    _fmt_date,
    _fmt_decimal,
    generate_quote_pdf,
)

SAMPLE_QUOTE = {
    "id": "abc12345",
    "code": "Q-2026-001",
    "created_at": "2026-01-15",
    "valid_until": "2026-02-14",
    "project_name": "Green Tower",
    "client_name": "Acme Corp",
    "status": "pending_approval",
    "items": [
        {
            "line_number": 1,
            "category": "Insulation",
            "description": "Rockwool slab 50mm",
            "unit": "sqm",
            "quantity": 100,
            "rate": Decimal("150.50"),
            "amount": Decimal("15050.00"),
        },
        {
            "line_number": 2,
            "category": "Labour",
            "description": "Installation labour",
            "unit": "day",
            "quantity": 5,
            "rate": Decimal("2000.00"),
            "amount": Decimal("10000.00"),
        },
    ],
    "subtotal": Decimal("25050.00"),
    "markup_percent": Decimal("10"),
    "markup_amount": Decimal("2505.00"),
    "tax_percent": Decimal("18"),
    "tax_amount": Decimal("4959.90"),
    "total_amount": Decimal("32514.90"),
    "terms": "Net 30 days from invoice. GST extra as applicable.",
}


def _read_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    assert len(reader.pages) == 1
    return reader.pages[0].extract_text()


def test_generate_quote_pdf_returns_valid_pdf_bytes():
    out = generate_quote_pdf(SAMPLE_QUOTE)
    assert out.startswith(b"%PDF")
    assert b"%%EOF" in out


def test_pdf_contains_company_and_document_title():
    text = _read_pdf(generate_quote_pdf(SAMPLE_QUOTE))
    assert "SWA Consultancy Pvt. Ltd." in text
    assert "Quotation" in text


def test_meta_section_renders_all_fields():
    text = _read_pdf(generate_quote_pdf(SAMPLE_QUOTE))
    assert "Q-2026-001" in text
    assert "Project: Green Tower" in text
    assert "Client: Acme Corp" in text
    assert "Status: Pending Approval" in text
    assert "Valid Until: 2026-02-14" in text


def test_line_items_table_renders_rows():
    text = _read_pdf(generate_quote_pdf(SAMPLE_QUOTE))
    assert "Category" in text
    assert "Insulation" in text
    assert "150.50" in text
    assert "15,050.00" in text
    assert "2,000.00" in text
    assert "Installation labour" in text


def test_totals_section_renders_breakdown():
    text = _read_pdf(generate_quote_pdf(SAMPLE_QUOTE))
    assert "Subtotal: 25,050.00" in text
    assert "Markup (10%): 2,505.00" in text
    assert "Tax (18%): 4,959.90" in text
    assert "Total: 32,514.90" in text


def test_terms_section_renders_when_present():
    text = _read_pdf(generate_quote_pdf(SAMPLE_QUOTE))
    assert "Terms & Conditions:" in text
    assert "Net 30 days from invoice" in text


def test_terms_omitted_when_absent():
    quote = dict(SAMPLE_QUOTE, terms=None)
    text = _read_pdf(generate_quote_pdf(quote))
    assert "Terms & Conditions:" not in text


def test_signature_block_present():
    text = _read_pdf(generate_quote_pdf(SAMPLE_QUOTE))
    assert "Authorized Signatory" in text
    assert "Client Acknowledgment" in text
    assert "Client Signature & Date" in text


def test_empty_items_and_minimal_quote_does_not_crash():
    quote = {"id": "abcdef12", "created_at": "2026-01-01", "items": []}
    out = generate_quote_pdf(quote)
    text = _read_pdf(out)
    assert "abcdef12" in text
    assert "Subtotal: 0.00" in text
    assert "Total: 0.00" in text


def test_item_with_blank_fields_renders_defaults():
    quote = dict(SAMPLE_QUOTE)
    quote["items"] = [{"description": "sparse row"}]
    quote["code"] = None
    text = _read_pdf(generate_quote_pdf(quote))
    assert "sparse row" in text


def test_string_and_numeric_totals_both_formatted():
    quote = dict(
        SAMPLE_QUOTE,
        subtotal="1234.5",
        markup_amount=12.34,
        tax_amount="100",
        total_amount=Decimal("1346.84"),
    )
    text = _read_pdf(generate_quote_pdf(quote))
    assert "Subtotal: 1,234.50" in text
    assert "Total: 1,346.84" in text


def test_fmt_date_variants():
    assert _fmt_date(None) == ""
    assert _fmt_date("2026-01-15") == "2026-01-15"
    assert _fmt_date(datetime(2026, 1, 15, 12, 30)) == "15 Jan 2026"


def test_fmt_decimal_variants():
    assert _fmt_decimal(None) == "0.00"
    assert _fmt_decimal("0") == "0.00"
    assert _fmt_decimal(1234.5) == "1,234.50"
    assert _fmt_decimal(Decimal("9999.99")) == "9,999.99"
    assert _fmt_decimal("1000") == "1,000.00"