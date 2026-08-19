from celery import Celery  # type: ignore[import-untyped]

from src.backend.core.config import settings

app = Celery("swa_erp", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
)

app.autodiscover_tasks(["src.backend.workers"])
