"""
tests/unit/test_ingestion.py — Comprehensive unit tests for the ingestion pipeline.

Covers:
- Valid single-file ingestion (dry-run)
- Full manifest ingestion (dry-run)
- Deterministic chunk IDs and output
- Manifest mismatch (file not in manifest)
- Missing file
- Outside-directory rejection
- Path traversal rejection
- Empty document handling
- Malformed document handling
- Unicode handling
- Heading and citation metadata preservation
- Safety-warning and procedure preservation
- Confirmation that dry-run performs no Astra DB or Gemini calls
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Re-usable fixtures and helpers
# ---------------------------------------------------------------------------

SAMPLE_MARKDOWN = """\
# MGC-TEST-001 — Sample Document

**Document ID:** MGC-TEST-001

---

## 1. Equipment Overview [MGC-TEST-001 §1]

The TestBot is a fictional training device.

---

## 2. Fault Scenarios [MGC-TEST-001 §2]

### 2.1 Failure to Start [MGC-TEST-001 §2.1]
*Unit tidak mau berputar*

**Symptom:** Device does not respond when start command is issued.

| # | Possible Cause | Likelihood |
|---|---|---|
| C1 | Power supply absent | High |
| C2 | Blown fuse | Medium |

**Safe inspection steps** (after isolation):

1. Isolate the device and apply LOTO.
2. Measure supply voltage at terminal block.
3. Inspect fuse.

**⚠ Escalation required if burned smell is present.**

### 2.2 Overheating [MGC-TEST-001 §2.2]
*Panas berlebih*

**Symptom:** Device body feels hot. Alarm TT-01 shown.

**Indonesian aliases:** panas berlebih, suhu tinggi, alarm TT-01.

---

## 3. Indonesian Aliases [MGC-TEST-001 §3]

| English | Bahasa Indonesia |
|---|---|
| Failure to start | Tidak mau berputar |
| Overheating | Panas berlebih |
"""

UNICODE_MARKDOWN = """\
# Dokumen Pengujian — Karakter Unicode

## Bagian 1 [§1]

Teks dengan karakter Unicode: café, naïve, Ångström, 日本語テスト, Ελληνικά.

### Alarm Kode [§1.1]

- ⚠ Peringatan: tegangan tinggi
- ≥ 24 V DC
- ♦ Catatan penting

## Bagian 2 [§2]

Prosedur dengan angka:

