"""remove dead deleted_at column from documents table

The documents table has a `deleted_at` column that was never read or written
anywhere — the actual delete mechanism uses the `is_active` flag (set via
`update_document(..., is_active=False)` in the delete endpoint). This
migration removes the dead column to avoid maintaining two competing
soft-delete mechanisms.

Revision ID: 0026
Revises: 0025
Create Date: 2026-08-07

"""
from collections.abc import Sequence

from alembic import op

revision: str = "0026"
down_revision: str | None = "0025"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("documents", "deleted_at")


def downgrade() -> None:
    import sqlalchemy as sa

    op.add_column(
        "documents",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
