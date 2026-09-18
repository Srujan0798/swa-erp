"""Allow non-project time entries and document references (L3-D).

Meeting 2 rule: time and document references may be non-project (R&D/
admin work dropped from MVP, so a nullable project is enough; no
marketing UI). Relax time_entries.project_id and
document_references.project_id to nullable. No data change; existing
rows are untouched.

Revision ID: 0037
Revises: 0036
Create Date: 2026-09-18
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0037"
down_revision: Union[str, None] = "0036"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("time_entries", "project_id", existing_type=None, nullable=True)
    op.alter_column("document_references", "project_id", existing_type=None, nullable=True)


def downgrade() -> None:
    # Non-project rows (project_id IS NULL) would block re-tightening;
    # clear or reassign them before downgrading.
    op.alter_column("document_references", "project_id", existing_type=None, nullable=False)
    op.alter_column("time_entries", "project_id", existing_type=None, nullable=False)
