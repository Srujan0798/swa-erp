"""add rfqs and rfq_items

Revision ID: 0009
Revises: 0005
Create Date: 2026-06-29

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rfqs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("rfq_number", sa.String(length=50), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("awarded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["vendor_id"], ["vendors.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_rfqs_project_id", "rfqs", ["project_id"], unique=False)
    op.create_index("ix_rfqs_vendor_id", "rfqs", ["vendor_id"], unique=False)
    op.create_index("ix_rfqs_rfq_number", "rfqs", ["rfq_number"], unique=True)

    op.create_table(
        "rfq_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rfq_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "quantity", sa.Numeric(precision=18, scale=2), nullable=False
        ),
        sa.Column(
            "vendor_rate", sa.Numeric(precision=18, scale=2), nullable=True
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["rfq_id"], ["rfqs.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["material_id"], ["materials.id"], ondelete="RESTRICT"
        ),
    )
    op.create_index("ix_rfq_items_rfq_id", "rfq_items", ["rfq_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_rfq_items_rfq_id", table_name="rfq_items")
    op.drop_table("rfq_items")
    op.drop_index("ix_rfqs_rfq_number", table_name="rfqs")
    op.drop_index("ix_rfqs_vendor_id", table_name="rfqs")
    op.drop_index("ix_rfqs_project_id", table_name="rfqs")
    op.drop_table("rfqs")
