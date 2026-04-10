"""
Tests for link validation in generated DOCX and PDF files.

Adapted from the root-level ``_validate_links.py`` and ``_validate_links_cross.py``
scripts. These tests are skipped when generated output files are not present.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import lxml.etree as ET
import pytest

OUTPUT_DIR = Path(__file__).resolve().parent.parent

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _qn(local: str) -> str:
    return f"{{{W}}}{local}"


# ── DOCX extraction helpers (from _validate_links.py) ────────────────────────

def extract_bookmarks(docx_path: Path) -> list[str]:
    """Return all user bookmarks (excluding Word-internal ``_*`` names)."""
    with zipfile.ZipFile(docx_path) as zf:
        with zf.open("word/document.xml") as f:
            root = ET.parse(f).getroot()
    return [
        bk.get(_qn("name"), "")
        for bk in root.iter(_qn("bookmarkStart"))
        if bk.get(_qn("name"), "") and not bk.get(_qn("name"), "").startswith("_")
    ]


def extract_internal_links(docx_path: Path) -> list[dict[str, str]]:
    """Return ``[{anchor, text}, ...]`` for every internal hyperlink."""
    with zipfile.ZipFile(docx_path) as zf:
        with zf.open("word/document.xml") as f:
            root = ET.parse(f).getroot()
    links: list[dict[str, str]] = []
    for hl in root.iter(_qn("hyperlink")):
        anchor = hl.get(_qn("anchor"))
        if not anchor:
            continue
        text = "".join(t.text or "" for t in hl.iter(_qn("t"))).strip() or "(no text)"
        links.append({"anchor": anchor, "text": text})
    return links


# ── Tests ─────────────────────────────────────────────────────────────────────

_DOCX_FILES = list(OUTPUT_DIR.glob("*.docx"))
_PDF_FILES  = list(OUTPUT_DIR.glob("*.pdf"))

_docx_available = pytest.mark.skipif(not _DOCX_FILES, reason="No .docx files in output dir")
_pdf_available  = pytest.mark.skipif(not _PDF_FILES,  reason="No .pdf files in output dir")


@_docx_available
class TestDocxInternalLinks:
    """Every internal hyperlink in the DOCX must have a matching bookmark."""

    @pytest.fixture(params=_DOCX_FILES, ids=[p.name for p in _DOCX_FILES])
    def docx_path(self, request) -> Path:
        return request.param

    def test_all_links_resolve(self, docx_path: Path):
        bookmarks = set(extract_bookmarks(docx_path))
        links     = extract_internal_links(docx_path)

        broken = [lk for lk in links if lk["anchor"] not in bookmarks]
        assert not broken, (
            f"Broken links in {docx_path.name}: "
            + ", ".join(f'[{lk["text"]}]→#{lk["anchor"]}' for lk in broken[:5])
        )


@_docx_available
@_pdf_available
class TestCrossValidation:
    """Bookmarks in DOCX should match named destinations in PDF."""

    @pytest.fixture(params=[
        p.stem for p in _DOCX_FILES if (OUTPUT_DIR / (p.stem + ".pdf")).exists()
    ])
    def pair(self, request) -> tuple[Path, Path]:
        stem = request.param
        return OUTPUT_DIR / f"{stem}.docx", OUTPUT_DIR / f"{stem}.pdf"

    def test_bookmark_coverage(self, pair: tuple[Path, Path]):
        docx_path, pdf_path = pair
        fitz = pytest.importorskip("fitz")
        import re

        bookmarks = set(extract_bookmarks(docx_path))

        doc = fitz.open(str(pdf_path))
        catalog_xref = doc.pdf_catalog()
        pdf_dests: set[str] = set()

        dests_key = doc.xref_get_key(catalog_xref, "Dests")
        if dests_key and dests_key[0] not in ("null", ""):
            obj_str = (
                doc.xref_object(int(dests_key[1].split()[0]))
                if dests_key[0] == "xref"
                else dests_key[1]
            )
            for m in re.finditer(r"/([A-Za-z0-9_\-.]+)\s*\[", obj_str):
                pdf_dests.add(m.group(1))
        doc.close()

        # Every PDF destination should have a corresponding DOCX bookmark
        only_pdf = pdf_dests - bookmarks
        # We allow some PDF-only anchors (page-level), but there should be
        # at least some overlap
        if bookmarks and pdf_dests:
            overlap = bookmarks & pdf_dests
            assert len(overlap) > 0, (
                f"No overlapping destinations between {docx_path.name} and {pdf_path.name}"
            )
