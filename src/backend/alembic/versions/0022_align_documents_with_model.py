"""align documents table with Document model

Adds columns the Document ORM model expects but the 0010 migration didn't create.

Revision ID: 0022
Revises: 0010
Create Date: 2026-07-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0022"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("stored_name", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("version_number", sa.Integer(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "updated_at")
    op.drop_column("documents", "version_number")
    op.drop_column("documents", "stored_name")
