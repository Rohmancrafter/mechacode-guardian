"""
Unit tests for backend/core/embedding_config.py.

Verifies that the canonical EmbeddingConfig singleton matches the values
resolved in UD-03 (2026-07-20). Changing this test output means the
embedding configuration has changed — which requires re-ingesting all
documents.
"""

from __future__ import annotations

from backend.core.embedding_config import EMBEDDING_CONFIG


class TestEmbeddingConfig:
    def test_model_name(self) -> None:
        assert EMBEDDING_CONFIG.model_name == "gemini-embedding-001"

    def test_dimensions(self) -> None:
        assert EMBEDDING_CONFIG.dimensions == 3072

    def test_normalise(self) -> None:
        assert EMBEDDING_CONFIG.normalise is True

    def test_ingest_task_type(self) -> None:
        assert EMBEDDING_CONFIG.ingest_task_type == "RETRIEVAL_DOCUMENT"

    def test_query_task_type(self) -> None:
        assert EMBEDDING_CONFIG.query_task_type == "RETRIEVAL_QUERY"
