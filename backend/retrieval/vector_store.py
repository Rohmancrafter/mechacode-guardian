"""Read-only Astra DB vector search for MechaCode Guardian."""

from __future__ import annotations

from typing import Any, Iterable, Protocol

from backend.core.config import Settings
from backend.core.embedding_config import EMBEDDING_CONFIG, EmbeddingConfig
from backend.core.models import Chunk


class VectorStoreError(RuntimeError):
    """Raised when Astra DB vector retrieval cannot complete safely."""


class _Collection(Protocol):
    def find(
        self,
        filter: dict[str, Any],
        *,
        projection: dict[str, bool],
        sort: dict[str, Any],
        limit: int,
        include_similarity: bool,
    ) -> Iterable[dict[str, Any]]: ...


def _get_existing_collection(settings: Settings) -> Any:
    try:
        from astrapy import DataAPIClient
    except ImportError as exc:
        raise VectorStoreError(
            "astrapy is not installed. Install backend requirements first."
        ) from exc

    client = DataAPIClient()
    database = client.get_database(
        settings.astra_db_api_endpoint,
        token=settings.astra_db_token,
        keyspace=settings.astra_db_keyspace,
    )

    collection_names = database.list_collection_names()
    if settings.kb_collection not in collection_names:
        raise VectorStoreError(
            "Knowledge-base collection does not exist: "
            f"{settings.kb_collection!r} in keyspace "
            f"{settings.astra_db_keyspace!r}."
        )

    return database.get_collection(settings.kb_collection)


def _required_text(document: dict[str, Any], field: str) -> str:
    value = document.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VectorStoreError(
            f"Astra retrieval result is missing required field {field!r}."
        )
    return value


def _to_chunk(document: dict[str, Any]) -> Chunk:
    raw_score = document.get("$similarity")
    if not isinstance(raw_score, (int, float)):
        raise VectorStoreError(
            "Astra retrieval result is missing numeric '$similarity'."
        )

    chunk_id = document.get("chunk_id") or document.get("_id")
    if not isinstance(chunk_id, str) or not chunk_id.strip():
        raise VectorStoreError(
            "Astra retrieval result is missing a valid chunk identifier."
        )

    return Chunk(
        chunk_id=chunk_id,
        text=_required_text(document, "content"),
        source_doc=_required_text(document, "document_id"),
        section_title=document.get("section_title"),
        language=str(document.get("language", "en")),
        provenance=str(document.get("provenance", "synthetic")),
        score=float(raw_score),
        source_file=document.get("source_file"),
        title=document.get("title"),
        safety_classification=document.get("safety_classification"),
        equipment_category=document.get("equipment_category"),
    )


class AstraVectorStore:
    """Run ANN similarity search against the existing Astra collection."""

    def __init__(
        self,
        settings: Settings,
        *,
        embedding_config: EmbeddingConfig = EMBEDDING_CONFIG,
        collection: _Collection | None = None,
    ) -> None:
        self._settings = settings
        self._config = embedding_config
        self._collection = collection

    def search(self, query_vector: list[float], *, top_k: int) -> list[Chunk]:
        if len(query_vector) != self._config.dimensions:
            raise ValueError(
                "Query vector dimension does not match the collection: "
                f"expected {self._config.dimensions}, "
                f"received {len(query_vector)}."
            )
        if not 1 <= top_k <= 100:
            raise ValueError("top_k must be between 1 and 100.")

        collection = (
            self._collection
            if self._collection is not None
            else _get_existing_collection(self._settings)
        )

        try:
            cursor = collection.find(
                {},
                projection={"$vector": False},
                sort={"$vector": query_vector},
                limit=top_k,
                include_similarity=True,
            )
            documents = list(cursor)
        except VectorStoreError:
            raise
        except Exception as exc:
            raise VectorStoreError(
                f"Astra DB vector search failed: {exc}"
            ) from exc

        chunks = [_to_chunk(document) for document in documents]
        chunks.sort(key=lambda chunk: chunk.score, reverse=True)
        return chunks
