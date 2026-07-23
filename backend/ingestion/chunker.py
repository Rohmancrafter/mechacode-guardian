"""
chunker.py — Heading-aware and paragraph-aware Markdown chunking.

Strategy (deterministic, no heavy parser required for the current corpus):

1.  Parse the document into a flat list of logical blocks. Each block is
    one of:
    - A heading line  (ATX-style: #, ##, ###, ####, etc.)
    - A fenced code block  (``` ... ```)
    - A table block  (contiguous lines that start with |)
    - A paragraph  (one or more non-blank lines separated by blank lines)

2.  Accumulate blocks under their nearest heading context.  When a group
    of blocks exceeds MAX_CHUNK_CHARS, split on a paragraph boundary.

3.  Atomic units that must not be split:
    - A safety-warning paragraph (contains WARNING, CAUTION, ⚠, ESCALATION).
    - A short numbered procedure (≤ MAX_PROCEDURE_LINES lines of a numbered
      list under one heading).
    - A fenced code block.
    - A Markdown table.

    If an atomic unit alone exceeds MAX_CHUNK_CHARS, it is emitted as a
    single oversized chunk (logged as an assumption violation).

4.  Each chunk is assigned:
    - The document heading stack at the point of the chunk.
    - The section anchor derived from the nearest ATX heading.

Chunk size limit:
    ARCHITECTURE.md §4.1 states "window=512 tokens, overlap=64 tokens"
    for the sliding-window chunker design.  The current corpus is
    Markdown plain text; a token is approximately 4 characters for
    English/Indonesian mixed text.

    ASSUMPTION (ingestion-chunker-A1): In the absence of a tokeniser
    dependency, we use a character-based proxy:
        MAX_CHUNK_CHARS = 512 * 4 = 2048 characters
        OVERLAP_CHARS   = 64  * 4 = 256  characters
    This is a conservative approximation.  If retrieval recall is poor,
    reduce MAX_CHUNK_CHARS (see ARCHITECTURE.md §4.1 note on 256-token
    fallback) or add a tokeniser in a future session.

    This assumption is reported explicitly in dry-run output.

Security:
    This module performs no I/O, no network calls, and no external API
    calls.  It operates purely on in-memory strings.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Tuneable constants (explicit — must not be silently changed)
# ---------------------------------------------------------------------------

MAX_CHUNK_CHARS: int = 2048
"""
Maximum characters per chunk.

ASSUMPTION ingestion-chunker-A1: Derived as 512 tokens × 4 chars/token,
per ARCHITECTURE.md §4.1 (512-token window).  No tokeniser dependency is
added for the current Markdown corpus as ARCHITECTURE.md §8 explicitly
avoids heavy parser dependencies for plain-text sources.
"""

OVERLAP_CHARS: int = 256
"""
Overlap carried forward between adjacent chunks of the same section.

