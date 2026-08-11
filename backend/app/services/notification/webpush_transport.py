import json
import time

from pywebpush import WebPushException, webpush

from app.core.config import settings
from app.services.notification.base import NotificationPayload, NotificationResult, NotificationTransport


class WebPushTransport(NotificationTransport):
    def send(self, subscription: dict, payload: NotificationPayload) -> NotificationResult:
        notification_data = {
            "title": payload.title,
            "body": payload.body,
            "icon": payload.icon,
            "badge": payload.badge,
            "data": {"task_id": payload.task_id, "click_action": f"/tasks/{payload.task_id}"},
        }
        try:
            webpush(
                subscription_info=subscription,
                data=json.dumps(notification_data),
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={
                    "sub": settings.vapid_claim_email,
                    "exp": int(time.time()) + 12 * 3600,
                },
            )
            return NotificationResult(success=True)
        except WebPushException as exc:
            return NotificationResult(success=False, detail=str(exc))
