"""Excel field parity: time logging columns + inquiry technical_lead

Revision ID: 0031
Revises: 0030
Create Date: 2026-08-23

Adds high-frequency Time Logging Sheet columns onto time_entries, and
stores Inquiry sheet "Technical Lead" as a free-text name (Excel reality).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0031"
down_revision: Union[str, None] = "0030"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    te_cols = {c["name"] for c in insp.get_columns("time_entries")}
    for name, col in [
        ("employee_name", sa.Column("employee_name", sa.String(length=255), nullable=True)),
        ("employee_role", sa.Column("employee_role", sa.String(length=50), nullable=True)),
        ("work_type", sa.Column("work_type", sa.String(length=50), nullable=True)),
        ("sheet_reference_id", sa.Column("sheet_reference_id", sa.String(length=50), nullable=True)),
        ("revision", sa.Column("revision", sa.String(length=20), nullable=True)),
        ("activity_type", sa.Column("activity_type", sa.String(length=50), nullable=True)),
        ("software_used", sa.Column("software_used", sa.String(length=100), nullable=True)),
        ("work_mode", sa.Column("work_mode", sa.String(length=50), nullable=True)),
        ("billable_hours", sa.Column("billable_hours", sa.Numeric(precision=4, scale=2), nullable=True)),
    ]:
        if name not in te_cols:
            op.add_column("time_entries", col)

    existing_indexes = {ix["name"] for ix in sa.inspect(conn).get_indexes("time_entries")}
    if "ix_time_entries_sheet_reference_id" not in existing_indexes:
        op.create_index(
            "ix_time_entries_sheet_reference_id",
            "time_entries",
            ["sheet_reference_id"],
            unique=False,
        )

    inq_cols = {c["name"] for c in insp.get_columns("inquiries")}
    if "technical_lead" not in inq_cols:
        op.add_column(
            "inquiries",
            sa.Column("technical_lead", sa.String(length=255), nullable=True),
        )


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    inq_cols = {c["name"] for c in insp.get_columns("inquiries")}
    if "technical_lead" in inq_cols:
        op.drop_column("inquiries", "technical_lead")

    existing_indexes = {ix["name"] for ix in insp.get_indexes("time_entries")}
    if "ix_time_entries_sheet_reference_id" in existing_indexes:
        op.drop_index("ix_time_entries_sheet_reference_id", table_name="time_entries")

    te_cols = {c["name"] for c in insp.get_columns("time_entries")}
    for name in (
        "billable_hours",
        "work_mode",
        "software_used",
        "activity_type",
        "revision",
        "sheet_reference_id",
        "work_type",
        "employee_role",
        "employee_name",
    ):
        if name in te_cols:
            op.drop_column("time_entries", name)
