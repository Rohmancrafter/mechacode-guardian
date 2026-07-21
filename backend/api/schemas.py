"""
API request and response schemas (Pydantic v2).

These are the external-facing contracts for all FastAPI endpoints.
Internal domain models live in backend/core/models.py.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from backend.core.models import (
    ChecklistStep,
    ConfidenceBand,
    EscalationTrigger,
    Language,
    ProbableCause,
)

# ---------------------------------------------------------------------------
# Shared disclaimer (SR-04 — mandatory on all AI outputs)
# ---------------------------------------------------------------------------

DISCLAIMER_TEXT = (
    "This is an AI-assisted recommendation. "
    "Always verify with the applicable technical manual and qualified personnel."
)


# ---------------------------------------------------------------------------
# POST /api/v1/diagnose — request
# ---------------------------------------------------------------------------


class DiagnoseRequest(BaseModel):
    """Symptom input submitted by the technician (FR-01)."""

    equipment_type: str = Field(
        min_length=1, max_length=200, description="e.g. 'CNC Milling Machine'"
    )
    manufacturer: str | None = Field(
        default=None, max_length=200, description="Equipment manufacturer"
    )
    model: str | None = Field(
        default=None, max_length=200, description="Equipment model identifier"
    )
    alarm_code: str | None = Field(
        default=None, max_length=100, description="Displayed alarm or error code"
    )
    symptom_text: str = Field(
        min_length=5, max_length=2000,
        description="Free-text symptom description in Indonesian or English"
    )
    language: Language | None = Field(
        default=None,
        description="Preferred response language. Auto-detected if omitted."
    )


# ---------------------------------------------------------------------------
# POST /api/v1/diagnose — response
# ---------------------------------------------------------------------------


class CitationBadge(BaseModel):
    """User-facing citation reference displayed next to a cause or checklist step."""

    evidence_index: int
    source_doc: str
    page_start: int | None = None
    page_end: int | None = None
    section_title: str | None = None


class DiagnoseResponse(BaseModel):
    """Full diagnosis response returned to the frontend."""

    session_id: UUID
    language: Language
    escalation_flag: bool
    escalation_triggers: list[EscalationTrigger] = Field(default_factory=list)
    escalation_message: str | None = None

    # Present only when escalation_flag is False and refusal_flag is False
    causes: list[ProbableCause] | None = None
    checklist: list[ChecklistStep] | None = None
    confidence_band: ConfidenceBand | None = None
    citations: list[CitationBadge] | None = None

    # Present only when escalation_flag is False but confidence is too low
    refusal_flag: bool = False
    refusal_message: str | None = None

    provider_used: str = ""
    fallback_used: bool = False

    disclaimer: str = DISCLAIMER_TEXT


# ---------------------------------------------------------------------------
# POST /api/v1/report/{session_id} — response
# ---------------------------------------------------------------------------


class ReportResponse(BaseModel):
    """Markdown diagnosis report returned to the frontend for download."""

    session_id: UUID
    markdown: str
    filename: str


# ---------------------------------------------------------------------------
# GET /health — response
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    """Simple health check response."""

    status: str = "ok"
    version: str = "0.1.0"
    environment: str = "development"
    services: dict[str, Any] = Field(default_factory=dict)
