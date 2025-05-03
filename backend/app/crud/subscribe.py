from models import Subscription


def is_subscribed(db, user_id: int) -> bool:
    return (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id,
        )
        .first()
        is not None
    )
