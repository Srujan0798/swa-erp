"""Drop dead documents.version column.

Migration 0010 created documents with a NOT NULL `version` column; the
codebase moved to `version_number` (migration 0022) and nothing has read
or written `version` since. The leftover NOT NULL constraint breaks every
document INSERT on migration-built databases. Dropping the dead column.

Revision ID: 0039
Revises: 0038
Create Date: 2026-09-21
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0039"
down_revision: Union[str, None] = "0038"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # IF EXISTS: dev databases built via create_all never had this column;
    # migration-built databases carry it as a dead NOT NULL leftover from 0010.
    op.execute("ALTER TABLE documents DROP COLUMN IF EXISTS version")


def downgrade() -> None:
    # Re-adding would need NOT NULL with a backfill; the column is dead,
    # so downgrade restores it as nullable to avoid breaking existing rows.
    op.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS version INTEGER")
