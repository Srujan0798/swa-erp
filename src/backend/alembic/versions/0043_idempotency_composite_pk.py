"""Make idempotency_keys PK composite (key, user_id).

The PK on `key` alone collided when two users shared an Idempotency-Key
(IntegrityError -> 500). The service scopes replay per (key, user), so the
uniqueness constraint must match. NOTE: downgrade requires no duplicate
`key` values across users (dedupe first if a production table has any).

Revision ID: 0043
Revises: 0042
Create Date: 2026-09-22
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0043"
down_revision: Union[str, None] = "0042"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("idempotency_keys_pkey", "idempotency_keys", type_="primary")
    op.create_primary_key("idempotency_keys_pkey", "idempotency_keys", ["key", "user_id"])


def downgrade() -> None:
    op.drop_constraint("idempotency_keys_pkey", "idempotency_keys", type_="primary")
    op.create_primary_key("idempotency_keys_pkey", "idempotency_keys", ["key"])
