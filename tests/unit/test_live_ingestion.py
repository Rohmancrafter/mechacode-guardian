"""Unit tests for live ingestion with no real network or database calls."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.ingestion.dry_run import (
    CorpusDryRunReport,
    DocumentDryRunResult,
)
from backend.ingestion.live import (
    LiveIngestionError,
    run_live_ingestion,
)
from backend.ingestion.metadata import AnnotatedChunk, ChunkMetadata


def _chunk(index: int) -> AnnotatedChunk:
    chunk_id = f"MGC-TEST-001::{index:04d}::hash{index:08d}"
    metadata = ChunkMetadata(
        document_id="MGC-TEST-001",
        title="Synthetic test document",
        source_file="MGC-TEST-001.md",
        version="1.0",
        language="en",
        provenance="original-synthetic",
        section_title="Test section",
        heading_stack=["Synthetic test document", "Test section"],
        chunk_id=chunk_id,
        chunk_index=index,
        content_hash=f"hash-{index}",
        safety_classification="low",
        equipment_category="sensor",
        equipment_type="synthetic sensor",
        fictional_equipment_name="MechaCo Test Sensor",
        ingested_at="2026-07-23T00:00:00Z",
    )
    return AnnotatedChunk(
        text=f"Chunk text {index}",
        metadata=metadata,
    )


def _plan(
    chunks: list[AnnotatedChunk] | None = None,
    failures: list[str] | None = None,
) -> CorpusDryRunReport:
    actual_chunks = chunks if chunks is not None else [_chunk(0), _chunk(1)]
    actual_failures = failures or []
    result = DocumentDryRunResult(
        document_id="MGC-TEST-001",
        filename="MGC-TEST-001.md",
        title="Synthetic test document",
        resolved_path=Path("knowledge/synthetic/MGC-TEST-001.md"),
        chunk_count=len(actual_chunks),
        section_references=["Test section"],
        oversized_chunks=0,
        validation_failures=actual_failures,
        annotated_chunks=actual_chunks,
    )
    return CorpusDryRunReport(
        document_results=[result],
        total_chunks=len(actual_chunks),
        total_files_validated=1,
        total_validation_failures=len(actual_failures),
    )


def _settings(dimensions: int = 3):
    return SimpleNamespace(
        google_ai_api_key="unit-test-key",
        astra_db_token="unit-test-token",
        astra_db_api_endpoint="https://test.astra.datastax.com",
        astra_db_keyspace="default_keyspace",
        kb_collection="mechacode_guardian_kb",
        embedding_model="gemini-embedding-001",
        embedding_dimensions=dimensions,
    )


class _FakeModels:
    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions
        self.calls: list[dict] = []

    def embed_content(self, **kwargs):
        self.calls.append(kwargs)
        embeddings = [
            SimpleNamespace(values=[0.1] * self.dimensions)
            for _ in kwargs["contents"]
        ]
        return SimpleNamespace(embeddings=embeddings)


class _FakeGeminiClient:
    def __init__(self, dimensions: int) -> None:
        self.models = _FakeModels(dimensions)


class _FakeCollection:
    def __init__(self) -> None:
        self.documents: dict[str, dict] = {}
        self.calls: list[tuple[dict, dict, bool]] = []

    def replace_one(self, filter, replacement, *, upsert=False):
        self.calls.append((filter, replacement, upsert))
        self.documents[replacement["_id"]] = replacement
        return SimpleNamespace()


def test_live_ingestion_batches_embeddings_and_upserts() -> None:
    plan = _plan([_chunk(0), _chunk(1), _chunk(2)])
    client = _FakeGeminiClient(dimensions=3)
    collection = _FakeCollection()

    report = run_live_ingestion(
        plan,
        _settings(),
        batch_size=2,
        gemini_client=client,
        collection=collection,
    )

    assert report.chunks_embedded == 3
    assert report.chunks_upserted == 3
    assert report.embedding_batches == 2
    assert len(client.models.calls) == 2
    assert len(collection.documents) == 3

    first_document = next(iter(collection.documents.values()))
    assert first_document["_id"] == first_document["chunk_id"]
    assert first_document["content"] == "Chunk text 0"
    assert first_document["embedding_model"] == "gemini-embedding-001"
    assert first_document["embedding_dimensions"] == 3
    assert len(first_document["$vector"]) == 3

    for _, _, upsert in collection.calls:
        assert upsert is True


def test_reingestion_is_idempotent_by_deterministic_id() -> None:
    plan = _plan()
    client = _FakeGeminiClient(dimensions=3)
    collection = _FakeCollection()

    run_live_ingestion(
        plan,
        _settings(),
        gemini_client=client,
        collection=collection,
    )
    run_live_ingestion(
        plan,
        _settings(),
        gemini_client=client,
        collection=collection,
    )

    assert len(collection.documents) == 2
    assert len(collection.calls) == 4


def test_validation_failure_stops_before_embedding() -> None:
    client = _FakeGeminiClient(dimensions=3)
    collection = _FakeCollection()

    with pytest.raises(
        LiveIngestionError,
        match="offline validation failed",
    ):
        run_live_ingestion(
            _plan(chunks=[], failures=["not in manifest"]),
            _settings(),
            gemini_client=client,
            collection=collection,
        )

    assert client.models.calls == []
    assert collection.calls == []


def test_unexpected_vector_dimension_stops_before_upsert() -> None:
    client = _FakeGeminiClient(dimensions=2)
    collection = _FakeCollection()

    with pytest.raises(
        LiveIngestionError,
        match="unexpected embedding dimension",
    ):
        run_live_ingestion(
            _plan(),
            _settings(dimensions=3),
            gemini_client=client,
            collection=collection,
        )

    assert collection.calls == []


@pytest.mark.parametrize("batch_size", [0, 101])
def test_invalid_batch_size_is_rejected(batch_size: int) -> None:
    with pytest.raises(ValueError, match="between 1 and 100"):
        run_live_ingestion(
            _plan(),
            _settings(),
            batch_size=batch_size,
            gemini_client=_FakeGeminiClient(dimensions=3),
            collection=_FakeCollection(),
        )
