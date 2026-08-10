import uuid
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.backend.core.config import settings
from src.backend.core.storage import get_storage
from src.backend.services.export_service import export_project_summary
from src.backend.workers.celery_app import app

_worker_engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
_worker_session_factory = sessionmaker(
    autoflush=False, autocommit=False, expire_on_commit=False, bind=_worker_engine
)


def _worker_db() -> Session:
    return _worker_session_factory()


def _store_result(job_id: str, pdf_bytes: bytes) -> str:
    key = f"jobs/{job_id}.pdf"
    return get_storage().save(key, pdf_bytes)


@app.task(bind=True, name="workers.generate_project_summary_pdf", max_retries=2)
def generate_project_summary_pdf(self, project_id: str) -> str:
    db = _worker_db()
    try:
        pdf_bytes = export_project_summary(db, uuid.UUID(project_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10) from exc
    finally:
        db.close()

    return _store_result(self.request.id, pdf_bytes)


@app.task(bind=True, name="workers.generate_financial_report_pdf", max_retries=2)
def generate_financial_report_pdf(self, start_date_iso: str, end_date_iso: str) -> str:
    db = _worker_db()
    try:
        from src.backend.services.export_service import export_financial_report

        pdf_bytes = export_financial_report(
            db, date.fromisoformat(start_date_iso), date.fromisoformat(end_date_iso)
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10) from exc
    finally:
        db.close()

    return _store_result(self.request.id, pdf_bytes)


@app.task(bind=True, name="workers.generate_project_slides_pdf", max_retries=2)
def generate_project_slides_pdf(self, project_id: str) -> str:
    db = _worker_db()
    try:
        from src.backend.services.export_service import export_project_slides

        pdf_bytes = export_project_slides(db, uuid.UUID(project_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10) from exc
    finally:
        db.close()

    return _store_result(self.request.id, pdf_bytes)
