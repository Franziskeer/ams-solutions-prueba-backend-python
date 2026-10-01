from fastapi import APIRouter, FastAPI

from notifications.dependencies import get_delivery_workers, get_provider
from notifications import router as notifications_router
from notifications.service import NotificationNotFound, NotificationNotProcessable

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    workers = get_delivery_workers()
    workers.start()
    try:
        yield
    finally:
        await workers.stop()
        await get_provider().aclose()


app = FastAPI(title="Notification Service (Technical Test)", lifespan=lifespan)

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
