"""align timesheet_audit_log with TimesheetAuditLog model

The TimesheetAuditLog ORM model (src/backend/models/time_tracking.py) is used by
src/backend/services/time_service.py:_create_audit_log(), which is invoked from both
submit_timesheet_service() and approve_timesheet_service(). Neither the 0012 migration
(which created `timesheets`) nor any later migration ever created the
`timesheet_audit_log` table, so POST /api/timesheets/{id}/submit and the approve
endpoint 500 on a live database with `relation "timesheet_audit_log" does not exist`.
Same systemic model/migration drift pattern as wave-12's Task and Document fixes,
manifesting here as a missing table.

Revision ID: 0024
Revises: 0013
Create Date: 2026-07-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0024"
down_revision: str | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "timesheet_audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("timesheet_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("performed_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["timesheet_id"], ["timesheets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["performed_by"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_timesheet_audit_log_timesheet_id", "timesheet_audit_log", ["timesheet_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_timesheet_audit_log_timesheet_id", table_name="timesheet_audit_log")
    op.drop_table("timesheet_audit_log")
