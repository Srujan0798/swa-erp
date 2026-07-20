"""align tasks table with Task model

Adds columns the Task ORM model expects but the 0006 migration didn't create,
and converts the priority column from String to Integer to match the model.

Revision ID: 0021
Revises: 0006
Create Date: 2026-07-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0021"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "task_dependencies",
        sa.Column(
            "task_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "depends_on_task_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("task_id", "depends_on_task_id"),
        sa.ForeignKeyConstraint(
            ["task_id"], ["tasks.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["depends_on_task_id"], ["tasks.id"], ondelete="CASCADE"
        ),
    )
    op.alter_column(
        "tasks",
        "created_by",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )
    op.add_column(
        "tasks",
        sa.Column(
            "reporter_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_tasks_reporter_id_users",
        "tasks",
        "users",
        ["reporter_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column(
        "tasks",
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column("estimated_hours", sa.Numeric(precision=6, scale=2), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column(
            "actual_hours",
            sa.Numeric(precision=6, scale=2),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "tasks",
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "tasks",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.execute("ALTER TABLE tasks ALTER COLUMN priority DROP DEFAULT")
    op.drop_constraint("ck_task_priority", "tasks", type_="check")
    op.alter_column(
        "tasks",
        "priority",
        existing_type=sa.String(length=50),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="""
            CASE priority
                WHEN 'low' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'high' THEN 3
                WHEN 'critical' THEN 4
                ELSE 0
            END
        """,
    )
    op.alter_column(
        "tasks",
        "priority",
        existing_type=sa.Integer(),
        existing_nullable=False,
        server_default="0",
    )
    op.alter_column(
        "tasks",
        "due_date",
        existing_type=sa.Date(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        using="due_date::timestamp with time zone",
    )
    op.add_column(
        "task_comments",
        sa.Column(
            "author_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_task_comments_author_id_users",
        "task_comments",
        "users",
        ["author_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column(
        "task_comments",
        sa.Column(
            "parent_comment_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_task_comments_parent_comment_id_task_comments",
        "task_comments",
        "task_comments",
        ["parent_comment_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.add_column(
        "task_comments",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.alter_column(
        "task_comments",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )


def downgrade() -> None:
    op.drop_table("task_dependencies")
    op.alter_column(
        "task_comments",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.drop_column("task_comments", "updated_at")
    op.drop_constraint(
        "fk_task_comments_parent_comment_id_task_comments",
        "task_comments",
        type_="foreignkey",
    )
    op.drop_column("task_comments", "parent_comment_id")
    op.drop_constraint(
        "fk_task_comments_author_id_users", "task_comments", type_="foreignkey"
    )
    op.drop_column("task_comments", "author_id")
    op.alter_column(
        "tasks",
        "created_by",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.alter_column(
        "tasks",
        "due_date",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.Date(),
        existing_nullable=True,
    )
    op.alter_column(
        "tasks",
        "priority",
        existing_type=sa.Integer(),
        type_=sa.String(length=50),
        existing_nullable=False,
        postgresql_using="""
            CASE priority
                WHEN 1 THEN 'low'
                WHEN 2 THEN 'medium'
                WHEN 3 THEN 'high'
                WHEN 4 THEN 'critical'
                ELSE 'medium'
            END
        """,
    )
    op.create_check_constraint(
        "ck_task_priority",
        "tasks",
        "priority IN ('low', 'medium', 'high', 'critical')",
    )
    op.drop_column("tasks", "version")
    op.drop_column("tasks", "position")
    op.drop_column("tasks", "actual_hours")
    op.drop_column("tasks", "estimated_hours")
    op.drop_column("tasks", "completed_at")
    op.drop_column("tasks", "started_at")
    op.drop_constraint("fk_tasks_reporter_id_users", "tasks", type_="foreignkey")
    op.drop_column("tasks", "reporter_id")
