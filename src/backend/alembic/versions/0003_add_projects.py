"""add projects

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("pm_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("designer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("auditor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("estimated_value", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("actual_value", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("target_end_date", sa.Date(), nullable=True),
        sa.Column("actual_end_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["pm_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["designer_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["auditor_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_projects_client_id", "projects", ["client_id"], unique=False)
    op.create_index("ix_projects_code", "projects", ["code"], unique=True)
    op.create_index("ix_projects_pm_id", "projects", ["pm_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_projects_pm_id", table_name="projects")
    op.drop_index("ix_projects_code", table_name="projects")
    op.drop_index("ix_projects_client_id", table_name="projects")
    op.drop_table("projects")