from datetime import datetime

from sqlalchemy import Column, Float, Integer, String, TIMESTAMP

from core.db import Base


class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String, nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Integer, nullable=False)
    wind_speed = Column(Float, nullable=False)
    pressure = Column(Integer, nullable=True)
    fetched_at = Column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
