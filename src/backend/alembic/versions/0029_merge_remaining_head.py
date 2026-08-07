"""merge remaining head 0022

Revision ID: 0029
Revises: 0028
Create Date: 2026-08-07 17:42:02.799667

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0029'
down_revision: Union[str, None] = ('0022', '0028')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass