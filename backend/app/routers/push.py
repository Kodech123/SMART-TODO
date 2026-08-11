from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.push_subscription import PushSubscription
from app.models.user import User
from app.schemas.push import PushSubscribeRequest, PushSubscribeResponse, PushUnsubscribeRequest

router = APIRouter(prefix="/api/v1/push", tags=["push"])


@router.post("/subscribe", response_model=PushSubscribeResponse, status_code=status.HTTP_201_CREATED)
def subscribe(
    payload: PushSubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PushSubscribeResponse:
    sub = payload.subscription
    existing = (
        db.query(PushSubscription)
        .filter(PushSubscription.user_id == current_user.user_id, PushSubscription.endpoint == sub.endpoint)
        .first()
    )
    if existing is not None:
        return PushSubscribeResponse(subscription_id=existing.subscription_id)

    subscription = PushSubscription(
        user_id=current_user.user_id,
        endpoint=sub.endpoint,
        auth_key=sub.keys.auth,
        p256dh_key=sub.keys.p256dh,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return PushSubscribeResponse(subscription_id=subscription.subscription_id)


@router.post("/unsubscribe")
def unsubscribe(
    payload: PushUnsubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    subscription = (
        db.query(PushSubscription)
        .filter(PushSubscription.user_id == current_user.user_id, PushSubscription.endpoint == payload.endpoint)
        .first()
    )
    if subscription is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    db.delete(subscription)
    db.commit()
    return {"message": "Unsubscribed"}
