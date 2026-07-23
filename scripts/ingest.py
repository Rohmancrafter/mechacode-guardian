"""
ingest.py — CLI for offline validation and explicit live ingestion.

Examples:
    python scripts/ingest.py --all --dry-run
    python scripts/ingest.py --all --live
    python scripts/ingest.py --file knowledge/synthetic/MGC-MOTOR-001.md --live

Live mode requires typing ``INGEST`` before the first network request. The
``--yes`` flag is available for an explicitly authorized non-interactive run.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

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
            "Use --dry-run for offline validation or --live for explicit "
            "Gemini embedding and Astra DB upsert."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--file",
        type=Path,
        metavar="PATH",
        help=(
            "Process one synthetic knowledge document. The file must be "
            "inside knowledge/synthetic/ and declared in manifest.json."
        ),
    )
    source_group.add_argument(
        "--all",
        action="store_true",
        dest="all_documents",
        help="Process every document declared in manifest.json.",
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Validate and preview locally without reading credentials.",
    )
    mode_group.add_argument(
        "--live",
        action="store_true",
        help="Generate Gemini embeddings and upsert them to Astra DB.",
    )

    parser.add_argument(
        "--yes",
        action="store_true",
        help=(
            "Skip the interactive INGEST confirmation in --live mode. "
            "Use only for an explicitly authorized non-interactive run."
        ),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        metavar="N",
        help="Gemini embedding batch size from 1 to 100 (default: 20).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show chunk previews and section headings in dry-run mode.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("knowledge/synthetic/manifest.json"),
        metavar="PATH",
        help="Override manifest path.",
    )
    return parser


def _print_validation_failures(report) -> None:
    print(
        "ERROR: Live ingestion aborted because validation failed.",
        file=sys.stderr,
    )
    for result in report.document_results:
        for failure in result.validation_failures:
            print(
                f"  - {result.filename}: {failure}",
                file=sys.stderr,
            )


def _confirm_live(settings, report) -> bool:
    print("")
    print("=" * 72)
    print("  LIVE INGESTION CONFIRMATION")
    print("=" * 72)
    print(f"  Files       : {len(report.document_results)}")
    print(f"  Chunks      : {report.total_chunks}")
    print(f"  Keyspace    : {settings.astra_db_keyspace}")
    print(f"  Collection  : {settings.kb_collection}")
    print(f"  Model       : {settings.embedding_model}")
    print(f"  Dimensions  : {settings.embedding_dimensions}")
    print("")
    print("  This operation will call Gemini and write to Astra DB.")
    print("  Existing matching _id values will be replaced (idempotent upsert).")
    print("=" * 72)

    if not sys.stdin.isatty():
        print(
            "ERROR: Interactive confirmation is unavailable. "
            "Re-run with --yes only if this live write is authorized.",
            file=sys.stderr,
        )
        return False

    try:
        answer = input("Type INGEST to continue: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("")
        return False
    return answer == "INGEST"


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.file is None and not args.all_documents:
        parser.error("Must specify either --file <path> or --all.")
    if not args.dry_run and not args.live:
        parser.error("Must specify exactly one mode: --dry-run or --live.")
    if args.yes and not args.live:
        parser.error("--yes can only be used together with --live.")
    if not 1 <= args.batch_size <= 100:
        parser.error("--batch-size must be between 1 and 100.")

    try:
        from backend.ingestion.path_security import PathSecurityError
        from backend.ingestion.pipeline import (
            build_ingestion_plan,
            run_dry_run,
        )
    except ImportError as exc:
        print(
            f"ERROR: Failed to import ingestion pipeline: {exc}",
            file=sys.stderr,
        )
        return 3

    try:
        if args.dry_run:
            report = run_dry_run(
                file=args.file,
                all_documents=args.all_documents,
                manifest_path=args.manifest,
                verbose=args.verbose,
            )
            return 2 if report.total_validation_failures else 0

        plan = build_ingestion_plan(
            file=args.file,
            all_documents=args.all_documents,
            manifest_path=args.manifest,
        )
        if plan.total_validation_failures:
            _print_validation_failures(plan)
            return 2

        from backend.core.config import get_settings

        settings = get_settings()

        if not args.yes and not _confirm_live(settings, plan):
            print(
                "Live ingestion cancelled. No Gemini or Astra DB call was made.",
                file=sys.stderr,
            )
            return 1

        from backend.ingestion.live import (
            format_live_report,
            run_live_ingestion,
        )

        live_report = run_live_ingestion(
            plan,
            settings,
            batch_size=args.batch_size,
        )
        print(format_live_report(live_report))
        return 0

    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"ERROR: File not found — {exc}", file=sys.stderr)
        return 2
    except PathSecurityError as exc:
        print(f"SECURITY ERROR: {exc}", file=sys.stderr)
        return 2
    except UnicodeDecodeError as exc:
        print(f"I/O ERROR: {exc}", file=sys.stderr)
        return 3
    except OSError as exc:
        label = (
            "CONFIGURATION ERROR"
            if "Required environment variable" in str(exc)
            else "I/O ERROR"
        )
        print(f"{label}: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:
        print(f"LIVE INGESTION ERROR: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
