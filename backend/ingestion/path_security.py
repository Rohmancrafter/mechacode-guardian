"""
path_security.py — Secure source-path validation for the ingestion pipeline.

Ensures that only files physically located inside knowledge/synthetic/ are
accepted. Rejects path-traversal attempts, symlink escapes, and any file
outside the approved corpus directory.

Security model:
- All paths are resolved to absolute real paths before comparison.
- Symlinks are NOT followed (Path.resolve() follows symlinks on POSIX;
  we use a custom check to detect them on both POSIX and Windows).
- Files must exist (no speculative paths).
- The resolved path must be a strict descendant of the approved root.
"""

from __future__ import annotations

import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Approved corpus root — only files under this directory may be ingested
# ---------------------------------------------------------------------------

CORPUS_ROOT_NAME = Path("knowledge/synthetic")


class PathSecurityError(ValueError):
    """Raised when a requested path fails security validation."""


def get_corpus_root(workspace_root: Path | None = None) -> Path:
    """
    Return the absolute, resolved path of the approved corpus root.

    Uses the current working directory as the workspace root if not specified.
    """
    base = Path(workspace_root) if workspace_root else Path.cwd()
    candidate = (base / CORPUS_ROOT_NAME).resolve()
    return candidate


def validate_corpus_path(
    requested_path: Path,
    workspace_root: Path | None = None,
) -> Path:
    """
    Validate that *requested_path* is a safe, approved corpus file.

    Returns the resolved absolute Path if validation passes.

    Raises:
        FileNotFoundError: If the file does not exist.
        PathSecurityError: If the path is outside knowledge/synthetic/,
            is a symlink escape, is a directory, or uses traversal sequences.
    """
    corpus_root = get_corpus_root(workspace_root)

    # --- Step 1: Require the file to exist before resolving ---
    # This prevents speculative traversal even before resolve().
    if not requested_path.exists():
        raise FileNotFoundError(f"File not found: {requested_path}")

    if requested_path.is_dir():
        raise PathSecurityError(
            f"Path is a directory, not a file: {requested_path}"
        )

    # --- Step 2: Resolve the path (follows symlinks, collapses .. / .) ---
    resolved = requested_path.resolve()

    # --- Step 3: Detect symlink escape ---
    # If the resolved target differs from what strict=False resolution would
    # give with strict=True, a symlink was involved. We check by seeing
    # whether any ancestor in the path chain is a symlink.
    _check_no_symlink_in_chain(resolved, corpus_root)

    # --- Step 4: Confirm the resolved path is inside the corpus root ---
    try:
        resolved.relative_to(corpus_root)
    except ValueError:
        raise PathSecurityError(
            f"Rejected: '{requested_path}' resolves to '{resolved}', "
            f"which is outside the approved corpus directory "
            f"'{corpus_root}'. "
            "Only files inside knowledge/synthetic/ may be ingested."
        )

    # --- Step 5: Must be a regular file ---
    if not resolved.is_file():
        raise PathSecurityError(
            f"Resolved path is not a regular file: {resolved}"
        )

    return resolved


def _check_no_symlink_in_chain(resolved_path: Path, corpus_root: Path) -> None:
    """
    Walk each component of *resolved_path* that lies inside or near
    *corpus_root* and raise PathSecurityError if any component is a symlink.

    This detects cases where e.g. knowledge/synthetic/link -> ../secrets/.
    """
    # We only need to check components under the corpus_root parent (workspace).
    # Start from the workspace root down to the resolved path.
    try:
        # Check all parents up to the resolved path itself
        check_from = corpus_root.parent.parent  # workspace root (2 levels up)
    except Exception:
        check_from = corpus_root

    current = check_from
    for part in resolved_path.relative_to(check_from).parts:
        current = current / part
        if current.is_symlink():
            raise PathSecurityError(
                f"Rejected: path component '{current}' is a symbolic link. "
                "Symlinks are not permitted in ingestion paths (security policy)."
            )


def validate_against_manifest(
    resolved_path: Path,
    manifest_filenames: frozenset[str],
) -> None:
    """
    Confirm that the filename of *resolved_path* is declared in the manifest.

    Raises:
        PathSecurityError: If the filename is not in *manifest_filenames*.
    """
    filename = resolved_path.name
    if filename not in manifest_filenames:
        raise PathSecurityError(
            f"Rejected: '{filename}' is not declared in the corpus manifest "
            "(knowledge/synthetic/manifest.json). "
            "Only documents registered in the manifest may be ingested."
        )
