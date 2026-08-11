SUBSCRIPTION_PAYLOAD = {
    "subscription": {
        "endpoint": "https://fcm.googleapis.com/fcm/send/example-endpoint",
        "expirationTime": None,
        "keys": {"p256dh": "BCEg-example-p256dh-key", "auth": "eEYK-example-auth-key"},
    }
}


def test_subscribe_creates_subscription(client, auth_headers):
    response = client.post("/api/v1/push/subscribe", headers=auth_headers, json=SUBSCRIPTION_PAYLOAD)
    assert response.status_code == 201, response.text
    assert response.json()["status"] == "active"


def test_subscribe_is_idempotent_for_same_endpoint(client, auth_headers):
    first = client.post("/api/v1/push/subscribe", headers=auth_headers, json=SUBSCRIPTION_PAYLOAD)
    second = client.post("/api/v1/push/subscribe", headers=auth_headers, json=SUBSCRIPTION_PAYLOAD)
    assert first.json()["subscription_id"] == second.json()["subscription_id"]


def test_unsubscribe_removes_subscription(client, auth_headers):
    client.post("/api/v1/push/subscribe", headers=auth_headers, json=SUBSCRIPTION_PAYLOAD)

    response = client.post(
        "/api/v1/push/unsubscribe",
        headers=auth_headers,
        json={"endpoint": SUBSCRIPTION_PAYLOAD["subscription"]["endpoint"]},
    )
    assert response.status_code == 200

    missing = client.post(
        "/api/v1/push/unsubscribe",
        headers=auth_headers,
        json={"endpoint": SUBSCRIPTION_PAYLOAD["subscription"]["endpoint"]},
    )
    assert missing.status_code == 404
