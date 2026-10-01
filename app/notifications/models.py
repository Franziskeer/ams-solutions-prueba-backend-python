from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

NotificationType = Literal["email", "sms", "push"]


class NotificationStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"


@dataclass
class Notification:
    id: str
    to: str
    message: str
    type: NotificationType
    status: NotificationStatus = NotificationStatus.QUEUED
    provider_id: str | None = None
