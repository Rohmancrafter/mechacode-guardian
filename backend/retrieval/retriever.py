"""Orchestration and confidence policy for MechaCode retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.core.config import Settings
from backend.core.models import Chunk, ConfidenceBand


class _QueryEmbedder(Protocol):
    def embed_query(self, query: str) -> list[float]: ...


class _VectorStore(Protocol):
    def search(self, query_vector: list[float], *, top_k: int) -> list[Chunk]: ...


@dataclass(frozen=True)
class RetrievalResult:
    """Ranked evidence and the confidence decision for one query."""

    query: str
    chunks: list[Chunk]
    confidence_band: ConfidenceBand
    should_proceed: bool

    @property
    def top_score(self) -> float:
        return self.chunks[0].score if self.chunks else 0.0


class Retriever:
    """Embed a query, search Astra DB, and apply configured thresholds."""

    def __init__(
        self,
        settings: Settings,
        *,
        embedder: _QueryEmbedder,
        vector_store: _VectorStore,
    ) -> None:
        self._settings = settings
        self._embedder = embedder
        self._vector_store = vector_store

    def retrieve(
        self,
        query: str,
        *,
        top_k: int | None = None,
    ) -> RetrievalResult:
        clean_query = query.strip()
        if not clean_query:
            raise ValueError("Retrieval query must not be empty.")

        effective_top_k = (
            self._settings.retrieval_top_k if top_k is None else top_k
        )
        if not 1 <= effective_top_k <= 100:
            raise ValueError("top_k must be between 1 and 100.")

        vector = self._embedder.embed_query(clean_query)
        chunks = self._vector_store.search(
            vector,
            top_k=effective_top_k,
        )
        top_score = chunks[0].score if chunks else 0.0

        if top_score < self._settings.retrieval_score_refuse:
            confidence = ConfidenceBand.LOW
            should_proceed = False
        elif top_score < self._settings.retrieval_score_proceed:
            confidence = ConfidenceBand.MEDIUM
            should_proceed = True
        else:
            confidence = ConfidenceBand.HIGH
            should_proceed = True

        return RetrievalResult(
            query=clean_query,
            chunks=chunks,
            confidence_band=confidence,
            should_proceed=should_proceed,
        )
