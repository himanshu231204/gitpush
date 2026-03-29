"""Usage tracking routes."""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.rate_limiter import check_rate_limit, TIER_LIMITS
from app.models.user import User
from app.models.usage import UsageLog
from app.schemas.usage import UsageSummary

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/summary", response_model=UsageSummary)
def usage_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return usage stats for the authenticated user."""
    total = db.query(func.count(UsageLog.id)).filter(UsageLog.user_id == current_user.id).scalar()

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today = (
        db.query(func.count(UsageLog.id))
        .filter(UsageLog.user_id == current_user.id, UsageLog.timestamp >= today_start)
        .scalar()
    )

    return UsageSummary(
        total_requests=total,
        requests_today=today,
        tier=current_user.tier,
        rate_limit=TIER_LIMITS.get(current_user.tier, TIER_LIMITS["free"]),
    )
