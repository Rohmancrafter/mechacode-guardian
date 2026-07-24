"""
Shared domain models (Pydantic v2) used across backend packages.

These are the canonical schemas for data flowing between modules.
API request/response schemas live in backend/api/schemas.py.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ConfidenceBand(str, Enum):
    """Three-tier confidence classification (PRD §FR-04.3, UD-02)."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Language(str, Enum):
    """Supported response languages."""

    INDONESIAN = "id"
    ENGLISH = "en"


class HazardType(str, Enum):
    """Hazard categories surfaced in escalation responses."""

    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    HYDRAULIC = "hydraulic"
    PNEUMATIC = "pneumatic"
    CHEMICAL = "chemical"
    UNKNOWN = "unknown"


class Chunk(BaseModel):
    """A single retrieved knowledge-base chunk with metadata."""

    chunk_id: str = Field(description="Unique identifier of the chunk in Astra DB")
    text: str = Field(description="Chunk text content")
    source_doc: str = Field(description="Source document name/ID")
    page_start: int | None = Field(default=None, description="Starting page number")
    page_end: int | None = Field(default=None, description="Ending page number")
    section_title: str | None = Field(default=None, description="Section heading")
    language: str = Field(default="en", description="Language of this chunk")
    provenance: str = Field(default="synthetic", description="Data provenance label")
    score: float = Field(description="Cosine similarity score from ANN search")
    source_file: str | None = Field(
        default=None,
        description="Original knowledge-base filename",
    )
    title: str | None = Field(
        default=None,
        description="Human-readable source document title",
    )
    safety_classification: str | None = Field(
        default=None,
        description="Safety classification copied from ingestion metadata",
    )
    equipment_category: str | None = Field(
        default=None,
        description="Equipment category copied from ingestion metadata",
    )


class ProbableCause(BaseModel):
    """A single probable fault cause with ranking and citation."""

    rank: int = Field(ge=1, le=3, description="Rank (1 = most likely)")
    description: str = Field(description="Plain-language cause description")
    evidence_indices: list[int] = Field(
        description="Indices into the retrieved chunks list that support this cause"
    )
    confidence_band: ConfidenceBand


class ChecklistStep(BaseModel):
    """A single inspection step in the generated checklist."""

    step_number: int
    action: str
    tool_required: str | None = None
    safety_note: str | None = Field(
        default=None,
        description=(
            "Required when step involves electrical, hydraulic, "
            "or pneumatic systems (SR-05)"
        ),
    )
    expected_outcome: str | None = None
    evidence_indices: list[int] = Field(default_factory=list)


class EscalationTrigger(BaseModel):
    """A fired safety trigger with context."""

    pattern: str
    hazard_type: HazardType
    severity: str
    matched_text: str


class SessionData(BaseModel):
    """Runtime session state accumulated during a diagnosis session."""

    session_id: UUID
    equipment_type: str
    manufacturer: str | None = None
    model: str | None = None
    alarm_code: str | None = None
    symptom_text: str
    language: Language
    retrieved_chunks: list[Chunk] = Field(default_factory=list)
    causes: list[ProbableCause] = Field(default_factory=list)
    checklist: list[ChecklistStep] = Field(default_factory=list)
    confidence_band: ConfidenceBand | None = None
    escalation_flag: bool = False
    escalation_triggers: list[EscalationTrigger] = Field(default_factory=list)
    provider_used: str = ""
    fallback_used: bool = False
    created_at: str = ""
    extra: dict[str, Any] = Field(default_factory=dict)
