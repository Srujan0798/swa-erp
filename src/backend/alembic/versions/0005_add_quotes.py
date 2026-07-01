"""add quotes and quote_items

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-29

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "quotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("boq_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("markup_percent", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("markup_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("tax_percent", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("terms", sa.Text(), nullable=True),
        sa.Column("validity_days", sa.Integer(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("client_response", sa.String(length=50), nullable=True),
        sa.Column("client_response_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("client_response_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["boq_id"], ["boqs.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_quotes_project_id", "quotes", ["project_id"], unique=False)
    op.create_index("ix_quotes_status", "quotes", ["status"], unique=False)

    op.create_table(
        "quote_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quote_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("boq_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("specification", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("rate", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["quote_id"], ["quotes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["boq_item_id"], ["boq_items.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_quote_items_quote_id", "quote_items", ["quote_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_quote_items_quote_id", table_name="quote_items")
    op.drop_table("quote_items")
    op.drop_index("ix_quotes_status", table_name="quotes")
    op.drop_index("ix_quotes_project_id", table_name="quotes")
    op.drop_table("quotes")
