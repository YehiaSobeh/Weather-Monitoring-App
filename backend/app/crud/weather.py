from models import Weather
from sqlalchemy import desc
 
 
def get_weather_history(db, city: str) -> list[Weather]:
    return (
        db.query(Weather)
        .filter(Weather.city == city)
        .order_by(desc(Weather.fetched_at))
        .all()
    )