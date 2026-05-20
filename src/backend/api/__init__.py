from src.backend.api.auth import router as auth_router
from src.backend.api.clients import router as clients_router
from src.backend.api.lifecycle import router as lifecycle_router
from src.backend.api.projects import router as projects_router
from src.backend.api.users import router as users_router

__all__ = ["auth_router", "clients_router", "lifecycle_router", "projects_router", "users_router"]
