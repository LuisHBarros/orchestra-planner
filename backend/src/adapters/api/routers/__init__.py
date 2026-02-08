"""API routers."""

from backend.src.adapters.api.routers.auth import router as auth_router
from backend.src.adapters.api.routers.invites import router as invites_router
from backend.src.adapters.api.routers.members import router as members_router
from backend.src.adapters.api.routers.projects import router as projects_router
from backend.src.adapters.api.routers.roles import router as roles_router
from backend.src.adapters.api.routers.tasks import router as tasks_router

__all__ = [
    "auth_router",
    "invites_router",
    "members_router",
    "projects_router",
    "roles_router",
    "tasks_router",
]
