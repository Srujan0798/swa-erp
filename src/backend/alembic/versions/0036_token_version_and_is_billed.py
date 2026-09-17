"""Align users.token_version and time_entries.is_billed with models.

The User model was renamed version → token_version (logout/rotation) and
TimeEntry gained is_billed (re-bill guard). 0034 added a `billed` column
that never landed on this database; this revision is idempotent.

Revision ID: 0036
Revises: 0035
Create Date: 2026-09-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0036"
down_revision: Union[str, None] = "0035"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("CREATE SEQUENCE IF NOT EXISTS invoice_number_seq"))
    insp = sa.inspect(conn)

    user_cols = {c["name"] for c in insp.get_columns("users")}
    if "token_version" not in user_cols and "version" in user_cols:
        op.alter_column("users", "version", new_column_name="token_version")
    elif "token_version" not in user_cols:
        op.add_column(
            "users",
            sa.Column("token_version", sa.Integer(), nullable=False, server_default="1"),
        )

    time_cols = {c["name"] for c in insp.get_columns("time_entries")}
    if "is_billed" not in time_cols and "billed" in time_cols:
        op.alter_column("time_entries", "billed", new_column_name="is_billed")
        existing_idx = {i["name"] for i in insp.get_indexes("time_entries")}
        if "ix_time_entries_billed" in existing_idx:
            op.drop_index("ix_time_entries_billed", table_name="time_entries")
        op.create_index("ix_time_entries_is_billed", "time_entries", ["is_billed"])
    elif "is_billed" not in time_cols:
        op.add_column(
            "time_entries",
            sa.Column(
                "is_billed",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )
        op.create_index("ix_time_entries_is_billed", "time_entries", ["is_billed"])


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    time_cols = {c["name"] for c in insp.get_columns("time_entries")}
    if "is_billed" in time_cols:
        existing_idx = {i["name"] for i in insp.get_indexes("time_entries")}
        if "ix_time_entries_is_billed" in existing_idx:
            op.drop_index("ix_time_entries_is_billed", table_name="time_entries")
        op.alter_column("time_entries", "is_billed", new_column_name="billed")
    user_cols = {c["name"] for c in insp.get_columns("users")}
    if "token_version" in user_cols:
        op.alter_column("users", "token_version", new_column_name="version")
