"""drop first_lead_id completely (Viraj 2026-08: no Lead ID columns, not even historical)

Revision ID: 0030
Revises: 0029
Create Date: 2026-08-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0030"
down_revision: Union[str, None] = "0029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("clients")}
    if "first_lead_id" in cols:
        op.drop_column("clients", "first_lead_id")


def downgrade() -> None:
    # Intentionally do not re-add first_lead_id — product decision is permanent.
    pass
