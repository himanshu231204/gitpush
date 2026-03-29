"""Subscription / payment database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey

from app.core.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(20), nullable=False)  # stripe | razorpay
    provider_subscription_id = Column(String(255), nullable=True)
    plan = Column(String(20), nullable=False)  # pro | enterprise
    status = Column(String(20), default="active")  # active | cancelled | expired
    amount = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
