from .auth import router as auth_router
from .org import router as organization_router
from .prj import router as project_router
from .comment import router as comment_router
from .noti import router as notification_router
from .attachment import router as attachment_router



__all__ = [
    "auth_router",
    "organization_router",
    "project_router",
    "task_router",
    "comment_router",
    "notification_router",
    "attachment_router"
]