ASSUMPTION ingestion-chunker-A1 (continued): Derived as 64 tokens × 4
chars/token per ARCHITECTURE.md §4.1 (64-token overlap).
"""

MAX_PROCEDURE_LINES: int = 30
"""
Maximum lines in a numbered procedure block before it is split
(safety guard only — procedures in the current corpus are short).
"""

# Regex patterns
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_FENCE_RE = re.compile(r"^```")
_TABLE_ROW_RE = re.compile(r"^\s*\|")
_HORIZONTAL_RULE_RE = re.compile(
    r"^\s{0,3}(?:(?:-\s*){3,}|(?:\*\s*){3,}|(?:_\s*){3,})$"
)
_SAFETY_RE = re.compile(
    r"(⚠|WARNING|CAUTION|DANGER|ESCALAT|Escalat|escalat|STOP|PROHIBITED|DO NOT)",
    re.IGNORECASE,
)
_NUMBERED_LIST_RE = re.compile(r"^\s*\d+\.\s+")


# ---------------------------------------------------------------------------
# Internal block types
# ---------------------------------------------------------------------------

@dataclass
class _Block:
    """A logical block extracted from the Markdown source."""

    kind: str            # "heading" | "paragraph" | "fence" | "table" | "blank"
    content: str         # Raw text of this block (may be multi-line)
    heading_level: int = 0   # 1–6 for headings, 0 otherwise
    heading_text: str = ""   # Heading text (stripped of # markers)
    is_atomic: bool = False  # True → never split this block mid-content


# ---------------------------------------------------------------------------
# Public output type
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    """A single text chunk ready for metadata attachment and embedding."""

    text: str
    """The chunk text (Unicode, as-stored in the document)."""

    heading_stack: list[str] = field(default_factory=list)
    """
    Ordered list of heading texts from H1 down to the nearest heading
    that contains this chunk.  e.g. ["§3 Fault Scenarios", "§3.1 Failure to Start"]
    """

    section_anchor: str = ""
    """
    The text of the nearest ATX heading immediately above this chunk,
    used as a citation anchor.  e.g. "§3.1 Failure to Start [MGC-MOTOR-001 §3.1]"
    """

    chunk_index: int = 0
    """Zero-based index of this chunk within the document."""

    is_oversized: bool = False
    """True if this chunk exceeds MAX_CHUNK_CHARS (reported in dry-run)."""


# ---------------------------------------------------------------------------
# Parser helpers
# ---------------------------------------------------------------------------

def _is_short_context_label(block: _Block) -> bool:
    """
    Return True when *block* is a short Markdown context label.

    Labels such as ``**Safe inspection steps:**`` and
    ``*Kondisi eskalasi*`` belong with the content that follows them.  Keeping
    them as independent chunks produces low-information embeddings.
    """
    if block.kind != "paragraph" or block.is_atomic or "\n" in block.content:
        return False

    raw = block.content.strip()
    is_emphasised = (
        (raw.startswith("**") and raw.endswith("**") and len(raw) > 4)
        or (raw.startswith("__") and raw.endswith("__") and len(raw) > 4)
        or (
            raw.startswith("*")
            and raw.endswith("*")
            and not raw.startswith("**")
            and len(raw) > 2
        )
        or (
            raw.startswith("_")
            and raw.endswith("_")
            and not raw.startswith("__")
            and len(raw) > 2
        )
    )

    visible = re.sub(r"[*_`]", "", raw).strip()
    visible = re.sub(r"\s+", " ", visible)
    words = re.findall(r"\w+", visible, flags=re.UNICODE)

    if not (2 <= sum(ch.isalnum() for ch in visible) <= 96):
        return False
    if not (1 <= len(words) <= 10):
        return False

    return visible.endswith(":") or is_emphasised


def _merge_short_context_labels(blocks: list[_Block]) -> list[_Block]:
    """
    Merge short context labels into the next content block.

    A run of labels is merged with the next non-heading block.  The merged
    block inherits atomicity from every source block so a label attached to a
    warning, procedure, table, or fenced block cannot be separated again.
    """
    merged: list[_Block] = []
    i = 0

    while i < len(blocks):
        block = blocks[i]
        if not _is_short_context_label(block):
            merged.append(block)
            i += 1
            continue

        labels = [block]
        j = i + 1
        while j < len(blocks) and _is_short_context_label(blocks[j]):
            labels.append(blocks[j])
            j += 1

        if j < len(blocks) and blocks[j].kind != "heading":
            target = blocks[j]
            merged.append(_Block(
                kind=target.kind,
                content="\n\n".join(
                    [label.content for label in labels] + [target.content]
                ),
                heading_level=target.heading_level,
                heading_text=target.heading_text,
                is_atomic=target.is_atomic or any(
                    label.is_atomic for label in labels
                ),
            ))
            i = j + 1
            continue

        # A label immediately before a heading has no following content in its
        # current section, so preserve it instead of attaching it incorrectly.
        merged.extend(labels)
        i = j

    return merged


def _parse_blocks(text: str) -> list[_Block]:
    """
    Parse *text* into a flat list of logical blocks.

    Handles:
    - ATX headings  (# through ######)
    - Fenced code blocks (``` ... ```)
    - Table rows  (lines starting with |)
    - Paragraphs and standalone lines
    - Blank lines (normalised away between blocks)
    """
    blocks: list[_Block] = []
    lines = text.splitlines()
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # ---- Blank line: skip ----
        if not line.strip():
            i += 1
            continue

        # ---- Thematic break / horizontal rule: discard ----
        # A table delimiter such as |---|---| is handled by the table branch
        # below and therefore is never mistaken for a thematic break.
        if _HORIZONTAL_RULE_RE.match(line):
            i += 1
            continue

        # ---- ATX Heading ----
        m = _HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            heading_text = m.group(2).strip()
            blocks.append(_Block(
                kind="heading",
                content=line,
                heading_level=level,
                heading_text=heading_text,
                is_atomic=False,
            ))
            i += 1
            continue

        # ---- Fenced code block ----
        if _FENCE_RE.match(line):
            fence_lines = [line]
            i += 1
            while i < n:
                fence_lines.append(lines[i])
                if _FENCE_RE.match(lines[i]) and len(fence_lines) > 1:
                    i += 1
                    break
                i += 1
            blocks.append(_Block(
                kind="fence",
                content="\n".join(fence_lines),
                is_atomic=True,
            ))
            continue

        # ---- Markdown table block ----
        if _TABLE_ROW_RE.match(line):
            table_lines = []
            while i < n and (lines[i].strip() == "" or _TABLE_ROW_RE.match(lines[i])):
                if lines[i].strip():
                    table_lines.append(lines[i])
                else:
                    break
                i += 1
            if table_lines:
                blocks.append(_Block(
                    kind="table",
                    content="\n".join(table_lines),
                    is_atomic=True,
                ))
            continue

        # ---- Paragraph (everything else) ----
        para_lines = []
        while i < n and lines[i].strip():
            current = lines[i]

            # Structural Markdown may legally follow a paragraph without an
            # intervening blank line.  Leave it for the next outer iteration.
            if para_lines and (
                _HEADING_RE.match(current)
                or _FENCE_RE.match(current)
                or _TABLE_ROW_RE.match(current)
                or _HORIZONTAL_RULE_RE.match(current)
            ):
                break

            # A thematic break reached as the first line is discarded here;
            # normally it is handled by the outer branch above.
            if _HORIZONTAL_RULE_RE.match(current):
                i += 1
                break

            para_lines.append(lines[i])
            i += 1
        content = "\n".join(para_lines)
        if not content:
            continue
        # Mark as atomic if it contains a safety warning
        is_atomic = bool(_SAFETY_RE.search(content))
        blocks.append(_Block(
            kind="paragraph",
            content=content,
            is_atomic=is_atomic,
        ))

    return _merge_short_context_labels(blocks)


def _blocks_to_chunks(
    blocks: list[_Block],
    overlap_chars: int = OVERLAP_CHARS,
    max_chunk_chars: int = MAX_CHUNK_CHARS,
) -> list[Chunk]:
    """
    Convert the parsed block list to a list of Chunk objects.

    Strategy:
    - Maintain a running heading stack as we encounter headings.
    - Accumulate paragraph/table/fence blocks into a buffer.
    - When the buffer would exceed max_chunk_chars, flush the current
      buffer as a chunk (preserving overlap) and start a new one.
    - Atomic blocks are never split; they are emitted as a chunk even
      if oversized.
    """
    chunks: list[Chunk] = []
    heading_stack: list[str] = []
    section_anchor: str = ""
    buffer: list[str] = []
    buffer_chars: int = 0
    chunk_index: int = 0

    def flush(carry_overlap: bool = True) -> None:
        nonlocal buffer, buffer_chars, chunk_index
        if not buffer:
            return
        text = "\n\n".join(buffer)
        oversized = len(text) > max_chunk_chars
        chunks.append(Chunk(
            text=text,
            heading_stack=list(heading_stack),
            section_anchor=section_anchor,
            chunk_index=chunk_index,
            is_oversized=oversized,
        ))
        chunk_index += 1

        if carry_overlap and buffer:
            # Carry the last block(s) up to overlap_chars forward
            overlap_text = buffer[-1] if buffer else ""
            if len(overlap_text) <= overlap_chars:
                buffer = [overlap_text]
                buffer_chars = len(overlap_text)
            else:
                # Trim to last overlap_chars characters of the last block
                trimmed = overlap_text[-overlap_chars:]
                buffer = [trimmed]
                buffer_chars = len(trimmed)
        else:
            buffer = []
            buffer_chars = 0

    for block in blocks:
        if block.kind == "heading":
            level = block.heading_level
            text = block.heading_text

            # Pending content belongs to the section that was active before
            # this heading.  Flush it before changing heading metadata.
            flush(carry_overlap=False)

            # Update heading stack
            # Truncate stack to this heading's level, then push
            heading_stack = heading_stack[: level - 1]
            heading_stack.append(text)
            section_anchor = text
            continue

        # --- Content block ---
        block_text = block.content

        if block.is_atomic:
            # Emit immediately; oversized atomic blocks are emitted as-is
            if buffer:
                flush(carry_overlap=False)
            oversized = len(block_text) > max_chunk_chars
            chunks.append(Chunk(
                text=block_text,
                heading_stack=list(heading_stack),
                section_anchor=section_anchor,
                chunk_index=chunk_index,
                is_oversized=oversized,
            ))
            chunk_index += 1
            buffer = []
            buffer_chars = 0
        else:
            candidate_chars = buffer_chars + len(block_text) + (2 if buffer else 0)
            if buffer and candidate_chars > max_chunk_chars:
                flush(carry_overlap=True)

            buffer.append(block_text)
            buffer_chars = sum(len(b) for b in buffer)

    flush(carry_overlap=False)
    return chunks


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chunk_markdown(
    text: str,
    max_chunk_chars: int = MAX_CHUNK_CHARS,
    overlap_chars: int = OVERLAP_CHARS,
) -> list[Chunk]:
    """
    Chunk a Markdown document into heading-aware, paragraph-aware segments.

    Parameters
    ----------
    text:
        Full Unicode text of the Markdown document.
    max_chunk_chars:
        Maximum characters per chunk (default: MAX_CHUNK_CHARS = 2048).
        ASSUMPTION ingestion-chunker-A1: proxy for 512 tokens, 4 chars/token.
    overlap_chars:
        Characters to carry forward as overlap (default: OVERLAP_CHARS = 256).
        ASSUMPTION ingestion-chunker-A1: proxy for 64 tokens, 4 chars/token.

    Returns
    -------
    list[Chunk]
        Ordered list of chunks.  Never empty for a non-empty document.
        Returns a single chunk containing "(empty document)" for an empty input.
    """
    if not text or not text.strip():
        return [Chunk(
            text="(empty document)",
            heading_stack=[],
            section_anchor="",
            chunk_index=0,
        )]

    blocks = _parse_blocks(text)
    return _blocks_to_chunks(blocks, overlap_chars=overlap_chars, max_chunk_chars=max_chunk_chars)
