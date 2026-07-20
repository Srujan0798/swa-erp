"""add GST breakdown to invoices

Wave-18 hardening pass: the existing invoices table had a generic tax_rate /
tax_amount pair (already 18% by default), but had no explicit GST field. This
migration adds `gst_percent` and `gst_amount` columns mirroring the Quote
table's `tax_percent` / `tax_amount` convention so that downstream code can
talk about "GST" explicitly on the invoice itself (client and vendor
gst_number fields already exist and are out of scope here).

The new columns are added with `server_default` so existing rows — pre-wave-18
invoices whose `total` already implicitly included an 18% tax — get a sensible
default. We then backfill `gst_amount` from `tax_amount` (which the existing
service computes as `subtotal * tax_rate / 100`); for rows where `tax_amount`
is 0 but `total > subtotal` we still default to 0 and let reports flag it
later. The backfill is a best-effort data migration, not a guess at
historical rate changes.

Revision ID: 0025
Revises: 0024
Create Date: 2026-07-21

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0025"
down_revision: str | None = "0024"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "invoices",
        sa.Column(
            "gst_percent",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            server_default=sa.text("18"),
        ),
    )
    op.add_column(
        "invoices",
        sa.Column(
            "gst_amount",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.execute(
        "UPDATE invoices SET gst_amount = tax_amount WHERE gst_amount = 0 AND tax_amount > 0"
    )


def downgrade() -> None:
    op.drop_column("invoices", "gst_amount")
    op.drop_column("invoices", "gst_percent")
