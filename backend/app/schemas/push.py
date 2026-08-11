from pydantic import BaseModel


class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionPayload(BaseModel):
    endpoint: str
    expirationTime: int | None = None
    keys: PushSubscriptionKeys


class PushSubscribeRequest(BaseModel):
    subscription: PushSubscriptionPayload


class PushSubscribeResponse(BaseModel):
    subscription_id: int
    status: str = "active"
    message: str = "Successfully subscribed to push notifications"


class PushUnsubscribeRequest(BaseModel):
    endpoint: str
