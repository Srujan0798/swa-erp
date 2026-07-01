"""add invoices and invoice_items

Revision ID: 0013
Revises: 0012
Create Date: 2026-06-29

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_number", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("subtotal", sa.Numeric(precision=18, scale=2), nullable=False, server_default=sa.text("0")),
        sa.Column("tax_rate", sa.Numeric(precision=5, scale=2), nullable=False, server_default=sa.text("18")),
        sa.Column("tax_amount", sa.Numeric(precision=18, scale=2), nullable=False, server_default=sa.text("0")),
        sa.Column("total", sa.Numeric(precision=18, scale=2), nullable=False, server_default=sa.text("0")),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'INR'")),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("invoice_number"),
    )
    op.create_index("ix_invoices_project_id", "invoices", ["project_id"], unique=False)
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"], unique=True)

    op.create_table(
        "invoice_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("rate", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("time_entry_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_invoice_items_invoice_id", "invoice_items", ["invoice_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_invoice_items_invoice_id", table_name="invoice_items")
    op.drop_table("invoice_items")
    op.drop_index("ix_invoices_invoice_number", table_name="invoices")
    op.drop_index("ix_invoices_project_id", table_name="invoices")
    op.drop_table("invoices")
