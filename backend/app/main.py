"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.services import UsageTrackingMiddleware
from app.routers import auth, usage, payments

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Backend API for run-git SaaS — auth, usage tracking, payments",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Usage tracking + rate limiting
app.add_middleware(UsageTrackingMiddleware)

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(usage.router, prefix="/api")
app.include_router(payments.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
