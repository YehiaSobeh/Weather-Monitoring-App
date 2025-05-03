from datetime import datetime

from core.db import Base
from sqlalchemy import TIMESTAMP, Boolean, Column, String, Integer
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    surname = Column(String(255))
    email = Column(String, unique=True, index=True)
    password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    subscriptions = relationship(
        "Subscription",
        backref="user",
        cascade="all, delete"
    )
