from app.services.notification.base import NotificationPayload
from app.services.notification.webpush_transport import WebPushTransport

PAYLOAD = NotificationPayload(title="Task Reminder: Test", body="Priority: P1", task_id=1, reminder_id=1)


def test_send_without_endpoint_fails_gracefully_instead_of_raising():
    result = WebPushTransport().send({"endpoint": None}, PAYLOAD)

    assert result.success is False
    assert "endpoint" in result.detail.lower()


def test_send_with_empty_endpoint_fails_gracefully():
    result = WebPushTransport().send({"endpoint": ""}, PAYLOAD)

    assert result.success is False
