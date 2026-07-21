"""
pipeline.py — Orchestrates the ingestion pipeline in dry-run mode.

Wires together:
  manifest loading → path security validation → document loading →
  chunking → metadata annotation → dry-run reporting

This module does NOT:
- Call the Gemini embedding API
- Write to Astra DB
- Make any network request
- Read any environment variable or credential

The single public function ``run_dry_run()`` is called by scripts/ingest.py.
"""

from __future__ import annotations

from pathlib import Path

from backend.ingestion.chunker import chunk_markdown
from backend.ingestion.dry_run import (
    CorpusDryRunReport,
    DocumentDryRunResult,
    print_dry_run_report,
)
from backend.ingestion.loader import load_markdown
from backend.ingestion.manifest import (
    DocumentEntry,
    load_manifest,
    get_document_by_filename,
)
from backend.ingestion.metadata import annotate_chunks
from backend.ingestion.path_security import (
    PathSecurityError,
    validate_corpus_path,
    validate_against_manifest,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ingest_single(
    resolved_path: Path,
    doc_entry: DocumentEntry,
    ingested_at: str | None = None,
) -> DocumentDryRunResult:
    """
    Load, chunk, and annotate one document.  Returns a DocumentDryRunResult.

    Does not write anything; callers decide what to do with the result.
    """
    text = load_markdown(resolved_path)
    chunks = chunk_markdown(text)
    annotated = annotate_chunks(chunks, doc_entry, ingested_at=ingested_at)

    section_refs: list[str] = []
    seen_anchors: set[str] = set()
    for ac in annotated:
        anchor = ac.metadata.section_title
        if anchor and anchor not in seen_anchors:
            section_refs.append(anchor)
            seen_anchors.add(anchor)

    oversized = sum(1 for c in chunks if c.is_oversized)

    return DocumentDryRunResult(
        document_id=doc_entry.document_id,
        filename=doc_entry.filename,
        title=doc_entry.title,
        resolved_path=resolved_path,
        chunk_count=len(annotated),
        section_references=section_refs,
        oversized_chunks=oversized,
        validation_failures=[],
        annotated_chunks=annotated,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_dry_run(
    *,
    file: Path | None = None,
    all_documents: bool = False,
    manifest_path: Path | None = None,
    workspace_root: Path | None = None,
    verbose: bool = False,
    ingested_at: str | None = None,
) -> CorpusDryRunReport:
    """
    Execute the ingestion pipeline in dry-run mode.

    Parameters
    ----------
    file:
        Path to a single document to process.  Mutually exclusive with
        ``all_documents``.
    all_documents:
        If True, process every document declared in the manifest.
    manifest_path:
        Override the manifest location (default: knowledge/synthetic/manifest.json).
    workspace_root:
        Override the workspace root used for path security resolution.
    verbose:
        If True, include chunk previews in the dry-run output.
    ingested_at:
        Fixed ingestion timestamp for deterministic test output.

    Returns
    -------
    CorpusDryRunReport

    Raises
    ------
    ValueError:
        If neither ``file`` nor ``all_documents`` is set, or both are set.
    FileNotFoundError / PathSecurityError:
        Propagated from path_security or loader if a file is invalid.
    """
    if file is not None and all_documents:
        raise ValueError(
            "Cannot specify both --file and --all. They are mutually exclusive."
        )
    if file is None and not all_documents:
        raise ValueError("Must specify either --file <path> or --all.")

    # Load manifest
    mpath = manifest_path or Path("knowledge/synthetic/manifest.json")
    manifest = load_manifest(mpath)
    manifest_filenames = frozenset(d.filename for d in manifest.documents)

    results: list[DocumentDryRunResult] = []
    total_failures = 0

    if file is not None:
        # --- Single-file mode ---
        result = _process_one_file(
            requested_path=file,
            manifest_filenames=manifest_filenames,
            manifest=manifest,
            workspace_root=workspace_root,
            ingested_at=ingested_at,
        )
        results.append(result)
        total_failures += len(result.validation_failures)

    else:
        # --- All-documents mode ---
        corpus_root_path = Path("knowledge/synthetic") if workspace_root is None \
            else workspace_root / "knowledge/synthetic"

        for doc_entry in manifest.documents:
            doc_path = corpus_root_path / doc_entry.filename
            result = _process_one_file(
                requested_path=doc_path,
                manifest_filenames=manifest_filenames,
                manifest=manifest,
                workspace_root=workspace_root,
                ingested_at=ingested_at,
            )
            results.append(result)
            total_failures += len(result.validation_failures)

    total_chunks = sum(r.chunk_count for r in results)

    report = CorpusDryRunReport(
        document_results=results,
        total_chunks=total_chunks,
        total_files_validated=len(results),
        total_validation_failures=total_failures,
    )

    print_dry_run_report(report, verbose=verbose)
    return report


def _process_one_file(
    requested_path: Path,
    manifest_filenames: frozenset[str],
    manifest,
    workspace_root: Path | None,
    ingested_at: str | None,
) -> DocumentDryRunResult:
    """
    Validate and ingest a single file.

    Returns a DocumentDryRunResult.  On validation failure, the result
    includes a non-empty ``validation_failures`` list and zero chunks.
    """
    failures: list[str] = []
    placeholder_path = requested_path.resolve() if requested_path.exists() else requested_path

    # --- Path security validation ---
    try:
        resolved = validate_corpus_path(requested_path, workspace_root=workspace_root)
    except (FileNotFoundError, PathSecurityError) as exc:
        failures.append(str(exc))
        return DocumentDryRunResult(
            document_id=requested_path.stem,
            filename=requested_path.name,
            title="(unknown — validation failed)",
            resolved_path=placeholder_path,
            chunk_count=0,
            section_references=[],
            oversized_chunks=0,
            validation_failures=failures,
        )

    # --- Manifest validation ---
    try:
        validate_against_manifest(resolved, manifest_filenames)
    except PathSecurityError as exc:
        failures.append(str(exc))
        return DocumentDryRunResult(
            document_id=resolved.stem,
            filename=resolved.name,
            title="(unknown — not in manifest)",
            resolved_path=resolved,
            chunk_count=0,
            section_references=[],
            oversized_chunks=0,
            validation_failures=failures,
        )

    # --- Look up manifest entry ---
    from backend.ingestion.manifest import get_document_by_filename
    doc_entry = get_document_by_filename(manifest, resolved.name)
    if doc_entry is None:
        failures.append(
            f"Internal error: '{resolved.name}' passed manifest validation "
            "but was not found in manifest entries."
        )
        return DocumentDryRunResult(
            document_id=resolved.stem,
            filename=resolved.name,
            title="(unknown — manifest lookup failed)",
            resolved_path=resolved,
            chunk_count=0,
            section_references=[],
            oversized_chunks=0,
            validation_failures=failures,
        )

    # --- Load, chunk, annotate ---
    try:
        result = _ingest_single(resolved, doc_entry, ingested_at=ingested_at)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        failures.append(f"Ingestion error: {exc}")
        return DocumentDryRunResult(
            document_id=doc_entry.document_id,
            filename=doc_entry.filename,
            title=doc_entry.title,
            resolved_path=resolved,
            chunk_count=0,
            section_references=[],
            oversized_chunks=0,
            validation_failures=failures,
        )

    return result
