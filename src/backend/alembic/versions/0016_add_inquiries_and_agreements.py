"""add inquiries and service_agreements tables

Revision ID: 0016
Revises: 0014
Create Date: 2026-07-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0016"
down_revision: str | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "inquiries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reference_id", sa.String(length=30), nullable=False),
        sa.Column("inquiry_date", sa.Date(), nullable=False),
        sa.Column("inquiry_type", sa.String(length=50), nullable=True),
        sa.Column("inquiry_source", sa.String(length=100), nullable=True),
        sa.Column("client_name", sa.String(length=255), nullable=False),
        sa.Column("requirement_summary", sa.Text(), nullable=True),
        sa.Column("estimated_value", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="New"),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("technical_lead_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("converted_client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("converted_project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_id", name="uq_inquiries_reference_id"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["technical_lead_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["converted_client_id"], ["clients.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["converted_project_id"], ["projects.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_inquiries_reference_id", "inquiries", ["reference_id"], unique=True)
    op.create_index("ix_inquiries_status", "inquiries", ["status"])
    op.create_index("ix_inquiries_client_name", "inquiries", ["client_name"])
    op.create_index("ix_inquiries_converted_client_id", "inquiries", ["converted_client_id"])
    op.create_index("ix_inquiries_converted_project_id", "inquiries", ["converted_project_id"])

    op.create_table(
        "service_agreements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reference_id", sa.String(length=30), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("inquiry_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("service_name", sa.String(length=255), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="Active"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_id", name="uq_service_agreements_reference_id"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["inquiry_id"], ["inquiries.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_service_agreements_reference_id", "service_agreements", ["reference_id"], unique=True)
    op.create_index("ix_service_agreements_client_id", "service_agreements", ["client_id"])
    op.create_index("ix_service_agreements_inquiry_id", "service_agreements", ["inquiry_id"])
    op.create_index("ix_service_agreements_status", "service_agreements", ["status"])


def downgrade() -> None:
    op.drop_index("ix_service_agreements_status", table_name="service_agreements")
    op.drop_index("ix_service_agreements_inquiry_id", table_name="service_agreements")
    op.drop_index("ix_service_agreements_client_id", table_name="service_agreements")
    op.drop_index("ix_service_agreements_reference_id", table_name="service_agreements")
    op.drop_table("service_agreements")

    op.drop_index("ix_inquiries_converted_project_id", table_name="inquiries")
    op.drop_index("ix_inquiries_converted_client_id", table_name="inquiries")
    op.drop_index("ix_inquiries_client_name", table_name="inquiries")
    op.drop_index("ix_inquiries_status", table_name="inquiries")
    op.drop_index("ix_inquiries_reference_id", table_name="inquiries")
    op.drop_table("inquiries")
