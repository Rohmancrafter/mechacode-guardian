"""
pipeline.py — Builds and runs the document-ingestion plan.

The planning stage is fully offline:
  manifest loading → path security validation → document loading →
  chunking → metadata annotation

``run_dry_run()`` prints the existing dry-run report.
``build_ingestion_plan()`` returns the same validated plan without printing,
so the live pipeline can reuse it before any network operation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.ingestion.chunker import chunk_markdown
from backend.ingestion.dry_run import (
    CorpusDryRunReport,
    DocumentDryRunResult,
    print_dry_run_report,
)
from backend.ingestion.loader import load_markdown
from backend.ingestion.manifest import (
    DocumentEntry,
    get_document_by_filename,
    load_manifest,
)
from backend.ingestion.metadata import annotate_chunks
from backend.ingestion.path_security import (
    PathSecurityError,
    validate_against_manifest,
    validate_corpus_path,
)


def _ingest_single(
    resolved_path: Path,
    doc_entry: DocumentEntry,
    ingested_at: str | None = None,
) -> DocumentDryRunResult:
    """Load, chunk, and annotate one validated document."""
    text = load_markdown(resolved_path)
    chunks = chunk_markdown(text)
    annotated = annotate_chunks(chunks, doc_entry, ingested_at=ingested_at)

    section_refs: list[str] = []
    seen_anchors: set[str] = set()
    for annotated_chunk in annotated:
        anchor = annotated_chunk.metadata.section_title
        if anchor and anchor not in seen_anchors:
            section_refs.append(anchor)
            seen_anchors.add(anchor)

    oversized = sum(1 for chunk in chunks if chunk.is_oversized)

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


def _process_one_file(
    requested_path: Path,
    manifest_filenames: frozenset[str],
    manifest: Any,
    workspace_root: Path | None,
    ingested_at: str | None,
) -> DocumentDryRunResult:
    """
    Validate and prepare one file.

    Validation failures are returned as a zero-chunk result so callers can
    report every invalid document without performing any network operation.
    """
    failures: list[str] = []
    placeholder_path = (
        requested_path.resolve()
        if requested_path.exists()
        else requested_path
    )

    try:
        resolved = validate_corpus_path(
            requested_path,
            workspace_root=workspace_root,
        )
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

    try:
        return _ingest_single(
            resolved,
            doc_entry,
            ingested_at=ingested_at,
        )
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


def build_ingestion_plan(
    *,
    file: Path | None = None,
    all_documents: bool = False,
    manifest_path: Path | None = None,
    workspace_root: Path | None = None,
    ingested_at: str | None = None,
) -> CorpusDryRunReport:
    """
    Build a validated, annotated ingestion plan without network access.

    This function does not load settings, read credentials, call Gemini, or
    access Astra DB.
    """
    if file is not None and all_documents:
        raise ValueError(
            "Cannot specify both --file and --all. They are mutually exclusive."
        )
    if file is None and not all_documents:
        raise ValueError("Must specify either --file <path> or --all.")

    resolved_manifest_path = (
        manifest_path
        or Path("knowledge/synthetic/manifest.json")
    )
    manifest = load_manifest(resolved_manifest_path)
    manifest_filenames = frozenset(
        document.filename
        for document in manifest.documents
    )

    results: list[DocumentDryRunResult] = []

    if file is not None:
        results.append(
            _process_one_file(
                requested_path=file,
                manifest_filenames=manifest_filenames,
                manifest=manifest,
                workspace_root=workspace_root,
                ingested_at=ingested_at,
            )
        )
    else:
        corpus_root = (
            Path("knowledge/synthetic")
            if workspace_root is None
            else workspace_root / "knowledge/synthetic"
        )
        for doc_entry in manifest.documents:
            results.append(
                _process_one_file(
                    requested_path=corpus_root / doc_entry.filename,
                    manifest_filenames=manifest_filenames,
                    manifest=manifest,
                    workspace_root=workspace_root,
                    ingested_at=ingested_at,
                )
            )

    return CorpusDryRunReport(
        document_results=results,
        total_chunks=sum(result.chunk_count for result in results),
        total_files_validated=len(results),
        total_validation_failures=sum(
            len(result.validation_failures)
            for result in results
        ),
    )


def run_dry_run(
    *,
    file: Path | None = None,
    all_documents: bool = False,
    manifest_path: Path | None = None,
    workspace_root: Path | None = None,
    verbose: bool = False,
    ingested_at: str | None = None,
) -> CorpusDryRunReport:
    """Build the offline ingestion plan and print the dry-run report."""
    report = build_ingestion_plan(
        file=file,
        all_documents=all_documents,
        manifest_path=manifest_path,
        workspace_root=workspace_root,
        ingested_at=ingested_at,
    )
    print_dry_run_report(report, verbose=verbose)
    return report
