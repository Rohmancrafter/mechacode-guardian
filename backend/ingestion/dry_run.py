"""
dry_run.py — Dry-run corpus summary for the ingestion pipeline.

Produces a human-readable, terminal-printable summary of what a real
ingestion run would produce, without:
- Writing to Astra DB
- Calling the Gemini embedding API
- Making any network request
- Reading any environment variable or credential

The dry-run report is designed to be unambiguous: it explicitly confirms
that no database, embedding, or network operation occurred.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

from backend.ingestion.metadata import AnnotatedChunk


# ---------------------------------------------------------------------------
# Report data model
# ---------------------------------------------------------------------------

@dataclass
class DocumentDryRunResult:
    """Dry-run result for a single document."""

    document_id: str
    filename: str
    title: str
    resolved_path: Path
    chunk_count: int
    section_references: list[str]
    oversized_chunks: int
    validation_failures: list[str] = field(default_factory=list)
    annotated_chunks: list[AnnotatedChunk] = field(default_factory=list)


@dataclass
class CorpusDryRunReport:
    """Aggregate dry-run report for one or more documents."""

    document_results: list[DocumentDryRunResult]
    total_chunks: int
    total_files_validated: int
    total_validation_failures: int


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

_SEPARATOR = "=" * 72
_SUB_SEPARATOR = "-" * 72


def _format_document_result(result: DocumentDryRunResult, verbose: bool = False) -> str:
    """Format a single document's dry-run result for terminal output."""
    lines: list[str] = []
    lines.append(f"  Document   : {result.document_id}")
    lines.append(f"  Title      : {result.title}")
    lines.append(f"  File       : {result.filename}")
    lines.append(f"  Resolved   : {result.resolved_path}")
    lines.append(f"  Chunks     : {result.chunk_count}")

    if result.oversized_chunks:
        lines.append(f"  ⚠ Oversized chunks (>{result.chunk_count} chars): {result.oversized_chunks}")

    if result.validation_failures:
        lines.append(f"  ✗ Validation failures: {len(result.validation_failures)}")
        for failure in result.validation_failures:
            lines.append(f"    - {failure}")
    else:
        lines.append("  ✓ Validation: passed")

    if result.section_references:
        lines.append(f"  Sections   : {len(result.section_references)} headings referenced")
        if verbose:
            for ref in result.section_references:
                lines.append(f"    § {ref}")

    if verbose and result.annotated_chunks:
        lines.append("  Chunks (preview):")
        for ac in result.annotated_chunks[:3]:
            preview = ac.text[:120].replace("\n", " ")
            lines.append(
                f"    [{ac.metadata.chunk_index:04d}] [{ac.metadata.chunk_id}] "
                f"{preview!r}…"
            )
        if len(result.annotated_chunks) > 3:
            lines.append(f"    … and {len(result.annotated_chunks) - 3} more chunks")

    return "\n".join(lines)


def format_dry_run_report(
    report: CorpusDryRunReport,
    verbose: bool = False,
) -> str:
    """
    Format the full corpus dry-run report for terminal output.

    The report explicitly confirms:
    - No embedding API was called
    - No Astra DB write occurred
    - No network request was made
    """
    lines: list[str] = []
    lines.append("")
    lines.append(_SEPARATOR)
    lines.append("  MechaCode Guardian — Ingestion Dry-Run Report")
    lines.append(_SEPARATOR)
    lines.append("")
    lines.append("  ⚠  DRY-RUN MODE — No data was written, embedded, or transmitted.")
    lines.append("     ✗ No Astra DB write performed.")
    lines.append("     ✗ No Gemini embedding API call performed.")
    lines.append("     ✗ No network request of any kind performed.")
    lines.append("     ✗ No environment variable or credential accessed.")
    lines.append("")
    lines.append(_SUB_SEPARATOR)
    lines.append("  ASSUMPTION [ingestion-chunker-A1]")
    lines.append("  Character-based chunk size proxy (no tokeniser dependency):")
    lines.append("    MAX_CHUNK_CHARS = 2048  (≈ 512 tokens × 4 chars/token)")
    lines.append("    OVERLAP_CHARS   =  256  (≈  64 tokens × 4 chars/token)")
    lines.append("  Source: ARCHITECTURE.md §4.1 (512-token window, 64-token overlap).")
    lines.append("  To use exact token counts, add a tokeniser in a future session.")
    lines.append(_SUB_SEPARATOR)
    lines.append("")

    # Per-document results
    lines.append(f"  Files validated : {report.total_files_validated}")
    lines.append(f"  Total chunks    : {report.total_chunks}")
    if report.total_validation_failures:
        lines.append(f"  ✗ Validation failures : {report.total_validation_failures}")
    else:
        lines.append("  ✓ Validation failures : 0")
    lines.append("")

    for result in report.document_results:
        lines.append(_SUB_SEPARATOR)
        lines.append(_format_document_result(result, verbose=verbose))
        lines.append("")

    lines.append(_SEPARATOR)
    lines.append("  Dry-run complete.")
    lines.append(_SEPARATOR)
    lines.append("")

    return "\n".join(lines)


def print_dry_run_report(
    report: CorpusDryRunReport,
    verbose: bool = False,
    stream=None,
) -> None:
    """Print the dry-run report to *stream* (default: stdout)."""
    if stream is None:
        stream = sys.stdout
    print(format_dry_run_report(report, verbose=verbose), file=stream)
