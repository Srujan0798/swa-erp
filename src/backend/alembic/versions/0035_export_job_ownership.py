"""Export-job ownership table (SEC-07 job IDOR fix)

Stores the enqueuing user for every async export job so that
``GET /api/jobs/{id}`` and ``GET /api/jobs/{id}/result`` can enforce
per-user ownership. A table (not Celery result metadata) is used because
the Celery result backend expires (``result_expires=3600``).

Revision ID: 0035
Revises: 0034
Create Date: 2026-09-17
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0035"
down_revision: Union[str, None] = "0034"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "export_jobs",
        sa.Column("job_id", sa.String(64), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_export_jobs_user_id", "export_jobs", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_export_jobs_user_id", table_name="export_jobs")
    op.drop_table("export_jobs")
