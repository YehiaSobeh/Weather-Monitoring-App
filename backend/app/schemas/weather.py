from datetime import datetime
from pydantic import BaseModel
 
 
class WeatherHistoryItem(BaseModel):
    city: str
    temperature: float
    humidity: int
    wind_speed: float
    pressure: int | None
    fetched_at: datetime
    updated_at: datetime