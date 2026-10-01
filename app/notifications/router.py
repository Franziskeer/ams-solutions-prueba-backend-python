from typing import Literal

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/requests", tags=["Notifications Requests"])


class NotificationRequest(BaseModel):
    to: str
    message: str
    type: Literal["email", "sms", "push"]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_request(body: NotificationRequest) -> dict:
    return {}


@router.post("/{request_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_request(request_id: str) -> dict:
    return {}


@router.get("/{request_id}")
async def get_request(request_id: str) -> dict:
    return {}
