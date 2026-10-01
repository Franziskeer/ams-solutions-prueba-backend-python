from fastapi import APIRouter, FastAPI

from notifications import router as notifications_router
from notifications.service import NotificationNotFound, NotificationNotProcessable

app = FastAPI(title="Notification Service (Technical Test)")

api_router = APIRouter(prefix="/v1")
api_router.include_router(notifications_router.router)

app.include_router(api_router)
app.add_exception_handler(
    NotificationNotFound, notifications_router.notification_not_found_handler
)
app.add_exception_handler(
    NotificationNotProcessable,
    notifications_router.notification_not_processable_handler,
)
