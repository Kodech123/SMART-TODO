from functools import lru_cache

from app.core.config import settings
from app.services.notification.base import NotificationTransport
from app.services.notification.log_transport import LogTransport
from app.services.notification.webpush_transport import WebPushTransport


@lru_cache
def get_notification_transport() -> NotificationTransport:
    """Selection is a single NOTIFICATION_TRANSPORT env var — swapping dev-log for
    real Web Push delivery requires zero code changes.
    """
    if settings.notification_transport == "webpush":
        return WebPushTransport()
    return LogTransport()
