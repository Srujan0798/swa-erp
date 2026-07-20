from src.backend.api.agreements import router as agreements_router
from src.backend.api.auth import router as auth_router
from src.backend.api.boqs import router as boqs_router
from src.backend.api.clients import router as clients_router
from src.backend.api.document_references import router as document_references_router
from src.backend.api.inquiries import router as inquiries_router
from src.backend.api.lifecycle import router as lifecycle_router
from src.backend.api.projects import router as projects_router
from src.backend.api.sustainability_metrics import router as sustainability_metrics_router
from src.backend.api.tasks import router as tasks_router
from src.backend.api.time_tracking import time_entries_router, timesheets_router
from src.backend.api.tokens import router as tokens_router
from src.backend.api.users import router as users_router

__all__ = [
    "agreements_router",
    "auth_router",
    "boqs_router",
    "clients_router",
    "document_references_router",
    "inquiries_router",
    "lifecycle_router",
    "projects_router",
    "sustainability_metrics_router",
    "tasks_router",
    "time_entries_router",
    "timesheets_router",
    "tokens_router",
    "users_router",
]
