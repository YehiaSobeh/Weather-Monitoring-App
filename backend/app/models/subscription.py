from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, TIMESTAMP, Float
from sqlalchemy.orm import relationship

from core.db import Base


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    city = Column(String, nullable=False)
    temperature_threshold = Column(Float, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    alerts = relationship("Alert", backref="subscription", cascade="all, delete")
