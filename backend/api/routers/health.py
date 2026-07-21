"""
Health check router — GET /health.

Returns application version, environment, and stub service reachability.
No external I/O is performed at this stage; service checks are placeholders
until each integration is implemented.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.api.schemas import HealthResponse
from backend.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Application health check")
async def health() -> HealthResponse:
    """
    Returns 200 OK with application status.

    Service checks are stubs — they will be wired to real connectivity
    checks (Astra DB ping, watsonx.ai reachability) in a later session.
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version="0.1.0",
        environment=settings.environment,
        services={
            "astra_db": "not_connected",  # TODO: wire real ping in retrieval session
            "watsonx_ai": "not_connected",  # TODO: wire real ping in generation session
            "google_ai": "not_connected",   # TODO: wire real ping in embedding session
        },
    )
