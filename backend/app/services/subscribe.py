from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Subscription
from schemas import SubscriptionRequest
from crud.subscribe import is_subscribed
from crud.user import get_email_by_user_id
from celery_tasks.tasks import send_subscription_email


def user_subscribe(
    db: Session, subscription: SubscriptionRequest, user_id: int
) -> Subscription:

    if is_subscribed(db, user_id):
        raise HTTPException(
            status_code=400, detail="User already has a subscription."
        )

    new_subscription = Subscription(
        **subscription.model_dump(),
        user_id=user_id
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    send_subscription_email.delay(
        get_email_by_user_id(db, user_id),
        new_subscription.city,
    )

    return new_subscription
