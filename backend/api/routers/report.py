"""
Report router — POST /api/v1/report/{session_id}.

Foundation stub: validates the session ID parameter and returns a minimal
placeholder response. Full report assembly will be wired in Day 6.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException

from backend.api.schemas import ReportResponse

router = APIRouter(prefix="/api/v1", tags=["report"])


@router.post(
    "/report/{session_id}",
    response_model=ReportResponse,
    summary="Generate and retrieve Markdown diagnosis report",
)
async def generate_report(session_id: str) -> ReportResponse:
    """
    Assembles and returns a Markdown diagnosis report for the given session.

    Current status: foundation stub — validates UUID and returns a placeholder.
    Full report assembly from session data will be implemented on Day 6.
    """
    try:
        parsed_id = uuid.UUID(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid session_id — must be a UUID") from exc

    placeholder_md = (
        f"# MechaCode Guardian — Diagnosis Report\n\n"
        f"**Session ID:** {parsed_id}\n\n"
        f"> Report generation is not yet implemented.\n"
        f"> This is a foundation stub. Full reporting will be available after Day 6.\n"
    )

    return ReportResponse(
        session_id=parsed_id,
        markdown=placeholder_md,
        filename=f"report_{parsed_id}.md",
    )
