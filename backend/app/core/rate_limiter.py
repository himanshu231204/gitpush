"""Rate limiting middleware using in-memory token bucket."""

import time
from collections import defaultdict
from fastapi import HTTPException, Request, status

from app.core.config import settings

# In-memory store: {user_id: {"tokens": float, "last_refill": float}}
_buckets: dict[int, dict] = defaultdict(lambda: {"tokens": 0, "last_refill": 0.0})

TIER_LIMITS = {
    "free": settings.rate_limit_free,
    "pro": settings.rate_limit_pro,
    "enterprise": settings.rate_limit_enterprise,
}


def _get_limit(tier: str) -> int:
    return TIER_LIMITS.get(tier, settings.rate_limit_free)


def check_rate_limit(user_id: int, tier: str = "free") -> None:
    """Raise 429 if the user has exceeded their per-minute rate limit."""
    limit = _get_limit(tier)
    now = time.time()
    bucket = _buckets[user_id]

    # Refill tokens (1 minute window)
    elapsed = now - bucket["last_refill"]
    if elapsed >= 60:
        bucket["tokens"] = 0
        bucket["last_refill"] = now

    if bucket["tokens"] >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded ({limit} requests/minute). Upgrade your plan for more.",
        )

    bucket["tokens"] += 1
