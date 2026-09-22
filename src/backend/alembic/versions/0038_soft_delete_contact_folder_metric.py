"""Soft-delete contacts, document folders, sustainability metrics, vendor contacts.

Closes the soft-delete gap: these business-data tables used hard
deletes. Adds nullable deleted_at (TIMESTAMPTZ) to each; existing rows
are untouched (NULL = live). Documents themselves already deactivate via
is_active; audit_log / reference_counters / refresh_tokens / export_jobs /
task_dependencies / notifications / compliance reference data stay hard by
design (see docs/conventions.md soft-delete matrix).

Revision ID: 0038
Revises: 0037
Create Date: 2026-09-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0038"
down_revision: Union[str, None] = "0037"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "contacts",
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
    )
    # NOTE: document_folders.deleted_at already exists (migration 0010);
    # the model was missing it (drift) — reconciled in models/document.py,
    # no DDL needed here.
    op.add_column(
        "sustainability_metrics",
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        "vendor_contacts",
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    # Soft-deleted rows would be resurrected by a downgrade; that is
    # acceptable for dev rollback but must never run against prod data
    # with deleted rows pending legal hold.
    op.drop_column("vendor_contacts", "deleted_at")
    op.drop_column("sustainability_metrics", "deleted_at")
    op.drop_column("contacts", "deleted_at")
