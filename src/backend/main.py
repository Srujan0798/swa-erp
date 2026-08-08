from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.api.agreements import router as agreements_router
from src.backend.api.auth import router as auth_router
from src.backend.api.boqs import router as boqs_router
from src.backend.api.clients import router as clients_router
from src.backend.api.compliance import projects_compliance_router
from src.backend.api.compliance import router as compliance_router
from src.backend.api.document_references import router as document_references_router
from src.backend.api.documents import router as documents_router
from src.backend.api.exports import router as exports_router
from src.backend.api.health import router as health_router
from src.backend.api.inquiries import router as inquiries_router
from src.backend.api.invoices import router as invoices_router
from src.backend.api.jobs import router as jobs_router
from src.backend.api.lifecycle import router as lifecycle_router
from src.backend.api.materials import router as materials_router
from src.backend.api.notifications import router as notifications_router
from src.backend.api.project_pnl import router as project_pnl_router
from src.backend.api.projects import router as projects_router
from src.backend.api.quotes import router as quotes_router
from src.backend.api.reports import dashboard_router
from src.backend.api.reports import router as reports_router
from src.backend.api.rfqs import router as rfqs_router
from src.backend.api.sustainability_metrics import router as sustainability_metrics_router
from src.backend.api.tasks import router as tasks_router
from src.backend.api.time_tracking import time_entries_router, timesheets_router
from src.backend.api.tokens import router as tokens_router
from src.backend.api.users import router as users_router
from src.backend.api.vendors import router as vendors_router
from src.backend.core.config import settings
from src.backend.core.middleware import RequestIdMiddleware
from src.backend.core.rate_limit import install_auth_rate_limiter

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
app.add_middleware(RequestIdMiddleware)
install_auth_rate_limiter(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(agreements_router)
app.include_router(boqs_router)
app.include_router(clients_router)
app.include_router(compliance_router)
app.include_router(document_references_router)
app.include_router(documents_router)
app.include_router(exports_router)
app.include_router(jobs_router)
app.include_router(inquiries_router)
app.include_router(invoices_router)
app.include_router(lifecycle_router)
app.include_router(materials_router)
app.include_router(notifications_router)
app.include_router(project_pnl_router)
app.include_router(projects_compliance_router)
app.include_router(projects_router)
app.include_router(quotes_router)
app.include_router(reports_router)
app.include_router(dashboard_router)
app.include_router(rfqs_router)
app.include_router(sustainability_metrics_router)
app.include_router(tasks_router)
app.include_router(time_entries_router)
app.include_router(timesheets_router)
app.include_router(tokens_router)
app.include_router(users_router)
app.include_router(vendors_router)
