import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from notifications import router as notifications_router
from notifications.dependencies import get_delivery_workers, get_provider
from notifications.service import NotificationNotFound, NotificationNotProcessable


def configure_logging() -> None:
    # uvicorn only configures its own loggers; without a handler, INFO records are dropped.
    logger = logging.getLogger("notifications")
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


configure_logging()


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
