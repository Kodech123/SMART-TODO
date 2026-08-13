import logging

from app.services.notification.base import NotificationPayload, NotificationResult, NotificationTransport

logger = logging.getLogger("dosmart.notifications")


class LogTransport(NotificationTransport):
    """Dev transport: logs the notification instead of delivering it over the network."""

    def send(self, subscription: dict, payload: NotificationPayload) -> NotificationResult:
        logger.info(
            "[notification] endpoint=%s title=%r body=%r task_id=%s reminder_id=%s",
            subscription.get("endpoint"),
            payload.title,
            payload.body,
            payload.task_id,
            payload.reminder_id,
        )
        return NotificationResult(success=True, detail="logged")
