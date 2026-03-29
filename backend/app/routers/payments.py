"""Payment routes — Stripe and Razorpay checkout + webhooks."""

import stripe
import razorpay
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.payment import CheckoutRequest, CheckoutResponse, SubscriptionResponse

router = APIRouter(prefix="/payments", tags=["payments"])

PLANS = {
    "pro": {"amount_usd": 9.99, "amount_inr": 799.0},
    "enterprise": {"amount_usd": 29.99, "amount_inr": 2399.0},
}


def _get_stripe_client():
    stripe.api_key = settings.stripe_secret_key
    return stripe


def _get_razorpay_client():
    return razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout(
    body: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a checkout session (Stripe) or order (Razorpay)."""
    if body.plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan. Choose 'pro' or 'enterprise'.")

    plan = PLANS[body.plan]

    if body.provider == "stripe":
        client = _get_stripe_client()
        session = client.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"run-git {body.plan.title()} Plan"},
                    "unit_amount": int(plan["amount_usd"] * 100),
                },
                "quantity": 1,
            }],
            mode="subscription",
            metadata={"user_id": str(current_user.id), "plan": body.plan},
            success_url="https://your-app.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://your-app.com/cancel",
        )
        return CheckoutResponse(
            provider="stripe",
            checkout_url=session.url,
            amount=plan["amount_usd"],
            currency="USD",
        )

    elif body.provider == "razorpay":
        client = _get_razorpay_client()
        order = client.order.create({
            "amount": int(plan["amount_inr"] * 100),
            "currency": "INR",
            "notes": {"user_id": str(current_user.id), "plan": body.plan},
        })
        return CheckoutResponse(
            provider="razorpay",
            order_id=order["id"],
            amount=plan["amount_inr"],
            currency="INR",
        )

    raise HTTPException(status_code=400, detail="Invalid provider. Choose 'stripe' or 'razorpay'.")


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = int(session["metadata"]["user_id"])
        plan = session["metadata"]["plan"]

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.tier = plan
            sub = Subscription(
                user_id=user_id,
                provider="stripe",
                provider_subscription_id=session.get("subscription"),
                plan=plan,
                status="active",
                amount=session["amount_total"] / 100,
                currency=session["currency"].upper(),
            )
            db.add(sub)
            db.commit()

    return {"status": "ok"}


@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Razorpay webhook events."""
    payload = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")

    client = _get_razorpay_client()
    try:
        client.utility.verify_webhook_signature(payload, signature, settings.razorpay_webhook_secret)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    import json
    data = json.loads(payload)
    if data.get("event") == "payment.captured":
        notes = data["payload"]["payment"]["entity"].get("notes", {})
        user_id = int(notes.get("user_id", 0))
        plan = notes.get("plan", "pro")

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.tier = plan
            sub = Subscription(
                user_id=user_id,
                provider="razorpay",
                plan=plan,
                status="active",
                amount=data["payload"]["payment"]["entity"]["amount"] / 100,
                currency="INR",
            )
            db.add(sub)
            db.commit()

    return {"status": "ok"}


@router.get("/subscriptions", response_model=list[SubscriptionResponse])
def list_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the authenticated user's subscriptions."""
    return db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
