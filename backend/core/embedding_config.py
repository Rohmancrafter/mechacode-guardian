"""
Shared EmbeddingConfig constant (UD-03).

Both ingestion and retrieval modules import this to enforce identical
configuration.  Changing this value after ingestion invalidates the
entire vector store — do not modify without re-ingesting all documents.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingConfig:
    """
    Canonical embedding configuration (UD-03 — resolved 2026-07-20).

    - model_name: 'gemini-embedding-001'
    - dimensions: 3072
    - normalise: True  (required for cosine similarity in Astra DB)
    - ingest_task_type: 'RETRIEVAL_DOCUMENT'
    - query_task_type:  'RETRIEVAL_QUERY'
    """
    model_name: str
    dimensions: int
    normalise: bool
    ingest_task_type: str
    query_task_type: str


# Module-level singleton — import this constant everywhere
EMBEDDING_CONFIG = EmbeddingConfig(
    model_name="gemini-embedding-001",
    dimensions=3072,
    normalise=True,
    ingest_task_type="RETRIEVAL_DOCUMENT",
    query_task_type="RETRIEVAL_QUERY",
)
