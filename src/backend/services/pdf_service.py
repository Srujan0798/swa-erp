from datetime import datetime
from decimal import Decimal

from fpdf import FPDF


class QuotePDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "SWA Consultancy Pvt. Ltd.", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, "Quotation", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(4)


class QuotePDFBuilder:
    def __init__(self, quote_data: dict) -> None:
        self.quote = quote_data
        self.pdf = QuotePDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def build(self) -> bytes:
        self.pdf.add_page()
        self._meta_section()
        self._line_items_table()
        self._totals_section()
        self._terms_section()
        self._signature_block()
        return bytes(self.pdf.output())

    def _meta_section(self) -> None:
        q = self.quote
        self.pdf.set_font("Helvetica", "B", 10)
        col_w = 45
        val_w = 130

        meta = [
            ("Quote #:", q.get("code") or str(q["id"])[:8]),
            ("Date:", _fmt_date(q["created_at"])),
            ("Valid Until:", _fmt_date(q.get("valid_until")) or "N/A"),
            ("Project:", q.get("project_name") or "N/A"),
            ("Client:", q.get("client_name") or "N/A"),
            ("Status:", q.get("status", "").replace("_", " ").title()),
        ]

        for label, value in meta:
            self.pdf.set_font("Helvetica", "B", 10)
            self.pdf.cell(col_w, 7, label)
            self.pdf.set_font("Helvetica", "", 10)
            self.pdf.cell(val_w, 7, str(value), new_x="LMARGIN", new_y="NEXT")

        self.pdf.ln(4)

    def _line_items_table(self) -> None:
        self.pdf.set_font("Helvetica", "B", 9)
        headers = ["#", "Category", "Description", "Unit", "Qty", "Rate", "Amount"]
        widths = [10, 30, 55, 18, 20, 25, 25]

        self.pdf.set_fill_color(220, 220, 220)
        for i, h in enumerate(headers):
            self.pdf.cell(widths[i], 7, h, border=1, fill=True, align="C")
        self.pdf.ln()

        self.pdf.set_font("Helvetica", "", 8)
        for item in self.quote.get("items", []):
            row = [
                str(item.get("line_number", "")),
                (item.get("category") or "")[:15],
                (item.get("description") or "")[:30],
                item.get("unit", ""),
                str(item.get("quantity", "")),
                _fmt_decimal(item.get("rate", Decimal("0"))),
                _fmt_decimal(item.get("amount", Decimal("0"))),
            ]
            for i, val in enumerate(row):
                align = "R" if i >= 4 else "L"
                self.pdf.cell(widths[i], 6, val, border=1, align=align)
            self.pdf.ln()

    def _totals_section(self) -> None:
        self.pdf.ln(4)
        self.pdf.set_font("Helvetica", "B", 10)
        x_start = 120
        self.pdf.set_x(x_start)

        rows = [
            ("Subtotal:", _fmt_decimal(self.quote.get("subtotal", Decimal("0")))),
            (
                f"Markup ({self.quote.get('markup_percent', Decimal('0'))}%):",
                _fmt_decimal(self.quote.get("markup_amount", Decimal("0"))),
            ),
            (
                f"Tax ({self.quote.get('tax_percent', Decimal('0'))}%):",
                _fmt_decimal(self.quote.get("tax_amount", Decimal("0"))),
            ),
        ]

        for label, value in rows:
            self.pdf.set_x(x_start)
            self.pdf.cell(50, 7, label, align="R")
            self.pdf.cell(30, 7, value, align="R", new_x="LMARGIN", new_y="NEXT")

        self.pdf.set_font("Helvetica", "B", 11)
        self.pdf.set_x(x_start)
        self.pdf.cell(50, 8, "Total:", align="R")
        self.pdf.cell(30, 8, _fmt_decimal(self.quote.get("total_amount", Decimal("0"))), align="R", new_x="LMARGIN", new_y="NEXT")

    def _terms_section(self) -> None:
        self.pdf.ln(6)
        terms = self.quote.get("terms")
        if terms:
            self.pdf.set_font("Helvetica", "B", 10)
            self.pdf.cell(0, 7, "Terms & Conditions:", new_x="LMARGIN", new_y="NEXT")
            self.pdf.set_font("Helvetica", "", 9)
            self.pdf.multi_cell(0, 5, terms)

    def _signature_block(self) -> None:
        self.pdf.ln(15)
        self.pdf.set_font("Helvetica", "", 10)
        self.pdf.cell(90, 6, "Authorized Signatory", align="L")
        self.pdf.cell(90, 6, "Client Acknowledgment", align="L", new_x="LMARGIN", new_y="NEXT")
        self.pdf.ln(12)
        self.pdf.cell(90, 0, "", border="T")
        self.pdf.cell(90, 0, "", border="T", new_x="LMARGIN", new_y="NEXT")
        self.pdf.set_font("Helvetica", "", 8)
        self.pdf.cell(90, 5, "SWA Consultancy Pvt. Ltd.", align="L")
        self.pdf.cell(90, 5, "Client Signature & Date", align="L", new_x="LMARGIN", new_y="NEXT")


def generate_quote_pdf(quote_data: dict) -> bytes:
    builder = QuotePDFBuilder(quote_data)
    return builder.build()


def _fmt_date(value: datetime | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value[:10]
    return value.strftime("%d %b %Y")


def _fmt_decimal(value: Decimal | float | str | None) -> str:
    if value is None:
        return "0.00"
    return f"{Decimal(str(value)):,.2f}"
