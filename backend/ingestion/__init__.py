"""
backend/ingestion — Document ingestion pipeline for MechaCode Guardian.

Modules
-------
manifest        Load and validate the corpus manifest (manifest.json).
path_security   Validate file paths; reject traversal and out-of-directory paths.
loader          Read Markdown documents from disk (UTF-8, no network I/O).
chunker         Heading-aware, paragraph-aware Markdown chunking.
metadata        Deterministic chunk ID and citation metadata generation.
dry_run         Human-readable dry-run summary (no DB/embedding/network calls).
pipeline        Orchestrator: wires all modules together for --dry-run mode.
"""