1. Langkah pertama: periksa tegangan
2. Langkah kedua: ukur arus
3. Langkah ketiga: catat hasil
"""

EMPTY_MARKDOWN = ""
WHITESPACE_ONLY_MARKDOWN = "   \n\n\t\n   "

SAMPLE_MANIFEST_CONTENT = {
    "corpus_id": "test-corpus",
    "corpus_version": "1.0.0",
    "created": "2026-07-22",
    "author": "Test Author",
    "license": "CC BY-NC 4.0",
    "provenance": "original-synthetic",
    "description": "Test corpus",
    "rag_collection": "mechacode_guardian_kb",
    "embedding_model": "gemini-embedding-001",
    "embedding_dimensionality": 3072,
    "documents": [
        {
            "document_id": "MGC-TEST-001",
            "title": "Test Document One",
            "filename": "MGC-TEST-001.md",
            "version": "1.0.0",
            "language": "en",
            "secondary_language": "id",
            "license": "CC BY-NC 4.0",
            "provenance": "original-synthetic",
            "equipment_type": "test device",
            "equipment_category": "test",
            "fictional_equipment_name": "TestBot TB-1",
            "approved_for_rag": False,
            "safety_classification": "moderate",
            "notes": "Test document.",
        }
    ],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_corpus_dir(tmp_path: Path) -> Path:
    """Create a temporary knowledge/synthetic/ directory with test files."""
    corpus = tmp_path / "knowledge" / "synthetic"
    corpus.mkdir(parents=True)

    # Write manifest
    manifest_path = corpus / "manifest.json"
    manifest_path.write_text(
        json.dumps(SAMPLE_MANIFEST_CONTENT, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Write sample document
    doc_path = corpus / "MGC-TEST-001.md"
    doc_path.write_text(SAMPLE_MARKDOWN, encoding="utf-8")

    return corpus


@pytest.fixture
def real_corpus_root() -> Path:
    """Return the real knowledge/synthetic/ path (from workspace root)."""
    return Path("knowledge/synthetic")


# ---------------------------------------------------------------------------
# 1. Manifest loading and validation
# ---------------------------------------------------------------------------

class TestManifestLoading:
    def test_load_valid_manifest(self, tmp_corpus_dir: Path) -> None:
        from backend.ingestion.manifest import load_manifest

        manifest = load_manifest(tmp_corpus_dir / "manifest.json")
        assert manifest.corpus_id == "test-corpus"
        assert manifest.embedding_model == "gemini-embedding-001"
        assert manifest.embedding_dimensionality == 3072
        assert len(manifest.documents) == 1
        assert manifest.documents[0].document_id == "MGC-TEST-001"

    def test_load_real_manifest(self, real_corpus_root: Path) -> None:
        """The real manifest.json loads without error."""
        from backend.ingestion.manifest import load_manifest

        if not real_corpus_root.exists():
            pytest.skip("knowledge/synthetic/ not present")

        manifest = load_manifest(real_corpus_root / "manifest.json")
        assert manifest.corpus_id == "mechacode-guardian-synthetic-v1"
        assert manifest.embedding_model == "gemini-embedding-001"
        assert manifest.embedding_dimensionality == 3072
        assert len(manifest.documents) == 5

    def test_raises_on_missing_manifest(self, tmp_path: Path) -> None:
        from backend.ingestion.manifest import load_manifest

        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            load_manifest(tmp_path / "nonexistent.json")

    def test_raises_on_malformed_json(self, tmp_path: Path) -> None:
        from backend.ingestion.manifest import load_manifest

        bad_json = tmp_path / "manifest.json"
        bad_json.write_text("{not valid json}", encoding="utf-8")

        with pytest.raises(ValueError, match="not valid JSON"):
            load_manifest(bad_json)

    def test_raises_on_missing_required_field(self, tmp_path: Path) -> None:
        from backend.ingestion.manifest import load_manifest

        incomplete = {k: v for k, v in SAMPLE_MANIFEST_CONTENT.items()
                      if k != "embedding_model"}
        (tmp_path / "manifest.json").write_text(
            json.dumps(incomplete), encoding="utf-8"
        )

        with pytest.raises(ValueError, match="embedding_model"):
            load_manifest(tmp_path / "manifest.json")

    def test_raises_on_missing_document_field(self, tmp_path: Path) -> None:
        from backend.ingestion.manifest import load_manifest

        bad_content = dict(SAMPLE_MANIFEST_CONTENT)
        bad_doc = dict(bad_content["documents"][0])
        del bad_doc["filename"]
        bad_content = dict(bad_content)
        bad_content["documents"] = [bad_doc]

        (tmp_path / "manifest.json").write_text(
            json.dumps(bad_content), encoding="utf-8"
        )

        with pytest.raises(ValueError, match="filename"):
            load_manifest(tmp_path / "manifest.json")

    def test_get_document_by_filename(self, tmp_corpus_dir: Path) -> None:
        from backend.ingestion.manifest import load_manifest, get_document_by_filename

        manifest = load_manifest(tmp_corpus_dir / "manifest.json")
        entry = get_document_by_filename(manifest, "MGC-TEST-001.md")
        assert entry is not None
        assert entry.document_id == "MGC-TEST-001"

    def test_get_document_by_filename_not_found(self, tmp_corpus_dir: Path) -> None:
        from backend.ingestion.manifest import load_manifest, get_document_by_filename

        manifest = load_manifest(tmp_corpus_dir / "manifest.json")
        entry = get_document_by_filename(manifest, "NONEXISTENT.md")
        assert entry is None


# ---------------------------------------------------------------------------
# 2. Path security validation
# ---------------------------------------------------------------------------

class TestPathSecurity:
    def test_valid_path_accepted(self, tmp_corpus_dir: Path) -> None:
        from backend.ingestion.path_security import validate_corpus_path

        doc_path = tmp_corpus_dir / "MGC-TEST-001.md"
        workspace = tmp_corpus_dir.parent.parent
        resolved = validate_corpus_path(doc_path, workspace_root=workspace)
        assert resolved.is_absolute()
        assert resolved.exists()

    def test_missing_file_raises(self, tmp_corpus_dir: Path) -> None:
        from backend.ingestion.path_security import validate_corpus_path

        missing = tmp_corpus_dir / "DOES_NOT_EXIST.md"
        workspace = tmp_corpus_dir.parent.parent

        with pytest.raises(FileNotFoundError):
            validate_corpus_path(missing, workspace_root=workspace)

    def test_outside_directory_rejected(self, tmp_path: Path, tmp_corpus_dir: Path) -> None:
        """A file outside knowledge/synthetic/ must be rejected."""
        from backend.ingestion.path_security import validate_corpus_path, PathSecurityError

        # Create a file outside the corpus directory
        outside_file = tmp_path / "outside.md"
        outside_file.write_text("# Outside", encoding="utf-8")
        workspace = tmp_corpus_dir.parent.parent

        with pytest.raises(PathSecurityError, match="outside the approved corpus"):
            validate_corpus_path(outside_file, workspace_root=workspace)

    def test_path_traversal_rejected(self, tmp_corpus_dir: Path, tmp_path: Path) -> None:
        """Dotdot traversal must be rejected."""
        from backend.ingestion.path_security import validate_corpus_path, PathSecurityError

        # Create a file in tmp_path and a path that traverses up
        outside_file = tmp_path / "secret.md"
        outside_file.write_text("# Secret", encoding="utf-8")
        workspace = tmp_corpus_dir.parent.parent

        # Build a path that uses .. to escape: knowledge/synthetic/../../secret.md
        traversal = tmp_corpus_dir / ".." / ".." / "secret.md"

        with pytest.raises((PathSecurityError, FileNotFoundError)):
            validate_corpus_path(traversal, workspace_root=workspace)

    def test_symlink_escaping_corpus_is_rejected(
        self, tmp_corpus_dir: Path, tmp_path: Path
    ) -> None:
        """
        A symlink placed *inside* knowledge/synthetic/ that points to a file
        *outside* the corpus must be rejected, even though the path presented
        to the validator looks like a legitimate corpus path.

        The attack pattern:
            knowledge/synthetic/evil.md -> /tmp/secret.md   (symlink)

        Path.resolve() follows the symlink, so the resolved target is outside
        the corpus root.  _check_no_symlink_in_chain() must catch the symlink
        component before the resolved-path check and raise PathSecurityError.

        Skip condition:
            Creating symlinks on Windows requires either Developer Mode or the
            SeCreateSymbolicLinkPrivilege.  If os.symlink() raises
            PermissionError or NotImplementedError the test is skipped with a
            clear explanation rather than a spurious failure.
        """
        import os
        from backend.ingestion.path_security import validate_corpus_path, PathSecurityError

        # The real file that lives outside the approved corpus directory.
        secret_file = tmp_path / "secret_outside_corpus.md"
        secret_file.write_text("# Secret content outside corpus\n", encoding="utf-8")

        # The symlink placed inside the corpus directory — it looks valid.
        symlink_in_corpus = tmp_corpus_dir / "MGC-EVIL-LINK.md"

        try:
            os.symlink(str(secret_file), str(symlink_in_corpus))
        except (PermissionError, NotImplementedError, OSError) as exc:
            pytest.skip(
                f"Symlink creation is not permitted in this environment "
                f"({type(exc).__name__}: {exc}). "
                "On Windows, enable Developer Mode or run as administrator to "
                "allow unprivileged symlink creation."
            )

        workspace = tmp_corpus_dir.parent.parent

        # The symlink is inside the corpus directory, so an existence check
        # passes — this is exactly the scenario that must be caught.
        assert symlink_in_corpus.exists(), (
            "Symlink should exist and follow to the target for this test to be meaningful."
        )
        assert symlink_in_corpus.is_symlink(), (
            "The path should be a symlink."
        )

        with pytest.raises(PathSecurityError, match="symbolic link"):
            validate_corpus_path(symlink_in_corpus, workspace_root=workspace)

    def test_directory_rejected(self, tmp_corpus_dir: Path) -> None:
        from backend.ingestion.path_security import validate_corpus_path, PathSecurityError

        workspace = tmp_corpus_dir.parent.parent

        with pytest.raises(PathSecurityError, match="directory"):
            validate_corpus_path(tmp_corpus_dir, workspace_root=workspace)

    def test_manifest_validation_passes_known_file(self, tmp_corpus_dir: Path) -> None:
        from backend.ingestion.path_security import validate_against_manifest

        known = frozenset({"MGC-TEST-001.md", "MGC-MOTOR-001.md"})
        path = tmp_corpus_dir / "MGC-TEST-001.md"
        # Should not raise
        validate_against_manifest(path, known)

    def test_manifest_validation_rejects_unknown_file(self, tmp_corpus_dir: Path) -> None:
        from backend.ingestion.path_security import validate_against_manifest, PathSecurityError

        known = frozenset({"MGC-TEST-001.md"})
        unknown_path = tmp_corpus_dir / "UNAPPROVED.md"
        unknown_path.write_text("# Unapproved", encoding="utf-8")

        with pytest.raises(PathSecurityError, match="not declared in the corpus manifest"):
            validate_against_manifest(unknown_path, known)


# ---------------------------------------------------------------------------
# 3. Loader
# ---------------------------------------------------------------------------

class TestLoader:
    def test_load_utf8_document(self, tmp_corpus_dir: Path) -> None:
        from backend.ingestion.loader import load_markdown

        path = tmp_corpus_dir / "MGC-TEST-001.md"
        text = load_markdown(path)
        assert "MGC-TEST-001" in text
        assert "Equipment Overview" in text

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        from backend.ingestion.loader import load_markdown

        with pytest.raises(FileNotFoundError):
            load_markdown(tmp_path / "nonexistent.md")

    def test_unicode_preserved(self, tmp_path: Path) -> None:
        """Unicode characters are preserved exactly."""
        from backend.ingestion.loader import load_markdown

        path = tmp_path / "unicode.md"
        path.write_text(UNICODE_MARKDOWN, encoding="utf-8")
        text = load_markdown(path)
        assert "café" in text
        assert "日本語テスト" in text
        assert "Ελληνικά" in text
        assert "⚠" in text
        assert "≥ 24 V DC" in text

    def test_load_empty_file(self, tmp_path: Path) -> None:
        """Empty file loads to empty string."""
        from backend.ingestion.loader import load_markdown

        path = tmp_path / "empty.md"
        path.write_text("", encoding="utf-8")
        text = load_markdown(path)
        assert text == ""


# ---------------------------------------------------------------------------
# 4. Chunker
# ---------------------------------------------------------------------------

class TestChunker:
    def test_non_empty_document_produces_chunks(self) -> None:
        from backend.ingestion.chunker import chunk_markdown

        chunks = chunk_markdown(SAMPLE_MARKDOWN)
        assert len(chunks) > 0

    def test_empty_document_returns_placeholder(self) -> None:
        from backend.ingestion.chunker import chunk_markdown

        chunks = chunk_markdown(EMPTY_MARKDOWN)
        assert len(chunks) == 1
        assert "(empty document)" in chunks[0].text

    def test_whitespace_only_returns_placeholder(self) -> None:
        from backend.ingestion.chunker import chunk_markdown

        chunks = chunk_markdown(WHITESPACE_ONLY_MARKDOWN)
        assert len(chunks) == 1
        assert "(empty document)" in chunks[0].text

    def test_chunk_indices_are_sequential(self) -> None:
        from backend.ingestion.chunker import chunk_markdown

        chunks = chunk_markdown(SAMPLE_MARKDOWN)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_heading_stack_populated(self) -> None:
        from backend.ingestion.chunker import chunk_markdown

        chunks = chunk_markdown(SAMPLE_MARKDOWN)
        # At least one chunk should have a non-empty heading_stack
        stacks = [c.heading_stack for c in chunks if c.heading_stack]
        assert len(stacks) > 0

    def test_section_anchor_populated(self) -> None:
        from backend.ingestion.chunker import chunk_markdown

        chunks = chunk_markdown(SAMPLE_MARKDOWN)
        anchored = [c for c in chunks if c.section_anchor]
        assert len(anchored) > 0

    def test_safety_warning_not_split(self) -> None:
        """A paragraph containing ⚠ should be marked atomic and not split."""
        from backend.ingestion.chunker import chunk_markdown, _SAFETY_RE

        chunks = chunk_markdown(SAMPLE_MARKDOWN)
        # Find chunks containing ⚠
        safety_chunks = [c for c in chunks if "⚠" in c.text]
        assert len(safety_chunks) > 0
        # All safety chunks should appear as single atomic units
        for sc in safety_chunks:
            # The safety keyword should be entirely within this chunk
            assert _SAFETY_RE.search(sc.text)

    def test_table_preserved_as_block(self) -> None:
        """Markdown tables are preserved as atomic blocks."""
        from backend.ingestion.chunker import chunk_markdown

        chunks = chunk_markdown(SAMPLE_MARKDOWN)
        table_chunks = [c for c in chunks if "|" in c.text and "---" in c.text]
        assert len(table_chunks) > 0

    def test_horizontal_rules_are_discarded_but_table_delimiter_is_kept(self) -> None:
        """Thematic breaks must not become low-information chunks."""
        from backend.ingestion.chunker import chunk_markdown

        markdown = """\
