"""Usage tracking middleware — logs every API request."""

from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import SessionLocal
from app.core.security import decode_token
from app.core.rate_limiter import check_rate_limit
from app.models.usage import UsageLog
from app.models.user import User


class UsageTrackingMiddleware(BaseHTTPMiddleware):
    """Logs requests and enforces rate limits for authenticated users."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip docs and health
        if request.url.path in ("/docs", "/redoc", "/openapi.json", "/health"):
            return await call_next(request)

        # Try to extract user from bearer token
        user_id = None
        tier = "free"
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            try:
                payload = decode_token(auth[7:])
                if payload.get("type") == "access":
                    user_id = payload.get("sub")
            except Exception:
                pass

        # Rate limit authenticated users
        if user_id:
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    tier = user.tier
                check_rate_limit(user_id, tier)
            finally:
                db.close()

        response = await call_next(request)

        # Log usage for authenticated users
        if user_id:
            db = SessionLocal()
            try:
                log = UsageLog(
                    user_id=user_id,
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    timestamp=datetime.now(timezone.utc),
                )
                db.add(log)
                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()

        return response
