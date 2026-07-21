"""
MechaCode Guardian — FastAPI application entry point.

Start with:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

Environment variables must be configured in .env before starting.
See .env.example for required variable names.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

# Load .env file before anything else so that get_settings() works.
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import health, diagnose, report
from backend.core.config import get_settings
from backend.core.logging import configure_root_logger, get_logger

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    settings = get_settings()
    configure_root_logger(settings.log_level)
    logger = get_logger(__name__)

    app = FastAPI(
        title="MechaCode Guardian API",
        description=(
            "AI-powered maintenance co-worker for mechatronics technicians. "
            "Grounds every diagnosis in ingested technical documentation."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS — allow the Vite dev server and any configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Accept"],
    )

    # Routers
    app.include_router(health.router)
    app.include_router(diagnose.router)
    app.include_router(report.router)

    logger.info(
        "MechaCode Guardian API started",
        extra={"event": "startup", "environment": settings.environment},
    )

    return app


app = create_app()
