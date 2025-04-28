from models import Subscription
from sqlalchemy.orm import Session


def is_subscribed(db, user_id: int) -> bool:
    return (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id,
        )
        .first()
        is not None
    )
