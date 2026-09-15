"""Invoice-number sequence + time_entry.billed column

Replaces the SELECT ORDER BY +1 race with a PostgreSQL sequence, and adds
a ``billed`` flag on time entries so already-invoiced rows are excluded.

Revision ID: 0034
Revises: 0033
Create Date: 2026-09-15
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0034"
down_revision: Union[str, None] = "0033"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- invoice number sequence ---
    op.execute(sa.text("CREATE SEQUENCE IF NOT EXISTS invoice_number_seq"))

    # Backfill the sequence to max(existing invoice_number suffix) so
    # future nextval() calls do not collide with already-issued numbers.
    conn = op.get_bind()
    row = conn.execute(
        sa.text(
            "SELECT MAX(CAST(SPLIT_PART(invoice_number, '-', 3) AS INTEGER)) "
            "FROM invoices WHERE deleted_at IS NULL"
        )
    ).fetchone()
    max_seq: int = int(row[0]) if row is not None and row[0] is not None else 0
    if max_seq > 0:
        conn.execute(sa.text(f"SELECT SETVAL('invoice_number_seq', {max_seq})"))

    # --- time_entry.billed flag ---
    op.add_column(
        "time_entries",
        sa.Column("billed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_time_entries_billed", "time_entries", ["billed"])


def downgrade() -> None:
    op.drop_index("ix_time_entries_billed", table_name="time_entries")
    op.drop_column("time_entries", "billed")
    op.execute(sa.text("DROP SEQUENCE IF EXISTS invoice_number_seq"))
