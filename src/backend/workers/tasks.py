import os
import tempfile
import uuid
from datetime import date

from sqlalchemy.orm import Session, sessionmaker

from src.backend.core.config import settings
from src.backend.db.base import Base
from src.backend.services.export_service import export_project_summary

from src.backend.workers.celery_app import app

from sqlalchemy import create_engine

_worker_engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
_worker_session_factory = sessionmaker(
    autoflush=False, autocommit=False, expire_on_commit=False, bind=_worker_engine
)


def _worker_db() -> Session:
    return _worker_session_factory()


@app.task(bind=True, name="workers.generate_project_summary_pdf", max_retries=2)
def generate_project_summary_pdf(self, project_id: str) -> str:
    db = _worker_db()
    try:
        pdf_bytes = export_project_summary(db, uuid.UUID(project_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
    finally:
        db.close()

    output_dir = os.path.join(tempfile.gettempdir(), "swa_erp_jobs")
    os.makedirs(output_dir, exist_ok=True)
    result_path = os.path.join(output_dir, f"{self.request.id}.pdf")
    with open(result_path, "wb") as f:
        f.write(pdf_bytes)
    return result_path


@app.task(bind=True, name="workers.generate_financial_report_pdf", max_retries=2)
def generate_financial_report_pdf(self, start_date_iso: str, end_date_iso: str) -> str:
    db = _worker_db()
    try:
        from src.backend.services.export_service import export_financial_report

        pdf_bytes = export_financial_report(
            db, date.fromisoformat(start_date_iso), date.fromisoformat(end_date_iso)
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
    finally:
        db.close()

    output_dir = os.path.join(tempfile.gettempdir(), "swa_erp_jobs")
    os.makedirs(output_dir, exist_ok=True)
    result_path = os.path.join(output_dir, f"{self.request.id}.pdf")
    with open(result_path, "wb") as f:
        f.write(pdf_bytes)
    return result_path
