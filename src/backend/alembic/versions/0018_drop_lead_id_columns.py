"""drop lead id columns (first_lead_id, technical_lead_id)

Revision ID: 0018
Revises: 0017
Create Date: 2026-08-11

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0018"
down_revision: str | None = "0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop foreign key constraint for first_inquiry_id if it exists
    op.drop_constraint(
        "fk_clients_first_inquiry_id_inquiries", 
        "clients", 
        type_="foreignkey"
    )
    
    # Drop first_lead_id column from clients table
    op.drop_column("clients", "first_lead_id")
    
    # Drop technical_lead_id column from inquiries table
    op.drop_constraint(
        "fk_inquiries_technical_lead_id_users", 
        "inquiries", 
        type_="foreignkey"
    )
    op.drop_column("inquiries", "technical_lead_id")


def downgrade() -> None:
    # Add technical_lead_id column back to inquiries table
    op.add_column(
        "inquiries",
        sa.Column("technical_lead_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_inquiries_technical_lead_id_users",
        "inquiries",
        "users",
        ["technical_lead_id"],
        ["id"],
        ondelete="SET NULL",
    )
    
    # Add first_lead_id column back to clients table
    op.add_column(
        "clients",
        sa.Column("first_lead_id", sa.String(length=30), nullable=True),
    )
    
    # Recreate foreign key constraint for first_inquiry_id
    op.create_foreign_key(
        "fk_clients_first_inquiry_id_inquiries",
        "clients",
        "inquiries",
        ["first_inquiry_id"],
        ["id"],
        ondelete="SET NULL",
    )