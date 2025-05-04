from pydantic import BaseModel


class SubscriptionRequest(BaseModel):
    city: str
    temperature_threshold: float
