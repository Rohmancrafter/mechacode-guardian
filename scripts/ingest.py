"""
ingest.py — CLI script for ingesting synthetic knowledge documents.

Usage (dry-run mode — the only operational mode in this session):

    # Single document
    py -3.12 scripts/ingest.py --file knowledge/synthetic/MGC-MOTOR-001.md --dry-run

    # All documents declared in the manifest
    py -3.12 scripts/ingest.py --all --dry-run

    # With verbose chunk previews
    py -3.12 scripts/ingest.py --all --dry-run --verbose

Restrictions (enforced at runtime, non-zero exit on violation):
    - --file and --all are mutually exclusive.
    - --dry-run is required in this session (live ingestion not yet implemented).
    - Only files inside knowledge/synthetic/ are accepted.
    - Files must be declared in knowledge/synthetic/manifest.json.
    - Path traversal and symlink escapes are rejected with exit code 2.
    - Manufacturer manuals and unapproved files are rejected with exit code 2.

Exit codes:
    0   Success — dry-run completed, all documents valid.
    1   Usage error (bad arguments).
    2   Validation failure (file outside corpus, not in manifest, path traversal).
    3   I/O or parsing error (unreadable file, malformed manifest).

Security:
    No environment variables are read.
    No credentials or API keys are accessed.
    No network request is made.
    No database write is performed.

References:
    ARCHITECTURE.md §1.4 (Ingestion CLI)
    ARCHITECTURE.md §4.1 (Ingestion pipeline)
    PRD.md FR-02 (Document ingestion)
    UD-05 (knowledge/synthetic/ only for MVP)
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

# Ensure the workspace root is on sys.path so `backend` is importable
# when this script is invoked directly (e.g. py -3.12 scripts/ingest.py).
_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

# On Windows, the default console encoding may not support Unicode characters
# (e.g. ⚠, ✓, ✗).  Reconfigure stdout/stderr to UTF-8 with replacement so
# output is never lost, and special characters degrade gracefully.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ingest.py",
        description=(
            "MechaCode Guardian — Document Ingestion CLI\n\n"
            "Processes synthetic knowledge documents for the RAG pipeline.\n"
            "--file and --all are mutually exclusive.\n"
            "--dry-run is the only supported mode in the current session."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--file",
        type=Path,
        metavar="PATH",
        help=(
            "Path to a single synthetic knowledge document to process. "
            "Must be located inside knowledge/synthetic/ and declared in "
            "knowledge/synthetic/manifest.json."
        ),
    )
    source_group.add_argument(
        "--all",
        action="store_true",
        dest="all_documents",
        help=(
            "Process every document declared in "
            "knowledge/synthetic/manifest.json."
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help=(
            "Parse and chunk documents but do not write to Astra DB, "
            "call the embedding API, or make any network request. "
            "(Required in the current session — live ingestion not yet implemented.)"
        ),
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show per-chunk previews and full section headings in dry-run output.",
    )

    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("knowledge/synthetic/manifest.json"),
        metavar="PATH",
        help="Override path to manifest.json (default: knowledge/synthetic/manifest.json).",
    )

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    # --- Validate: must specify --file or --all ---
    if args.file is None and not args.all_documents:
        parser.error(
            "Must specify either --file <path> or --all. "
            "Use --help for usage."
        )
        return 1  # unreachable but explicit

    # --- Validate: --dry-run required ---
    if not args.dry_run:
        print(
            "ERROR: --dry-run is required. "
            "Live ingestion (Astra DB write + Gemini embedding) is not yet implemented. "
            "Run with --dry-run to validate and preview the ingestion pipeline.",
            file=sys.stderr,
        )
        return 1

    # --- Import ingestion pipeline (deferred to avoid import cost on bad args) ---
    try:
        from backend.ingestion.pipeline import run_dry_run
        from backend.ingestion.path_security import PathSecurityError
    except ImportError as exc:
        print(
            f"ERROR: Failed to import ingestion pipeline: {exc}\n"
            "Ensure the backend package is installed or run from the project root.",
            file=sys.stderr,
        )
        return 3

    # --- Execute ---
    try:
        report = run_dry_run(
            file=args.file,
            all_documents=args.all_documents,
            manifest_path=args.manifest,
            verbose=args.verbose,
        )
    except ValueError as exc:
        # Usage / validation errors (bad arguments, invalid manifest)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"ERROR: File not found — {exc}", file=sys.stderr)
        return 2
    except PathSecurityError as exc:
        print(f"SECURITY ERROR: {exc}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as exc:
        print(f"I/O ERROR: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:
        print(f"UNEXPECTED ERROR: {exc}", file=sys.stderr)
        return 3

    # --- Report exit code ---
    if report.total_validation_failures > 0:
        # Individual file failures were already printed in the report
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
