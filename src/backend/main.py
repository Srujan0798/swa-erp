from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.api.auth import router as auth_router
from src.backend.api.health import router as health_router
from src.backend.api.users import router as users_router
from src.backend.core.config import settings
from src.backend.core.middleware import RequestIdMiddleware

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(users_router)
