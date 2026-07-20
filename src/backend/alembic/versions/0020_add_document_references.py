"""add document references table

Revision ID: 0020
Revises: 0019
Create Date: 2026-07-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0020"
down_revision: str | None = "0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "document_references",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reference_id", sa.String(length=30), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("doc_date", sa.Date(), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_ref", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("revision", sa.String(length=10), nullable=False, server_default="R0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="Draft"),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_id", name="uq_document_references_reference_id"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["token_id"], ["tokens.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_document_references_reference_id",
        "document_references",
        ["reference_id"],
        unique=True,
    )
    op.create_index(
        "ix_document_references_project_id", "document_references", ["project_id"]
    )
    op.create_index(
        "ix_document_references_token_id", "document_references", ["token_id"]
    )
    op.create_index(
        "ix_document_references_document_type",
        "document_references",
        ["document_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_document_references_document_type", table_name="document_references")
    op.drop_index("ix_document_references_token_id", table_name="document_references")
    op.drop_index("ix_document_references_project_id", table_name="document_references")
    op.drop_index("ix_document_references_reference_id", table_name="document_references")
    op.drop_table("document_references")
