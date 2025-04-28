from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db, get_user_id_from_token
from schemas import SubscriptionRequest
from services import subscribe as subscribe_service

router = APIRouter()


@router.post(
    "/create",
    summary="Subscribe to Alerts",
    description="Allows a user to subscribe to alerts by providing subscription details.",
    response_model=SubscriptionRequest,
)
def subscribe(
    subscription: SubscriptionRequest,
    user_id=Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
) -> SubscriptionRequest:
    """
    - subscription: Subscription details (request body).
    - db: Database session (dependency).
    """
    return subscribe_service.user_subscribe(db, subscription, user_id)
