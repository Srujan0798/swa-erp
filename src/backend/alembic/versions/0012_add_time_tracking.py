"""add time_entries and timesheets

Revision ID: 0012
Revises: 0005
Create Date: 2026-06-29

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0012"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "time_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("hours", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_billable", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_time_entries_project_id", "time_entries", ["project_id"], unique=False)
    op.create_index("ix_time_entries_task_id", "time_entries", ["task_id"], unique=False)
    op.create_index("ix_time_entries_user_id", "time_entries", ["user_id"], unique=False)

    op.create_table(
        "timesheets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("week_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("total_hours", sa.Numeric(precision=6, scale=2), nullable=False, server_default=sa.text("0")),
        sa.Column("billable_hours", sa.Numeric(precision=6, scale=2), nullable=False, server_default=sa.text("0")),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_timesheets_user_id", "timesheets", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_timesheets_user_id", table_name="timesheets")
    op.drop_table("timesheets")
    op.drop_index("ix_time_entries_user_id", table_name="time_entries")
    op.drop_index("ix_time_entries_task_id", table_name="time_entries")
    op.drop_index("ix_time_entries_project_id", table_name="time_entries")
    op.drop_table("time_entries")
