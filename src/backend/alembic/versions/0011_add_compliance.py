"""add compliance tables

Revision ID: 0011
Revises: 0005
Create Date: 2026-06-29

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "compliance_standards",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "compliance_checklist_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "standard_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("requirement", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["standard_id"], ["compliance_standards.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_compliance_checklist_items_standard_id",
        "compliance_checklist_items",
        ["standard_id"],
        unique=False,
    )

    op.create_table(
        "project_compliance_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "checklist_item_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column(
            "evidence_document_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "reviewed_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["checklist_item_id"],
            ["compliance_checklist_items.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["evidence_document_id"], ["documents.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"], ["users.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "ix_project_compliance_items_project_id",
        "project_compliance_items",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "ix_project_compliance_items_checklist_item_id",
        "project_compliance_items",
        ["checklist_item_id"],
        unique=False,
    )

    # Seed initial standards
    standards_table = sa.table(
        "compliance_standards",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String()),
        sa.column("version", sa.String()),
        sa.column("description", sa.Text()),
    )
    op.bulk_insert(
        standards_table,
        [
            {
                "id": "a1111111-1111-1111-1111-111111111111",
                "name": "NBC",
                "version": "2016",
                "description": "National Building Code of India",
            },
            {
                "id": "b2222222-2222-2222-2222-222222222222",
                "name": "ECBC",
                "version": "2017",
                "description": "Energy Conservation Building Code",
            },
            {
                "id": "c3333333-3333-3333-3333-333333333333",
                "name": "IGBC",
                "version": "2011",
                "description": "Indian Green Building Council",
            },
            {
                "id": "d4444444-4444-4444-4444-444444444444",
                "name": "IS",
                "version": "2021",
                "description": "Indian Standards — Fire Codes",
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_project_compliance_items_checklist_item_id",
        table_name="project_compliance_items",
    )
    op.drop_index(
        "ix_project_compliance_items_project_id",
        table_name="project_compliance_items",
    )
    op.drop_table("project_compliance_items")
    op.drop_index(
        "ix_compliance_checklist_items_standard_id",
        table_name="compliance_checklist_items",
    )
    op.drop_table("compliance_checklist_items")
    op.drop_table("compliance_standards")
