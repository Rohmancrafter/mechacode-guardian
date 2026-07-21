"""
ingest.py — CLI script for ingesting synthetic knowledge documents into Astra DB.

Usage (after implementing ingestion pipeline on Day 2–3):
    python scripts/ingest.py --file knowledge/synthetic/MGC-MOTOR-001.md

Status: Foundation stub — CLI argument parsing is in place.
The ingestion logic (Docling parsing, chunking, embedding, Astra DB write)
will be implemented in the Day 2–3 sessions per DELIVERY_PLAN.md.

Restrictions:
- Only ingest files under knowledge/synthetic/ for MVP.
- Do NOT ingest manufacturer manuals without verified redistribution rights (UD-05).
- Do NOT modify the Astra DB capstone collection (ARCHITECTURE.md §1.3).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ingest.py",
        description="MechaCode Guardian — Document Ingestion CLI",
    )
    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Path to a synthetic knowledge document to ingest (e.g. knowledge/synthetic/MGC-MOTOR-001.md)",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="mechacode_guardian_kb",
        help="Target Astra DB collection name (default: mechacode_guardian_kb)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and chunk the document but do not write to Astra DB",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        return 1

    if not str(args.file).startswith("knowledge/synthetic"):
        # Safety guard — only synthetic knowledge files should be ingested for MVP
        print(
            f"WARNING: File is outside knowledge/synthetic/ — "
            f"only synthetic documents should be ingested for MVP (UD-05).\n"
            f"File: {args.file}",
            file=sys.stderr,
        )

    print(f"[ingest.py] Target file   : {args.file}")
    print(f"[ingest.py] Collection    : {args.collection}")
    print(f"[ingest.py] Dry-run       : {args.dry_run}")
    print(
        "[ingest.py] STATUS: Ingestion pipeline not yet implemented.\n"
        "            Implement backend/ingestion/ modules on Day 2–3 per DELIVERY_PLAN.md."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
