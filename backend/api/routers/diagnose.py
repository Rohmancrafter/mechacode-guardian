"""
Diagnose router — POST /api/v1/diagnose.

Foundation stub: validates the request schema and returns a minimal
placeholder response. The full pipeline (retrieval → safety gate →
generation) will be wired in Day 3–6 sessions.

No external service calls are made here yet.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from backend.api.schemas import DiagnoseRequest, DiagnoseResponse, DISCLAIMER_TEXT
from backend.core.models import Language

router = APIRouter(prefix="/api/v1", tags=["diagnosis"])


@router.post(
    "/diagnose",
    response_model=DiagnoseResponse,
    summary="Submit symptom description and receive diagnosis",
)
async def diagnose(request: DiagnoseRequest) -> DiagnoseResponse:
    """
    Accepts equipment context and symptom description; returns a diagnosis.

    Current status: foundation stub — returns a clearly-labelled placeholder.
    The full RAG pipeline is NOT yet implemented.
    """
    session_id = uuid.uuid4()
    detected_language = request.language or Language.INDONESIAN

    # Stub response — clearly not operational
    return DiagnoseResponse(
        session_id=session_id,
        language=detected_language,
        escalation_flag=False,
        refusal_flag=True,
        refusal_message=(
            "RAG pipeline not yet implemented. "
            "This is a foundation stub response. "
            "Full diagnosis capability will be available after Day 6."
        ),
        provider_used="stub",
        fallback_used=False,
        disclaimer=DISCLAIMER_TEXT,
    )
