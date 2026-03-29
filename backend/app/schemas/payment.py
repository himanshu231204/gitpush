"""Payment / subscription schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    plan: str  # pro | enterprise
    provider: str  # stripe | razorpay


class CheckoutResponse(BaseModel):
    provider: str
    checkout_url: Optional[str] = None  # Stripe
    order_id: Optional[str] = None  # Razorpay
    amount: float
    currency: str


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    provider: str
    plan: str
    status: str
    amount: float
    currency: str
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True
