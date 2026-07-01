"""add boqs and boq_items

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-29

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "boqs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("parsed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("parsed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "version_number", name="uq_boq_project_version"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parsed_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_boqs_project_id", "boqs", ["project_id"], unique=False)

    op.create_table(
        "boq_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("boq_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("specification", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("rate", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["boq_id"], ["boqs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_boq_items_boq_id", "boq_items", ["boq_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_boq_items_boq_id", table_name="boq_items")
    op.drop_table("boq_items")
    op.drop_index("ix_boqs_project_id", table_name="boqs")
    op.drop_table("boqs")
