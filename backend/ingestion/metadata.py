"""
metadata.py — Deterministic metadata and chunk ID generation.

Each chunk produced by the ingestion pipeline is augmented with structured,
citation-ready metadata that satisfies:

- FR-02.3: source document name, page/section reference, section title,
           language, ingestion timestamp, provenance label ("synthetic")
- ARCHITECTURE.md §4.1 chunk tag schema:
      doc_id, source_file, section_title, language, provenance

Additional fields for evaluation and citation faithfulness:
- chunk_id        — deterministic, stable across re-ingestion runs
- content_hash    — SHA-256 of the chunk text (for duplicate detection FR-02.4)
- chunk_index     — zero-based ordinal within the document
- heading_stack   — full breadcrumb from H1 to nearest heading
- section_anchor  — nearest heading text (citation anchor)
- safety_classification — from manifest entry
- equipment_category    — from manifest entry
- fictional_equipment_name — from manifest entry (makes citations clear it is synthetic)

Chunk ID scheme (deterministic):
    chunk_id = "{document_id}::{chunk_index:04d}::{content_hash[:12]}"
    Example:  "MGC-MOTOR-001::0003::a1b2c3d4e5f6"

This scheme is:
- Stable: same content → same ID on any re-run.
- Sortable: chunk_index pads to 4 digits so lexicographic == ordinal order.
- Collision-resistant: 12 hex chars of SHA-256 provides 48-bit prefix.

Security: No network calls, no environment variable reads, no credentials.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from backend.ingestion.chunker import Chunk
from backend.ingestion.manifest import DocumentEntry


# ---------------------------------------------------------------------------
# Typed output
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ChunkMetadata:
    """
    Complete, citation-ready metadata for a single ingested chunk.

    Field naming follows ARCHITECTURE.md §4.1 exactly.
    Do not rename fields without updating the Astra DB schema.
    """

    # --- Document identity ---
    document_id: str          # e.g. "MGC-MOTOR-001"
    title: str                # Document title from manifest
    source_file: str          # Filename: e.g. "MGC-MOTOR-001.md"
    version: str              # Document version from manifest
    language: str             # Primary language code
    provenance: str           # Always "original-synthetic" for this corpus

    # --- Section / heading reference ---
    section_title: str        # Nearest heading text (citation anchor)
    heading_stack: list[str]  # Full breadcrumb from H1 to nearest heading

    # --- Chunk identity ---
    chunk_id: str             # Deterministic ID (see module docstring)
    chunk_index: int          # Zero-based ordinal within the document
    content_hash: str         # SHA-256 hex of chunk text

    # --- Safety and equipment metadata (from manifest) ---
    safety_classification: str    # "low" | "moderate" | "high" | "critical"
    equipment_category: str       # e.g. "motor", "plc", "sensor"
    equipment_type: str           # Verbose description
    fictional_equipment_name: str # e.g. "MechaCo MTR-24"

    # --- Ingestion provenance ---
    ingested_at: str          # ISO-8601 UTC timestamp


@dataclass(frozen=True)
class AnnotatedChunk:
    """A chunk text paired with its full metadata."""

    text: str
    metadata: ChunkMetadata


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256_hex(text: str) -> str:
    """Return the lowercase hex SHA-256 digest of *text* (UTF-8 encoded)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _make_chunk_id(document_id: str, chunk_index: int, content_hash: str) -> str:
    """
    Build a deterministic chunk ID.

    Format: "{document_id}::{chunk_index:04d}::{content_hash[:12]}"
    """
    return f"{document_id}::{chunk_index:04d}::{content_hash[:12]}"


def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string (e.g. '2026-07-22T10:30:00Z')."""
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def annotate_chunks(
    chunks: list[Chunk],
    document_entry: DocumentEntry,
    ingested_at: str | None = None,
) -> list[AnnotatedChunk]:
    """
    Attach deterministic metadata to each chunk in *chunks*.

    Parameters
    ----------
    chunks:
        Output of ``chunker.chunk_markdown()``.
    document_entry:
        Manifest entry for the source document.
    ingested_at:
        Optional fixed timestamp (ISO-8601 UTC).  If None, uses current UTC
        time.  Pass a fixed value in tests for deterministic output.

    Returns
    -------
    list[AnnotatedChunk]
        One AnnotatedChunk per input chunk, in document order.
    """
    ts = ingested_at if ingested_at is not None else _utc_now_iso()

    annotated: list[AnnotatedChunk] = []
    for chunk in chunks:
        content_hash = _sha256_hex(chunk.text)
        chunk_id = _make_chunk_id(
            document_id=document_entry.document_id,
            chunk_index=chunk.chunk_index,
            content_hash=content_hash,
        )
        metadata = ChunkMetadata(
            document_id=document_entry.document_id,
            title=document_entry.title,
            source_file=document_entry.filename,
            version=document_entry.version,
            language=document_entry.language,
            provenance=document_entry.provenance,
            section_title=chunk.section_anchor,
            heading_stack=list(chunk.heading_stack),
            chunk_id=chunk_id,
            chunk_index=chunk.chunk_index,
            content_hash=content_hash,
            safety_classification=document_entry.safety_classification,
            equipment_category=document_entry.equipment_category,
            equipment_type=document_entry.equipment_type,
            fictional_equipment_name=document_entry.fictional_equipment_name,
            ingested_at=ts,
        )
        annotated.append(AnnotatedChunk(text=chunk.text, metadata=metadata))

    return annotated
