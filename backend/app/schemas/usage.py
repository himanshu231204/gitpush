"""Usage tracking schemas."""

from datetime import datetime
from pydantic import BaseModel


class UsageLogResponse(BaseModel):
    id: int
    user_id: int
    endpoint: str
    method: str
    status_code: int
    timestamp: datetime

    class Config:
        from_attributes = True


class UsageSummary(BaseModel):
    total_requests: int
    requests_today: int
    tier: str
    rate_limit: int
