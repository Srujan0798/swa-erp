"""Project Tracking + Clients Sheet Excel field parity

Revision ID: 0033
Revises: 0032
Create Date: 2026-08-23

Adds Project Tracking columns (inquiry, milestone, progress, team leader,
project owner) and Clients Sheet columns (primary contact, date onboarded).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0033"
down_revision: Union[str, None] = "0032"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    p_cols = {c["name"] for c in insp.get_columns("projects")}
    if "inquiry_id" not in p_cols:
        op.add_column(
            "projects",
            sa.Column("inquiry_id", postgresql.UUID(as_uuid=True), nullable=True),
        )
        op.create_foreign_key(
            "fk_projects_inquiry_id_inquiries",
            "projects",
            "inquiries",
            ["inquiry_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index("ix_projects_inquiry_id", "projects", ["inquiry_id"])
    if "milestone" not in p_cols:
        op.add_column("projects", sa.Column("milestone", sa.String(length=255), nullable=True))
    if "progress_indicators" not in p_cols:
        op.add_column(
            "projects", sa.Column("progress_indicators", sa.String(length=255), nullable=True)
        )
    if "team_leader_name" not in p_cols:
        op.add_column(
            "projects", sa.Column("team_leader_name", sa.String(length=255), nullable=True)
        )
    if "project_owner_name" not in p_cols:
        op.add_column(
            "projects", sa.Column("project_owner_name", sa.String(length=255), nullable=True)
        )
    if "notes" not in p_cols:
        op.add_column("projects", sa.Column("notes", sa.Text(), nullable=True))

    c_cols = {c["name"] for c in insp.get_columns("clients")}
    if "primary_contact" not in c_cols:
        op.add_column(
            "clients", sa.Column("primary_contact", sa.String(length=255), nullable=True)
        )
    if "date_onboarded" not in c_cols:
        op.add_column("clients", sa.Column("date_onboarded", sa.Date(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    c_cols = {c["name"] for c in insp.get_columns("clients")}
    if "date_onboarded" in c_cols:
        op.drop_column("clients", "date_onboarded")
    if "primary_contact" in c_cols:
        op.drop_column("clients", "primary_contact")

    p_cols = {c["name"] for c in insp.get_columns("projects")}
    if "notes" in p_cols:
        op.drop_column("projects", "notes")
    if "project_owner_name" in p_cols:
        op.drop_column("projects", "project_owner_name")
    if "team_leader_name" in p_cols:
        op.drop_column("projects", "team_leader_name")
    if "progress_indicators" in p_cols:
        op.drop_column("projects", "progress_indicators")
    if "milestone" in p_cols:
        op.drop_column("projects", "milestone")
    if "inquiry_id" in p_cols:
        op.drop_index("ix_projects_inquiry_id", table_name="projects")
        op.drop_constraint("fk_projects_inquiry_id_inquiries", "projects", type_="foreignkey")
        op.drop_column("projects", "inquiry_id")
