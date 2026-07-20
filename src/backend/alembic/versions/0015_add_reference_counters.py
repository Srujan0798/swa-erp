"""add reference_counters table

Revision ID: 0015
Revises: 0014
Create Date: 2026-07-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0015"
down_revision: str | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reference_counters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=10), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("last_seq", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("entity_type", "year", name="uq_refcounter_type_year"),
    )
    op.create_index("ix_reference_counters_entity_type", "reference_counters", ["entity_type"])


def downgrade() -> None:
    op.drop_index("ix_reference_counters_entity_type", table_name="reference_counters")
    op.drop_table("reference_counters")
