from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Subscription
from schemas import SubscriptionRequest
from crud.subscribe import is_subscribed


def user_subscribe(
    db: Session, subscription: SubscriptionRequest, user_id: int
) -> Subscription:

    if is_subscribed(db, user_id):
        raise HTTPException(status_code=400, detail="User already has a subscription.")

    new_subscription = Subscription(**subscription.model_dump(), user_id=user_id)
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription
