"""merge all migration heads into one chain

Revision ID: 0028
Revises: 0011, 0018, 0020, 0021, 0023, 0027
Create Date: 2026-08-07 17:40:41.772447

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0028'
down_revision: Union[str, None] = ('0011', '0018', '0020', '0021', '0023', '0027')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass