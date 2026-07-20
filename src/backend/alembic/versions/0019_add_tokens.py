"""add tokens table

Revision ID: 0019
Revises: 0018
Create Date: 2026-07-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0019"
down_revision: str | None = "0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reference_id", sa.String(length=30), nullable=False),
        sa.Column("agreement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_date", sa.Date(), nullable=False),
        sa.Column("token_type", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("token_status", sa.String(length=50), nullable=False, server_default="In Progress"),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("swa_employee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("project_owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("client_employee_name", sa.String(length=255), nullable=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_id", name="uq_tokens_reference_id"),
        sa.ForeignKeyConstraint(["agreement_id"], ["service_agreements.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["swa_employee_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_tokens_reference_id", "tokens", ["reference_id"], unique=True)
    op.create_index("ix_tokens_agreement_id", "tokens", ["agreement_id"])
    op.create_index("ix_tokens_project_id", "tokens", ["project_id"])
    op.create_index("ix_tokens_token_status", "tokens", ["token_status"])


def downgrade() -> None:
    op.drop_index("ix_tokens_token_status", table_name="tokens")
    op.drop_index("ix_tokens_project_id", table_name="tokens")
    op.drop_index("ix_tokens_agreement_id", table_name="tokens")
    op.drop_index("ix_tokens_reference_id", table_name="tokens")
    op.drop_table("tokens")
