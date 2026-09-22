"""Align documents table with the Document model (round 2).

Migration 0022 added updated_at/stored_name/version_number but left
updated_at without the server default the model declares, so INSERTs on
migration-built databases store NULL updated_at and DocumentRead (which
requires a datetime) fails validation. 0010 declared uploaded_by NOT NULL
while the model allows NULL (system uploads). This migration:
- backfills NULL updated_at from created_at, then sets server default now()
- relaxes uploaded_at nullability already-true (no-op, documented)
- relaxes uploaded_by to nullable to match the model

Revision ID: 0040
Revises: 0039
Create Date: 2026-09-21
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0040"
down_revision: Union[str, None] = "0039"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE documents SET updated_at = created_at WHERE updated_at IS NULL")
    op.execute("ALTER TABLE documents ALTER COLUMN updated_at SET DEFAULT now()")
    # IF EXISTS / idempotent: create_all-built databases never had NOT NULL here.
    op.execute("ALTER TABLE documents ALTER COLUMN uploaded_by DROP NOT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE documents ALTER COLUMN uploaded_by SET NOT NULL")
    op.execute("ALTER TABLE documents ALTER COLUMN updated_at DROP DEFAULT")
