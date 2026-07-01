"""add material categories and materials

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "material_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["parent_id"], ["material_categories.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_material_categories_parent_id", "material_categories", ["parent_id"], unique=False)

    op.create_table(
        "materials",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.ForeignKeyConstraint(["category_id"], ["material_categories.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_materials_code", "materials", ["code"], unique=True)
    op.create_index("ix_materials_category_id", "materials", ["category_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_materials_category_id", table_name="materials")
    op.drop_index("ix_materials_code", table_name="materials")
    op.drop_table("materials")
    op.drop_index("ix_material_categories_parent_id", table_name="material_categories")
    op.drop_table("material_categories")
