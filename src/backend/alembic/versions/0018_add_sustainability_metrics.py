"""add sustainability metrics table

Revision ID: 0018
Revises: 0015
Create Date: 2026-07-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0018"
down_revision: str | None = "0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sustainability_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("reference_id", sa.String(length=30), nullable=True),
        sa.Column("recorded_date", sa.Date(), nullable=True),
        sa.Column("compliant_with_green_standards", sa.Boolean(), nullable=True),
        sa.Column("energy_saved_kwh", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("co2_avoided_tco2e", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column(
            "lifecycle_cost_savings_inr", sa.Numeric(precision=18, scale=2), nullable=True
        ),
        sa.Column(
            "insulation_efficiency_ratio", sa.Numeric(precision=5, scale=2), nullable=True
        ),
        sa.Column(
            "payback_period_months", sa.Numeric(precision=6, scale=2), nullable=True
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_sustainability_metrics_project_id",
        "sustainability_metrics",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_sustainability_metrics_project_id", table_name="sustainability_metrics"
    )
    op.drop_table("sustainability_metrics")
