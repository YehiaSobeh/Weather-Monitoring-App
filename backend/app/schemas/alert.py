from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    subscription_id: NotImplementedError
    actual_temperature: float
    threshold: float
    is_active: bool
