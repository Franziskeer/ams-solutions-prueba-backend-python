from fastapi import APIRouter, FastAPI

from notifications import router as notifications_router

app = FastAPI(title="Notification Service (Technical Test)")

api_router = APIRouter(prefix="/v1")
api_router.include_router(notifications_router.router)

app.include_router(api_router)