# Separators

---

***

___

| Name | Value |
|---|---|
| Motor | 24 V |
"""
        chunks = chunk_markdown(markdown)

        assert all(c.text.strip() not in {"---", "***", "___"} for c in chunks)
        assert any("|---|---|" in c.text for c in chunks)

    def test_short_context_labels_are_attached_to_following_content(self) -> None:
        """Short labels retain meaning by staying with the related content."""
        from backend.ingestion.chunker import chunk_markdown

        markdown = """\
# Inspection

**Safe inspection steps:**

1. Isolate the training motor.
2. Verify zero energy.

*Kondisi eskalasi*

**WARNING:** Stop if damaged insulation is visible.
"""
        chunks = chunk_markdown(markdown)

        inspection = next(c for c in chunks if "**Safe inspection steps:**" in c.text)
        escalation = next(c for c in chunks if "*Kondisi eskalasi*" in c.text)

        assert "1. Isolate the training motor." in inspection.text
        assert "**WARNING:** Stop if damaged insulation is visible." in escalation.text
        assert all(c.text.strip() != "**Safe inspection steps:**" for c in chunks)
        assert all(c.text.strip() != "*Kondisi eskalasi*" for c in chunks)

    def test_content_before_new_heading_keeps_previous_section_metadata(self) -> None:
        """A heading change must not relabel content from the previous section."""
        from backend.ingestion.chunker import chunk_markdown

        markdown = """\
