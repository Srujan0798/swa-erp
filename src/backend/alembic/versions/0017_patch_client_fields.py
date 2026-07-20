"""patch client fields (industry, client_status, first_lead_id, first_inquiry_id)

Revision ID: 0017
Revises: 0016
Create Date: 2026-07-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0017"
down_revision: str | None = "0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "clients",
        sa.Column("industry", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "clients",
        sa.Column("client_status", sa.String(length=50), nullable=False, server_default="Active"),
    )
    op.add_column(
        "clients",
        sa.Column("first_lead_id", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "clients",
        sa.Column("first_inquiry_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_clients_first_inquiry_id_inquiries",
        "clients",
        "inquiries",
        ["first_inquiry_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_clients_first_inquiry_id_inquiries", "clients", type_="foreignkey")
    op.drop_column("clients", "first_inquiry_id")
    op.drop_column("clients", "first_lead_id")
    op.drop_column("clients", "client_status")
    op.drop_column("clients", "industry")
