"""
Read-only retrieval CLI for MechaCode Guardian.

Example:
    python scripts/retrieve.py \
        "Motor tidak berputar meskipun power supply aktif"
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
        prog="retrieve.py",
        description=(
            "MechaCode Guardian — embed one query and run read-only "
            "vector search against Astra DB."
        ),
    )
    parser.add_argument(
        "query",
        help="Technical symptom or question to search in the knowledge base.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        metavar="N",
        help="Number of results from 1 to 100 (default: configured value, 7).",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Print full chunk content instead of a 600-character preview.",
    )
    return parser


def _preview(text: str, *, full: bool) -> str:
    compact = " ".join(text.split())
    if full or len(compact) <= 600:
        return compact
    return compact[:597].rstrip() + "..."


def main() -> int:
    args = _build_parser().parse_args()

    try:
        from backend.core.config import get_settings
        from backend.retrieval.embedder import QueryEmbedder
        from backend.retrieval.retriever import Retriever
        from backend.retrieval.vector_store import AstraVectorStore

        settings = get_settings()
        retriever = Retriever(
            settings,
            embedder=QueryEmbedder(settings),
            vector_store=AstraVectorStore(settings),
        )
        result = retriever.retrieve(args.query, top_k=args.top_k)
    except ValueError as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"CONFIGURATION ERROR: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:
        print(f"RETRIEVAL ERROR: {exc}", file=sys.stderr)
        return 3

    print("")
    print("=" * 72)
    print("  MechaCode Guardian — Retrieval Result")
    print("=" * 72)
    print(f"  Query       : {result.query}")
    print(f"  Results     : {len(result.chunks)}")
    print(f"  Top score   : {result.top_score:.4f}")
    print(f"  Confidence  : {result.confidence_band.value}")
    print(
        "  Decision    : "
        + (
            "Evidence may proceed to the RAG generation stage."
            if result.should_proceed
            else "Insufficient evidence — do not generate a diagnosis."
        )
    )

    if not result.chunks:
        print("-" * 72)
        print("  No knowledge-base chunks were returned.")

    for rank, chunk in enumerate(result.chunks, start=1):
        print("-" * 72)
        print(f"  Rank        : {rank}")
        print(f"  Score       : {chunk.score:.4f}")
        print(f"  Document    : {chunk.source_doc}")
        print(f"  Source file : {chunk.source_file or '-'}")
        print(f"  Section     : {chunk.section_title or '-'}")
        print(f"  Equipment   : {chunk.equipment_category or '-'}")
        print(f"  Safety      : {chunk.safety_classification or '-'}")
        print(f"  Chunk ID    : {chunk.chunk_id}")
        print(f"  Content     : {_preview(chunk.text, full=args.full)}")

    print("=" * 72)
    return 0 if result.should_proceed else 4


if __name__ == "__main__":
    sys.exit(main())