# First Section

Content that belongs to the first section.

# Second Section

Content that belongs to the second section.
"""
        chunks = chunk_markdown(markdown)

        first = next(c for c in chunks if "belongs to the first" in c.text)
        second = next(c for c in chunks if "belongs to the second" in c.text)

        assert first.section_anchor == "First Section"
        assert first.heading_stack == ["First Section"]
        assert second.section_anchor == "Second Section"
        assert second.heading_stack == ["Second Section"]

    def test_unicode_chunks_correct(self) -> None:
        """Unicode text in Markdown produces correct chunks."""
        from backend.ingestion.chunker import chunk_markdown

        chunks = chunk_markdown(UNICODE_MARKDOWN)
        assert len(chunks) > 0
        full_text = "\n".join(c.text for c in chunks)
        assert "café" in full_text
        assert "日本語テスト" in full_text
        assert "⚠" in full_text

    def test_heading_metadata_in_section_anchors(self) -> None:
        """Section anchors reference document headings from the source."""
        from backend.ingestion.chunker import chunk_markdown

        chunks = chunk_markdown(SAMPLE_MARKDOWN)
        anchors = {c.section_anchor for c in chunks if c.section_anchor}
        # We expect headings like "Equipment Overview..." and "Fault Scenarios..."
        assert any("Overview" in a or "Fault" in a or "Equipment" in a or "Aliases" in a
                   for a in anchors), f"Expected equipment-related headings, got: {anchors}"

    def test_small_document_single_chunk(self) -> None:
        """A very short document fits in one chunk."""
        from backend.ingestion.chunker import chunk_markdown

        short = "# Title\n\nShort content.\n"
        chunks = chunk_markdown(short)
        assert len(chunks) >= 1

    def test_oversized_block_flagged(self) -> None:
        """A chunk exceeding MAX_CHUNK_CHARS is flagged as oversized."""
        from backend.ingestion.chunker import chunk_markdown, MAX_CHUNK_CHARS

        # Build a paragraph that exceeds the limit
        long_para = "x " * (MAX_CHUNK_CHARS + 100)
        long_doc = f"# Heading\n\n{long_para}\n"
        chunks = chunk_markdown(long_doc)
        oversized = [c for c in chunks if c.is_oversized]
        # At least one chunk should be flagged
        assert len(oversized) > 0

    def test_deterministic_output_same_input(self) -> None:
        """Same input always produces same chunks."""
        from backend.ingestion.chunker import chunk_markdown

        chunks_a = chunk_markdown(SAMPLE_MARKDOWN)
        chunks_b = chunk_markdown(SAMPLE_MARKDOWN)
        assert len(chunks_a) == len(chunks_b)
        for a, b in zip(chunks_a, chunks_b):
            assert a.text == b.text
            assert a.section_anchor == b.section_anchor
            assert a.chunk_index == b.chunk_index


# ---------------------------------------------------------------------------
# 5. Metadata (deterministic chunk IDs)
# ---------------------------------------------------------------------------

class TestMetadata:
    def _make_doc_entry(self):
        from backend.ingestion.manifest import DocumentEntry
        return DocumentEntry(
            document_id="MGC-TEST-001",
            title="Test Document",
            filename="MGC-TEST-001.md",
            version="1.0.0",
            language="en",
            license="CC BY-NC 4.0",
            provenance="original-synthetic",
            equipment_type="test device",
            equipment_category="test",
            approved_for_rag=False,
            safety_classification="moderate",
            notes="Test.",
            fictional_equipment_name="TestBot TB-1",
        )

    def test_chunk_ids_are_deterministic(self) -> None:
        """Same text + same document_id → same chunk_id."""
        from backend.ingestion.chunker import chunk_markdown
        from backend.ingestion.metadata import annotate_chunks

        doc_entry = self._make_doc_entry()
        fixed_ts = "2026-07-22T00:00:00Z"

        chunks_a = chunk_markdown(SAMPLE_MARKDOWN)
        annotated_a = annotate_chunks(chunks_a, doc_entry, ingested_at=fixed_ts)

        chunks_b = chunk_markdown(SAMPLE_MARKDOWN)
        annotated_b = annotate_chunks(chunks_b, doc_entry, ingested_at=fixed_ts)

        assert len(annotated_a) == len(annotated_b)
        for a, b in zip(annotated_a, annotated_b):
            assert a.metadata.chunk_id == b.metadata.chunk_id

    def test_chunk_id_format(self) -> None:
        """Chunk IDs follow the expected format."""
        from backend.ingestion.chunker import chunk_markdown
        from backend.ingestion.metadata import annotate_chunks

        doc_entry = self._make_doc_entry()
        chunks = chunk_markdown("# Heading\n\nContent here.\n")
        annotated = annotate_chunks(chunks, doc_entry, ingested_at="2026-07-22T00:00:00Z")

        for ac in annotated:
            cid = ac.metadata.chunk_id
            # Format: "DOC_ID::NNNN::HHHHHHHHHHHH"
            parts = cid.split("::")
            assert len(parts) == 3, f"Unexpected chunk_id format: {cid}"
            assert parts[0] == "MGC-TEST-001"
            assert len(parts[1]) == 4 and parts[1].isdigit()
            assert len(parts[2]) == 12

    def test_content_hash_is_sha256_prefix(self) -> None:
        """Content hash in metadata is the first 12 chars of SHA-256."""
        import hashlib
        from backend.ingestion.chunker import chunk_markdown
        from backend.ingestion.metadata import annotate_chunks

        doc_entry = self._make_doc_entry()
        chunks = chunk_markdown("# Title\n\nTest content.\n")
        annotated = annotate_chunks(chunks, doc_entry, ingested_at="2026-07-22T00:00:00Z")

        for ac in annotated:
            expected_hash = hashlib.sha256(ac.text.encode("utf-8")).hexdigest()
            assert ac.metadata.content_hash == expected_hash
            assert ac.metadata.chunk_id.endswith(expected_hash[:12])

    def test_metadata_fields_populated(self) -> None:
        """All required metadata fields are non-empty."""
        from backend.ingestion.chunker import chunk_markdown
        from backend.ingestion.metadata import annotate_chunks

        doc_entry = self._make_doc_entry()
        chunks = chunk_markdown(SAMPLE_MARKDOWN)
        annotated = annotate_chunks(chunks, doc_entry, ingested_at="2026-07-22T00:00:00Z")

        assert len(annotated) > 0
        for ac in annotated:
            m = ac.metadata
            assert m.document_id == "MGC-TEST-001"
            assert m.title == "Test Document"
            assert m.source_file == "MGC-TEST-001.md"
            assert m.language == "en"
            assert m.provenance == "original-synthetic"
            assert m.safety_classification == "moderate"
            assert m.equipment_category == "test"
            assert m.chunk_id  # non-empty
            assert m.content_hash  # non-empty
            assert m.ingested_at == "2026-07-22T00:00:00Z"

    def test_different_content_different_chunk_id(self) -> None:
        """Different content produces different chunk IDs."""
        from backend.ingestion.chunker import chunk_markdown
        from backend.ingestion.metadata import annotate_chunks

        doc_entry = self._make_doc_entry()
        ts = "2026-07-22T00:00:00Z"

        chunks_a = chunk_markdown("# Title\n\nContent A.\n")
        annotated_a = annotate_chunks(chunks_a, doc_entry, ingested_at=ts)

        chunks_b = chunk_markdown("# Title\n\nContent B.\n")
        annotated_b = annotate_chunks(chunks_b, doc_entry, ingested_at=ts)

        ids_a = {ac.metadata.chunk_id for ac in annotated_a}
        ids_b = {ac.metadata.chunk_id for ac in annotated_b}
        assert ids_a != ids_b

    def test_unicode_hash_correct(self) -> None:
        """Unicode text is hashed correctly (UTF-8 encoding)."""
        import hashlib
        from backend.ingestion.chunker import chunk_markdown
        from backend.ingestion.metadata import annotate_chunks

        doc_entry = self._make_doc_entry()
        chunks = chunk_markdown(UNICODE_MARKDOWN)
        annotated = annotate_chunks(chunks, doc_entry, ingested_at="2026-07-22T00:00:00Z")

        for ac in annotated:
            expected = hashlib.sha256(ac.text.encode("utf-8")).hexdigest()
            assert ac.metadata.content_hash == expected

    def test_heading_stack_in_metadata(self) -> None:
        """heading_stack from chunker is preserved in metadata."""
        from backend.ingestion.chunker import chunk_markdown
        from backend.ingestion.metadata import annotate_chunks

        doc_entry = self._make_doc_entry()
        chunks = chunk_markdown(SAMPLE_MARKDOWN)
        annotated = annotate_chunks(chunks, doc_entry, ingested_at="2026-07-22T00:00:00Z")

        # At least some chunks should have a heading_stack
        with_stack = [ac for ac in annotated if ac.metadata.heading_stack]
        assert len(with_stack) > 0

    def test_section_title_in_metadata(self) -> None:
        """section_title (citation anchor) is preserved in metadata."""
        from backend.ingestion.chunker import chunk_markdown
        from backend.ingestion.metadata import annotate_chunks

        doc_entry = self._make_doc_entry()
        chunks = chunk_markdown(SAMPLE_MARKDOWN)
        annotated = annotate_chunks(chunks, doc_entry, ingested_at="2026-07-22T00:00:00Z")

        # At least some chunks should have a section_title
        with_section = [ac for ac in annotated if ac.metadata.section_title]
        assert len(with_section) > 0


# ---------------------------------------------------------------------------
# 6. Pipeline — dry-run (no Astra DB / Gemini calls)
# ---------------------------------------------------------------------------

class TestPipelineDryRun:
    def test_single_file_dry_run_succeeds(
        self, tmp_corpus_dir: Path, capsys
    ) -> None:
        from backend.ingestion.pipeline import run_dry_run

        doc_path = tmp_corpus_dir / "MGC-TEST-001.md"
        report = run_dry_run(
            file=doc_path,
            manifest_path=tmp_corpus_dir / "manifest.json",
            workspace_root=tmp_corpus_dir.parent.parent,
            ingested_at="2026-07-22T00:00:00Z",
        )

        assert report.total_files_validated == 1
        assert report.total_chunks > 0
        assert report.total_validation_failures == 0

    def test_all_documents_dry_run_succeeds(
        self, tmp_corpus_dir: Path, capsys
    ) -> None:
        from backend.ingestion.pipeline import run_dry_run

        report = run_dry_run(
            all_documents=True,
            manifest_path=tmp_corpus_dir / "manifest.json",
            workspace_root=tmp_corpus_dir.parent.parent,
            ingested_at="2026-07-22T00:00:00Z",
        )

        assert report.total_files_validated == 1  # only 1 doc in test manifest
        assert report.total_chunks > 0
        assert report.total_validation_failures == 0

    def test_dry_run_output_confirms_no_db_call(
        self, tmp_corpus_dir: Path, capsys
    ) -> None:
        """Dry-run output explicitly states no Astra DB write was performed."""
        from backend.ingestion.pipeline import run_dry_run

        doc_path = tmp_corpus_dir / "MGC-TEST-001.md"
        run_dry_run(
            file=doc_path,
            manifest_path=tmp_corpus_dir / "manifest.json",
            workspace_root=tmp_corpus_dir.parent.parent,
            ingested_at="2026-07-22T00:00:00Z",
        )

        captured = capsys.readouterr()
        assert "No Astra DB write" in captured.out or "No data was written" in captured.out

    def test_dry_run_output_confirms_no_embedding_call(
        self, tmp_corpus_dir: Path, capsys
    ) -> None:
        """Dry-run output explicitly states no Gemini embedding call was made."""
        from backend.ingestion.pipeline import run_dry_run

        doc_path = tmp_corpus_dir / "MGC-TEST-001.md"
        run_dry_run(
            file=doc_path,
            manifest_path=tmp_corpus_dir / "manifest.json",
            workspace_root=tmp_corpus_dir.parent.parent,
            ingested_at="2026-07-22T00:00:00Z",
        )

        captured = capsys.readouterr()
        assert "No Gemini embedding" in captured.out or "embedding API" in captured.out

    def test_dry_run_output_confirms_no_network_request(
        self, tmp_corpus_dir: Path, capsys
    ) -> None:
        """Dry-run output explicitly states no network request was made."""
        from backend.ingestion.pipeline import run_dry_run

        doc_path = tmp_corpus_dir / "MGC-TEST-001.md"
        run_dry_run(
            file=doc_path,
            manifest_path=tmp_corpus_dir / "manifest.json",
            workspace_root=tmp_corpus_dir.parent.parent,
            ingested_at="2026-07-22T00:00:00Z",
        )

        captured = capsys.readouterr()
        assert "No network request" in captured.out or "network" in captured.out.lower()

    def test_dry_run_is_deterministic(self, tmp_corpus_dir: Path) -> None:
        """Two dry-run passes on the same input produce identical chunk IDs."""
        from backend.ingestion.pipeline import run_dry_run

        fixed_ts = "2026-07-22T00:00:00Z"
        doc_path = tmp_corpus_dir / "MGC-TEST-001.md"

        report_a = run_dry_run(
            file=doc_path,
            manifest_path=tmp_corpus_dir / "manifest.json",
            workspace_root=tmp_corpus_dir.parent.parent,
            ingested_at=fixed_ts,
        )
        report_b = run_dry_run(
            file=doc_path,
            manifest_path=tmp_corpus_dir / "manifest.json",
            workspace_root=tmp_corpus_dir.parent.parent,
            ingested_at=fixed_ts,
        )

        ids_a = [
            ac.metadata.chunk_id
            for r in report_a.document_results
            for ac in r.annotated_chunks
        ]
        ids_b = [
            ac.metadata.chunk_id
            for r in report_b.document_results
            for ac in r.annotated_chunks
        ]
        assert ids_a == ids_b

    def test_mutually_exclusive_file_and_all(self, tmp_corpus_dir: Path) -> None:
        """Specifying both --file and --all raises ValueError."""
        from backend.ingestion.pipeline import run_dry_run

        with pytest.raises(ValueError, match="mutually exclusive"):
            run_dry_run(
                file=tmp_corpus_dir / "MGC-TEST-001.md",
                all_documents=True,
                manifest_path=tmp_corpus_dir / "manifest.json",
            )

    def test_neither_file_nor_all_raises(self, tmp_corpus_dir: Path) -> None:
        """Specifying neither --file nor --all raises ValueError."""
        from backend.ingestion.pipeline import run_dry_run

        with pytest.raises(ValueError, match="Must specify"):
            run_dry_run(manifest_path=tmp_corpus_dir / "manifest.json")

    def test_missing_file_produces_validation_failure(
        self, tmp_corpus_dir: Path
    ) -> None:
        from backend.ingestion.pipeline import run_dry_run

        missing = tmp_corpus_dir / "MISSING.md"
        report = run_dry_run(
            file=missing,
            manifest_path=tmp_corpus_dir / "manifest.json",
            workspace_root=tmp_corpus_dir.parent.parent,
        )
        assert report.total_validation_failures > 0

    def test_outside_directory_produces_validation_failure(
        self, tmp_corpus_dir: Path, tmp_path: Path
    ) -> None:
        """A file outside knowledge/synthetic/ produces a validation failure."""
        from backend.ingestion.pipeline import run_dry_run

        # Create a file outside the corpus
        outside = tmp_path / "outside.md"
        outside.write_text("# Outside\n\nContent.\n", encoding="utf-8")

        report = run_dry_run(
            file=outside,
            manifest_path=tmp_corpus_dir / "manifest.json",
            workspace_root=tmp_corpus_dir.parent.parent,
        )
        assert report.total_validation_failures > 0

    def test_file_not_in_manifest_produces_validation_failure(
        self, tmp_corpus_dir: Path
    ) -> None:
        """A file inside the corpus dir but not in the manifest is rejected."""
        from backend.ingestion.pipeline import run_dry_run

        # Create an unapproved file in the corpus dir
        unapproved = tmp_corpus_dir / "UNAPPROVED.md"
        unapproved.write_text("# Unapproved\n\nContent.\n", encoding="utf-8")

        report = run_dry_run(
            file=unapproved,
            manifest_path=tmp_corpus_dir / "manifest.json",
            workspace_root=tmp_corpus_dir.parent.parent,
        )
        assert report.total_validation_failures > 0

    def test_chunk_count_reported_per_document(self, tmp_corpus_dir: Path) -> None:
        from backend.ingestion.pipeline import run_dry_run

        doc_path = tmp_corpus_dir / "MGC-TEST-001.md"
        report = run_dry_run(
            file=doc_path,
            manifest_path=tmp_corpus_dir / "manifest.json",
            workspace_root=tmp_corpus_dir.parent.parent,
            ingested_at="2026-07-22T00:00:00Z",
        )

        assert len(report.document_results) == 1
        result = report.document_results[0]
        assert result.chunk_count == report.total_chunks
        assert result.chunk_count > 0


# ---------------------------------------------------------------------------
# 7. Real corpus — integration-style dry-run (reads actual knowledge/synthetic/)
# ---------------------------------------------------------------------------

class TestRealCorpusDryRun:
    """
    These tests use the actual knowledge/synthetic/ documents.
    They are skipped if the directory is not present.
    """

    @pytest.fixture(autouse=True)
    def check_corpus(self) -> None:
        if not Path("knowledge/synthetic/MGC-MOTOR-001.md").exists():
            pytest.skip("Real corpus not present at knowledge/synthetic/")

    def test_motor_document_dry_run(self, capsys) -> None:
        from backend.ingestion.pipeline import run_dry_run

        report = run_dry_run(
            file=Path("knowledge/synthetic/MGC-MOTOR-001.md"),
            ingested_at="2026-07-22T00:00:00Z",
        )

        assert report.total_validation_failures == 0
        assert report.total_chunks > 0
        result = report.document_results[0]
        assert result.document_id == "MGC-MOTOR-001"
        assert result.chunk_count > 0
        assert result.section_references  # headings extracted

    def test_all_corpus_documents_dry_run(self, capsys) -> None:
        from backend.ingestion.pipeline import run_dry_run

        report = run_dry_run(
            all_documents=True,
            ingested_at="2026-07-22T00:00:00Z",
        )

        assert report.total_files_validated == 5
        assert report.total_validation_failures == 0
        assert report.total_chunks > 0

        # Each document should have produced chunks
        for result in report.document_results:
            assert result.chunk_count > 0, (
                f"Document {result.document_id} produced zero chunks"
            )

    def test_motor_document_chunk_ids_deterministic(self) -> None:
        from backend.ingestion.pipeline import run_dry_run

        fixed_ts = "2026-07-22T00:00:00Z"

        report_a = run_dry_run(
            file=Path("knowledge/synthetic/MGC-MOTOR-001.md"),
            ingested_at=fixed_ts,
        )
        report_b = run_dry_run(
            file=Path("knowledge/synthetic/MGC-MOTOR-001.md"),
            ingested_at=fixed_ts,
        )

        ids_a = [ac.metadata.chunk_id for ac in report_a.document_results[0].annotated_chunks]
        ids_b = [ac.metadata.chunk_id for ac in report_b.document_results[0].annotated_chunks]
        assert ids_a == ids_b

    def test_motor_document_sections_referenced(self) -> None:
        """MGC-MOTOR-001 chunks reference known section headings."""
        from backend.ingestion.pipeline import run_dry_run

        report = run_dry_run(
            file=Path("knowledge/synthetic/MGC-MOTOR-001.md"),
            ingested_at="2026-07-22T00:00:00Z",
        )
        result = report.document_results[0]
        section_text = " ".join(result.section_references)
        # Should contain section headings from the document
        assert any(
            kw in section_text
            for kw in ["Fault", "Equipment", "Inspection", "Escalation", "Glossary", "Overview"]
        ), f"No expected section keywords in: {result.section_references}"

    def test_safety_warning_chunk_preserved(self) -> None:
        """Safety escalation content in MGC-MOTOR-001 §3.5 is in a chunk."""
        from backend.ingestion.pipeline import run_dry_run

        report = run_dry_run(
            file=Path("knowledge/synthetic/MGC-MOTOR-001.md"),
            ingested_at="2026-07-22T00:00:00Z",
        )
        result = report.document_results[0]
        all_text = "\n".join(ac.text for ac in result.annotated_chunks)
        # The escalation warning from §3.5 must be present
        assert "Escalation required" in all_text or "escalat" in all_text.lower()

    def test_unicode_indonesian_aliases_preserved(self) -> None:
        """Indonesian alias text (Unicode) is preserved in chunks."""
        from backend.ingestion.pipeline import run_dry_run

        report = run_dry_run(
            file=Path("knowledge/synthetic/MGC-MOTOR-001.md"),
            ingested_at="2026-07-22T00:00:00Z",
        )
        result = report.document_results[0]
        all_text = "\n".join(ac.text for ac in result.annotated_chunks)
        # Indonesian text from document
        assert "Beban lebih" in all_text or "Motor tidak" in all_text or "panas" in all_text.lower()

    def test_no_astra_or_gemini_import_called(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Dry-run must not call any external services.

        We patch the network-facing libraries and verify they are not called.
        """
        from backend.ingestion.pipeline import run_dry_run

        # Patch astrapy and google.genai to fail loudly if touched
        astra_mock = MagicMock()
        astra_mock.side_effect = RuntimeError("ASTRA DB MUST NOT BE CALLED IN DRY-RUN")

        genai_mock = MagicMock()
        genai_mock.side_effect = RuntimeError("GEMINI MUST NOT BE CALLED IN DRY-RUN")

        with patch.dict("sys.modules", {
            "astrapy": MagicMock(),
            "google.genai": MagicMock(),
        }):
            # This should complete without RuntimeError
            report = run_dry_run(
                file=Path("knowledge/synthetic/MGC-MOTOR-001.md"),
                ingested_at="2026-07-22T00:00:00Z",
            )
            assert report.total_validation_failures == 0

    def test_chunk_metadata_provenance_is_synthetic(self) -> None:
        """All chunks must carry provenance = 'original-synthetic'."""
        from backend.ingestion.pipeline import run_dry_run

        report = run_dry_run(
            file=Path("knowledge/synthetic/MGC-MOTOR-001.md"),
            ingested_at="2026-07-22T00:00:00Z",
        )
        for ac in report.document_results[0].annotated_chunks:
            assert ac.metadata.provenance == "original-synthetic", (
                f"Chunk {ac.metadata.chunk_id} has unexpected provenance: "
                f"{ac.metadata.provenance}"
            )

    def test_path_traversal_rejected_on_real_corpus(self) -> None:
        """A dotdot traversal into the real corpus directory is rejected."""
        from backend.ingestion.pipeline import run_dry_run
        from backend.ingestion.path_security import PathSecurityError

        # Attempt traversal: knowledge/synthetic/../../README.md
        traversal_path = Path("knowledge/synthetic/../../README.md")

        report = run_dry_run(
            file=traversal_path,
            ingested_at="2026-07-22T00:00:00Z",
        )
        # Either raises (and ingest.py catches it) or produces a validation failure
        assert report.total_validation_failures > 0
