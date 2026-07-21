"""
manifest.py — Load and validate the synthetic knowledge corpus manifest.

Reads knowledge/synthetic/manifest.json and provides typed access to
document metadata. Raises clear errors for malformed or missing manifests.

Security: This module reads a static JSON file inside the repository.
It does not access any network resource or external credential.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Default manifest location (relative to workspace root)
# ---------------------------------------------------------------------------

DEFAULT_MANIFEST_PATH = Path("knowledge/synthetic/manifest.json")


# ---------------------------------------------------------------------------
# Typed data models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DocumentEntry:
    """A single document record as declared in manifest.json."""

    document_id: str          # e.g. "MGC-MOTOR-001"
    title: str
    filename: str             # e.g. "MGC-MOTOR-001.md"
    version: str
    language: str             # primary language code, e.g. "en"
    license: str
    provenance: str           # should always be "original-synthetic"
    equipment_type: str
    equipment_category: str
    approved_for_rag: bool
    safety_classification: str
    notes: str

    # Optional fields that may not be present on every entry
    secondary_language: str = ""
    fictional_equipment_name: str = ""


@dataclass(frozen=True)
class CorpusManifest:
    """Parsed and validated manifest for the synthetic knowledge corpus."""

    corpus_id: str
    corpus_version: str
    created: str
    author: str
    license: str
    provenance: str
    description: str
    rag_collection: str
    embedding_model: str
    embedding_dimensionality: int
    documents: tuple[DocumentEntry, ...]


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_manifest(manifest_path: Path = DEFAULT_MANIFEST_PATH) -> CorpusManifest:
    """
    Load and validate the corpus manifest from *manifest_path*.

    Raises:
        FileNotFoundError: If the manifest file does not exist.
        ValueError: If the manifest is missing required top-level keys,
            or any document entry is missing required fields.
    """
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Manifest not found: {manifest_path}. "
            "Ensure the knowledge/synthetic/ directory is present."
        )

    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Manifest is not valid JSON: {exc}") from exc

    # --- Validate top-level required fields ---
    _required_top = {
        "corpus_id", "corpus_version", "created", "author", "license",
        "provenance", "description", "rag_collection",
        "embedding_model", "embedding_dimensionality", "documents",
    }
    missing_top = _required_top - raw.keys()
    if missing_top:
        raise ValueError(
            f"Manifest is missing required top-level field(s): {sorted(missing_top)}"
        )

    if not isinstance(raw["documents"], list):
        raise ValueError("Manifest 'documents' field must be a JSON array.")

    # --- Parse document entries ---
    _required_doc = {
        "document_id", "title", "filename", "version", "language",
        "license", "provenance", "equipment_type", "equipment_category",
        "approved_for_rag", "safety_classification", "notes",
    }
    entries: list[DocumentEntry] = []
    for idx, doc in enumerate(raw["documents"]):
        missing_doc = _required_doc - doc.keys()
        if missing_doc:
            raise ValueError(
                f"Document entry #{idx} is missing required field(s): "
                f"{sorted(missing_doc)}. Entry: {doc.get('document_id', '<unknown>')}"
            )
        entries.append(
            DocumentEntry(
                document_id=doc["document_id"],
                title=doc["title"],
                filename=doc["filename"],
                version=doc["version"],
                language=doc["language"],
                license=doc["license"],
                provenance=doc["provenance"],
                equipment_type=doc["equipment_type"],
                equipment_category=doc["equipment_category"],
                approved_for_rag=bool(doc["approved_for_rag"]),
                safety_classification=doc["safety_classification"],
                notes=doc["notes"],
                secondary_language=doc.get("secondary_language", ""),
                fictional_equipment_name=doc.get("fictional_equipment_name", ""),
            )
        )

    return CorpusManifest(
        corpus_id=raw["corpus_id"],
        corpus_version=raw["corpus_version"],
        created=raw["created"],
        author=raw["author"],
        license=raw["license"],
        provenance=raw["provenance"],
        description=raw["description"],
        rag_collection=raw["rag_collection"],
        embedding_model=raw["embedding_model"],
        embedding_dimensionality=int(raw["embedding_dimensionality"]),
        documents=tuple(entries),
    )


def get_document_by_filename(
    manifest: CorpusManifest,
    filename: str,
) -> DocumentEntry | None:
    """Return the DocumentEntry whose `filename` matches *filename*, or None."""
    for doc in manifest.documents:
        if doc.filename == filename:
            return doc
    return None


def list_approved_documents(manifest: CorpusManifest) -> list[DocumentEntry]:
    """Return only documents with approved_for_rag == True."""
    return [d for d in manifest.documents if d.approved_for_rag]
