from pydantic import BaseModel


class SubscriptionRequest(BaseModel):
    city: str
    condition_thresholds: float
