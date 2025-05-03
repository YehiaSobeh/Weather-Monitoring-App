from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Float, Integer

from core.db import Base


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # condition_triggered = Column(Json, nullable=False)
    actual_temperature = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    is_active = Column(Boolean, default=False, nullable=False)
