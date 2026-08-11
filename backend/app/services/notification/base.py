from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class NotificationPayload:
    title: str
    body: str
    task_id: int
    icon: str = "/icon-192x192.png"
    badge: str = "/badge-72x72.png"


@dataclass
class NotificationResult:
    success: bool
    detail: str = ""


class NotificationTransport(ABC):
    @abstractmethod
    def send(self, subscription: dict, payload: NotificationPayload) -> NotificationResult:
        raise NotImplementedError
