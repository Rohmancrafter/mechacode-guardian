"""Offline regression tests for the MechaCode retrieval pipeline."""

from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

import pytest

from backend.core.config import Settings
from backend.core.embedding_config import EMBEDDING_CONFIG
from backend.core.models import Chunk, ConfidenceBand
from backend.retrieval.embedder import (
    QueryEmbedder,
    RetrievalEmbeddingError,
)
from backend.retrieval.retriever import Retriever
from backend.retrieval.vector_store import AstraVectorStore, VectorStoreError


@pytest.fixture
def settings() -> Settings:
    return Settings(
        google_ai_api_key="test-google-key",
        astra_db_token="test-astra-token",
        astra_db_api_endpoint="https://example.invalid",
    )


@pytest.fixture
def embedding_config():
    return replace(EMBEDDING_CONFIG, dimensions=3)


class FakeModels:
    def __init__(self, vector: list[float]) -> None:
        self.vector = vector
        self.calls: list[dict] = []

    def embed_content(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            embeddings=[SimpleNamespace(values=self.vector)]
        )


class FakeGemini:
    def __init__(self, vector: list[float]) -> None:
        self.models = FakeModels(vector)


def test_query_embedder_uses_query_task_type(
    monkeypatch,
    settings,
    embedding_config,
):
    client = FakeGemini([0.1, 0.2, 0.3])
    monkeypatch.setattr(
        "backend.retrieval.embedder._make_embed_config",
        lambda task_type, dimensions: {
            "task_type": task_type,
            "dimensions": dimensions,
        },
    )
    embedder = QueryEmbedder(
        settings,
        embedding_config=embedding_config,
        gemini_client=client,
    )

    vector = embedder.embed_query("  motor berhenti  ")

    assert vector == [0.1, 0.2, 0.3]
    assert client.models.calls == [
        {
            "model": "gemini-embedding-001",
            "contents": "motor berhenti",
            "config": {
                "task_type": "RETRIEVAL_QUERY",
                "dimensions": 3,
            },
        }
    ]


def test_query_embedder_rejects_empty_query(settings, embedding_config):
    embedder = QueryEmbedder(
        settings,
        embedding_config=embedding_config,
        gemini_client=FakeGemini([0.1, 0.2, 0.3]),
    )

    with pytest.raises(ValueError, match="must not be empty"):
        embedder.embed_query("   ")


def test_query_embedder_validates_dimension(
    monkeypatch,
    settings,
    embedding_config,
):
    monkeypatch.setattr(
        "backend.retrieval.embedder._make_embed_config",
        lambda *_: object(),
    )
    embedder = QueryEmbedder(
        settings,
        embedding_config=embedding_config,
        gemini_client=FakeGemini([0.1, 0.2]),
    )

    with pytest.raises(
        RetrievalEmbeddingError,
        match="expected 3, received 2",
    ):
        embedder.embed_query("motor")


class FakeCollection:
    def __init__(self, documents: list[dict]) -> None:
        self.documents = documents
        self.calls: list[dict] = []

    def find(self, filter, **kwargs):
        self.calls.append({"filter": filter, **kwargs})
        return iter(self.documents)


def _astra_document(score: float = 0.82) -> dict:
    return {
        "_id": "MGC-MOTOR-001::0001::abcdef123456",
        "chunk_id": "MGC-MOTOR-001::0001::abcdef123456",
        "content": "Inspect the motor supply and isolation state.",
        "document_id": "MGC-MOTOR-001",
        "source_file": "MGC-MOTOR-001.md",
        "title": "Motor Troubleshooting Guide",
        "section_title": "Motor does not rotate",
        "language": "en",
        "provenance": "original-synthetic",
        "equipment_category": "motor",
        "safety_classification": "high",
        "$similarity": score,
    }


def test_vector_store_runs_read_only_ann_search(
    settings,
    embedding_config,
):
    collection = FakeCollection([_astra_document()])
    store = AstraVectorStore(
        settings,
        embedding_config=embedding_config,
        collection=collection,
    )

    chunks = store.search([0.1, 0.2, 0.3], top_k=7)

    assert len(chunks) == 1
    assert chunks[0].text.startswith("Inspect the motor")
    assert chunks[0].source_doc == "MGC-MOTOR-001"
    assert chunks[0].score == pytest.approx(0.82)
    assert chunks[0].safety_classification == "high"
    assert collection.calls == [
        {
            "filter": {},
            "projection": {"$vector": False},
            "sort": {"$vector": [0.1, 0.2, 0.3]},
            "limit": 7,
            "include_similarity": True,
        }
    ]


def test_vector_store_rejects_wrong_vector_dimension(
    settings,
    embedding_config,
):
    store = AstraVectorStore(
        settings,
        embedding_config=embedding_config,
        collection=FakeCollection([]),
    )

    with pytest.raises(ValueError, match="expected 3, received 2"):
        store.search([0.1, 0.2], top_k=7)


def test_vector_store_rejects_result_without_similarity(
    settings,
    embedding_config,
):
    document = _astra_document()
    document.pop("$similarity")
    store = AstraVectorStore(
        settings,
        embedding_config=embedding_config,
        collection=FakeCollection([document]),
    )

    with pytest.raises(VectorStoreError, match="similarity"):
        store.search([0.1, 0.2, 0.3], top_k=7)


class FakeEmbedder:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def embed_query(self, query: str) -> list[float]:
        self.queries.append(query)
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    def __init__(self, score: float | None) -> None:
        self.score = score
        self.calls: list[tuple[list[float], int]] = []

    def search(self, vector: list[float], *, top_k: int) -> list[Chunk]:
        self.calls.append((vector, top_k))
        if self.score is None:
            return []
        return [
            Chunk(
                chunk_id="chunk-1",
                text="Evidence",
                source_doc="MGC-MOTOR-001",
                score=self.score,
            )
        ]


@pytest.mark.parametrize(
    ("score", "expected_band", "should_proceed"),
    [
        (0.54, ConfidenceBand.LOW, False),
        (0.55, ConfidenceBand.MEDIUM, True),
        (0.67, ConfidenceBand.MEDIUM, True),
        (0.68, ConfidenceBand.HIGH, True),
    ],
)
def test_retriever_applies_configured_thresholds(
    settings,
    score,
    expected_band,
    should_proceed,
):
    embedder = FakeEmbedder()
    store = FakeVectorStore(score)
    retriever = Retriever(
        settings,
        embedder=embedder,
        vector_store=store,
    )

    result = retriever.retrieve("  motor berhenti  ")

    assert result.query == "motor berhenti"
    assert result.confidence_band is expected_band
    assert result.should_proceed is should_proceed
    assert embedder.queries == ["motor berhenti"]
    assert store.calls == [([0.1, 0.2, 0.3], 7)]


def test_retriever_refuses_when_no_results(settings):
    retriever = Retriever(
        settings,
        embedder=FakeEmbedder(),
        vector_store=FakeVectorStore(None),
    )

    result = retriever.retrieve("unknown equipment")

    assert result.chunks == []
    assert result.top_score == 0.0
    assert result.confidence_band is ConfidenceBand.LOW
    assert result.should_proceed is False
