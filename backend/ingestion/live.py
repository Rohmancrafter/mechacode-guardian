"""
live.py — Explicit Gemini-to-Astra DB ingestion.

This module receives an already validated offline ingestion plan, generates
Gemini embeddings in batches, and idempotently upserts each chunk into an
existing Astra DB collection.

It never creates or drops a collection and never deletes documents.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

from backend.core.config import Settings
from backend.ingestion.dry_run import CorpusDryRunReport
from backend.ingestion.metadata import AnnotatedChunk


class LiveIngestionError(RuntimeError):
    """Raised when live ingestion cannot complete safely."""


class _ModelsClient(Protocol):
    def embed_content(
        self,
        *,
        model: str,
        contents: list[str],
        config: Any,
    ) -> Any: ...


class _GeminiClient(Protocol):
    models: _ModelsClient


class _Collection(Protocol):
    def replace_one(
        self,
        filter: dict[str, Any],
        replacement: dict[str, Any],
        *,
        upsert: bool = False,
    ) -> Any: ...


@dataclass(frozen=True)
class LiveIngestionReport:
    """Summary of a completed live ingestion."""

    files_processed: int
    chunks_embedded: int
    chunks_upserted: int
    embedding_batches: int
    collection_name: str
    embedding_model: str
    embedding_dimensions: int


def _flatten_chunks(plan: CorpusDryRunReport) -> list[AnnotatedChunk]:
    if plan.total_validation_failures:
        failures = [
            failure
            for result in plan.document_results
            for failure in result.validation_failures
        ]
        details = "; ".join(failures)
        raise LiveIngestionError(
            "Live ingestion aborted because offline validation failed: "
            f"{details}"
        )

    chunks = [
        chunk
        for result in plan.document_results
        for chunk in result.annotated_chunks
    ]
    if not chunks:
        raise LiveIngestionError(
            "Live ingestion aborted because the ingestion plan has no chunks."
        )
    return chunks


def _create_gemini_client(api_key: str) -> Any:
    try:
        from google import genai
    except ImportError as exc:
        raise LiveIngestionError(
            "google-genai is not installed. "
            "Install the project ingestion dependencies first."
        ) from exc

    return genai.Client(api_key=api_key)


def _get_existing_collection(settings: Settings) -> Any:
    try:
        from astrapy import DataAPIClient
    except ImportError as exc:
        raise LiveIngestionError(
            "astrapy is not installed. "
            "Install the project ingestion dependencies first."
        ) from exc

    client = DataAPIClient()
    database = client.get_database(
        settings.astra_db_api_endpoint,
        token=settings.astra_db_token,
        keyspace=settings.astra_db_keyspace,
    )

    collection_names = database.list_collection_names()
    if settings.kb_collection not in collection_names:
        raise LiveIngestionError(
            "Target Astra DB collection does not exist: "
            f"{settings.kb_collection!r} in keyspace "
            f"{settings.astra_db_keyspace!r}. "
            "The live pipeline will not create it automatically."
        )

    return database.get_collection(settings.kb_collection)


def _embed_batch(
    client: _GeminiClient,
    texts: list[str],
    *,
    model: str,
    dimensions: int,
) -> list[list[float]]:
    try:
        from google.genai import types
    except ImportError as exc:
        raise LiveIngestionError(
            "google-genai is not installed. "
            "Install the project ingestion dependencies first."
        ) from exc

    response = client.models.embed_content(
        model=model,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=dimensions,
        ),
    )

    response_embeddings = getattr(response, "embeddings", None)
    if response_embeddings is None:
        raise LiveIngestionError(
            "Gemini returned no embeddings."
        )

    vectors: list[list[float]] = []
    for index, embedding in enumerate(response_embeddings):
        values = getattr(embedding, "values", None)
        if values is None:
            raise LiveIngestionError(
                f"Gemini embedding {index} has no vector values."
            )

        vector = [float(value) for value in values]
        if len(vector) != dimensions:
            raise LiveIngestionError(
                "Gemini returned an unexpected embedding dimension: "
                f"expected {dimensions}, received {len(vector)} "
                f"for batch item {index}."
            )
        vectors.append(vector)

    if len(vectors) != len(texts):
        raise LiveIngestionError(
            "Gemini returned an unexpected number of embeddings: "
            f"expected {len(texts)}, received {len(vectors)}."
        )

    return vectors


def _to_astra_document(
    chunk: AnnotatedChunk,
    vector: list[float],
    *,
    embedding_model: str,
    embedding_dimensions: int,
) -> dict[str, Any]:
    metadata = asdict(chunk.metadata)
    return {
        "_id": chunk.metadata.chunk_id,
        "content": chunk.text,
        **metadata,
        "embedding_model": embedding_model,
        "embedding_dimensions": embedding_dimensions,
        "$vector": vector,
    }


def run_live_ingestion(
    plan: CorpusDryRunReport,
    settings: Settings,
    *,
    batch_size: int = 20,
    gemini_client: _GeminiClient | None = None,
    collection: _Collection | None = None,
) -> LiveIngestionReport:
    """
    Embed and idempotently upsert every chunk in *plan*.

    Dependencies can be injected in unit tests, ensuring no real API or
    database call occurs during the test suite.
    """
    if batch_size < 1 or batch_size > 100:
        raise ValueError("batch_size must be between 1 and 100.")

    chunks = _flatten_chunks(plan)

    active_gemini_client = (
        gemini_client
        if gemini_client is not None
        else _create_gemini_client(settings.google_ai_api_key)
    )
    active_collection = (
        collection
        if collection is not None
        else _get_existing_collection(settings)
    )

    embedded_count = 0
    upserted_count = 0
    embedding_batches = 0

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        vectors = _embed_batch(
            active_gemini_client,
            [chunk.text for chunk in batch],
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
        )
        embedding_batches += 1
        embedded_count += len(vectors)

        for chunk, vector in zip(batch, vectors, strict=True):
            document = _to_astra_document(
                chunk,
                vector,
                embedding_model=settings.embedding_model,
                embedding_dimensions=settings.embedding_dimensions,
            )
            try:
                active_collection.replace_one(
                    {"_id": chunk.metadata.chunk_id},
                    document,
                    upsert=True,
                )
            except Exception as exc:
                raise LiveIngestionError(
                    "Astra DB upsert failed for chunk "
                    f"{chunk.metadata.chunk_id!r}: {exc}"
                ) from exc
            upserted_count += 1

    return LiveIngestionReport(
        files_processed=len(plan.document_results),
        chunks_embedded=embedded_count,
        chunks_upserted=upserted_count,
        embedding_batches=embedding_batches,
        collection_name=settings.kb_collection,
        embedding_model=settings.embedding_model,
        embedding_dimensions=settings.embedding_dimensions,
    )


def format_live_report(report: LiveIngestionReport) -> str:
    """Format a concise terminal summary without exposing credentials."""
    return "\n".join(
        [
            "",
            "=" * 72,
            "  MechaCode Guardian — Live Ingestion Complete",
            "=" * 72,
            f"  Files processed      : {report.files_processed}",
            f"  Chunks embedded      : {report.chunks_embedded}",
            f"  Chunks upserted      : {report.chunks_upserted}",
            f"  Embedding batches    : {report.embedding_batches}",
            f"  Collection           : {report.collection_name}",
            f"  Embedding model      : {report.embedding_model}",
            f"  Vector dimensions    : {report.embedding_dimensions}",
            "=" * 72,
            "",
        ]
    )
