"""
loader.py — Markdown document loading for the ingestion pipeline.

Reads a validated synthetic knowledge document from disk and returns its
raw Unicode text. No parsing or transformation occurs here — this module
is solely responsible for I/O.

Restrictions:
- Only files that have already passed path_security validation should be
  passed to this module.
- Does not call any network resource or external API.
- Preserves Unicode exactly as stored on disk.
"""

from __future__ import annotations

from pathlib import Path


def load_markdown(path: Path) -> str:
    """
    Read a Markdown file at *path* and return its full Unicode text content.

    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: If the file cannot be read.
        UnicodeDecodeError: If the file is not valid UTF-8.
    """
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    # All corpus documents are authored in UTF-8. Reject if encoding fails
    # rather than silently substituting replacement characters.
    return path.read_text(encoding="utf-8", errors="strict")
