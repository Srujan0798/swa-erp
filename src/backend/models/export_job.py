import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.db.base import Base


class ExportJob(Base):
    """Ownership record for an async export (Celery) job.

    Written at enqueue time in ``src/backend/api/exports.py``; read by
    ``src/backend/api/jobs.py`` to enforce per-user ownership (SEC-07).

    A table — rather than Celery result metadata — is used on purpose: the
    result backend has a TTL (``result_expires=3600``), so an expired result
    could otherwise fail open. This row survives result expiry.
    """

    __tablename__ = "export_jobs"

    job_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
