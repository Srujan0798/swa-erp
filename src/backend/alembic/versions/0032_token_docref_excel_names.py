"""Excel name columns on tokens + document_references

Revision ID: 0032
Revises: 0031
Create Date: 2026-08-23

Stores free-text names from Tokens / Document Reference sheets even when
the named person is not a system user (import previously dropped names).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0032"
down_revision: Union[str, None] = "0031"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    te_cols = {c["name"] for c in insp.get_columns("tokens")}
    if "swa_employee_name" not in te_cols:
        op.add_column("tokens", sa.Column("swa_employee_name", sa.String(length=255), nullable=True))
    if "project_owner_name" not in te_cols:
        op.add_column("tokens", sa.Column("project_owner_name", sa.String(length=255), nullable=True))

    dr_cols = {c["name"] for c in insp.get_columns("document_references")}
    if "author_name" not in dr_cols:
        op.add_column(
            "document_references",
            sa.Column("author_name", sa.String(length=255), nullable=True),
        )


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    dr_cols = {c["name"] for c in insp.get_columns("document_references")}
    if "author_name" in dr_cols:
        op.drop_column("document_references", "author_name")

    te_cols = {c["name"] for c in insp.get_columns("tokens")}
    if "project_owner_name" in te_cols:
        op.drop_column("tokens", "project_owner_name")
    if "swa_employee_name" in te_cols:
        op.drop_column("tokens", "swa_employee_name")
