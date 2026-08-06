"""add version column to projects for optimistic locking

Adds the `version` integer column to the `projects` table, mirroring the
convention already established on `tasks` (0021), `users`, and other models.
`version` is used as the optimistic-locking counter: the project update path
increments it on every write and rejects stale updates (expected version
mismatch) with HTTP 409, mitigating concurrent edits by two PMs on the same
project (see plan/ARCHITECTURE.md failure-points table).

Revision ID: 0026
Revises: 0025
Create Date: 2026-08-07

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0027"
down_revision: str | None = "0026"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )


def downgrade() -> None:
    op.drop_column("projects", "version")
