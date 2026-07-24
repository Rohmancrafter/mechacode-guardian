"""Gemini query embeddings for MechaCode Guardian retrieval."""

from __future__ import annotations

from typing import Any, Protocol

from backend.core.config import Settings
from backend.core.embedding_config import EMBEDDING_CONFIG, EmbeddingConfig


class RetrievalEmbeddingError(RuntimeError):
    """Raised when a retrieval query cannot be embedded safely."""


class _ModelsClient(Protocol):
    def embed_content(
        self,
        *,
        model: str,
        contents: str,
        config: Any,
    ) -> Any: ...


class _GeminiClient(Protocol):
    models: _ModelsClient


def _create_gemini_client(api_key: str) -> Any:
    try:
        from google import genai
    except ImportError as exc:
        raise RetrievalEmbeddingError(
            "google-genai is not installed. Install backend requirements first."
        ) from exc

    return genai.Client(api_key=api_key)


def _make_embed_config(task_type: str, dimensions: int) -> Any:
    try:
        from google.genai import types
    except ImportError as exc:
        raise RetrievalEmbeddingError(
            "google-genai is not installed. Install backend requirements first."
        ) from exc

    return types.EmbedContentConfig(
        task_type=task_type,
        output_dimensionality=dimensions,
    )


class QueryEmbedder:
    """Generate one Gemini embedding using the RETRIEVAL_QUERY task type."""

    def __init__(
        self,
        settings: Settings,
        *,
        embedding_config: EmbeddingConfig = EMBEDDING_CONFIG,
        gemini_client: _GeminiClient | None = None,
    ) -> None:
        self._settings = settings
        self._config = embedding_config
        self._client = gemini_client

    def embed_query(self, query: str) -> list[float]:
        clean_query = query.strip()
        if not clean_query:
            raise ValueError("Retrieval query must not be empty.")

        client = (
            self._client
            if self._client is not None
            else _create_gemini_client(self._settings.google_ai_api_key)
        )

        try:
            response = client.models.embed_content(
                model=self._config.model_name,
                contents=clean_query,
                config=_make_embed_config(
                    self._config.query_task_type,
                    self._config.dimensions,
                ),
            )
        except RetrievalEmbeddingError:
            raise
        except Exception as exc:
            raise RetrievalEmbeddingError(
                f"Gemini query embedding failed: {exc}"
            ) from exc

        embeddings = getattr(response, "embeddings", None)
        if not embeddings or len(embeddings) != 1:
            received = 0 if embeddings is None else len(embeddings)
            raise RetrievalEmbeddingError(
                "Gemini returned an unexpected number of query embeddings: "
                f"expected 1, received {received}."
            )

        values = getattr(embeddings[0], "values", None)
        if values is None:
            raise RetrievalEmbeddingError(
                "Gemini query embedding contains no vector values."
            )

        vector = [float(value) for value in values]
        if len(vector) != self._config.dimensions:
            raise RetrievalEmbeddingError(
                "Gemini returned an unexpected query embedding dimension: "
                f"expected {self._config.dimensions}, received {len(vector)}."
            )

        return vector
