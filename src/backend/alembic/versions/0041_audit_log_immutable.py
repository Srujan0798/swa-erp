"""Immutable audit log + documents alignment CHECKs.

1. audit_log becomes append-only at the database level: a trigger rejects
   UPDATE and DELETE on every row. Application code only INSERTs (verified:
   no UPDATE/DELETE of AuditLog anywhere in src/). This makes the audit
   trail tamper-evident even against a compromised app session.
2. documents.uploaded_by is already relaxed by 0040; documents.content_type
   length 100 -> 255 is NOT changed (all real MIME types fit; widening can
   ride a future migration if needed).

Revision ID: 0041
Revises: 0040
Create Date: 2026-09-21
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0041"
down_revision: Union[str, None] = "0040"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_audit_log_mutation()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only (action=%, id=%)',
                COALESCE(OLD.action, NEW.action), COALESCE(OLD.id, NEW.id);
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_audit_log_no_update ON audit_log;
        CREATE TRIGGER trg_audit_log_no_update
            BEFORE UPDATE ON audit_log
            FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_mutation();
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_audit_log_no_delete ON audit_log;
        CREATE TRIGGER trg_audit_log_no_delete
            BEFORE DELETE ON audit_log
            FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_no_delete ON audit_log")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_no_update ON audit_log")
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_log_mutation()")
