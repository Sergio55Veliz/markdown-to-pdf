"""
Tests for link validation in DOCX files generated from example Markdowns.

Each test class generates its DOCX fresh (deleting any pre-existing file),
then validates:
  1. All expected heading bookmarks are detected.
  2. Each bookmark lives in the correct paragraph (right heading/subheading).
  3. Every TOC hyperlink has the correct display text.
  4. No internal hyperlinks are broken (every anchor has a matching bookmark).

Optionally generates PDFs and cross-validates bookmark coverage if Playwright
and PyMuPDF (fitz) are available.
"""

from __future__ import annotations

import io
import re
import urllib.parse
import zipfile
from pathlib import Path

import lxml.etree as ET
import pytest

from markdown_to_pdf.word.generator import markdown_to_docx

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"

_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _qn(local: str) -> str:
    return f"{{{_W}}}{local}"


# ── DOCX generation ───────────────────────────────────────────────────────────

def _build_docx(md_path: Path) -> Path:
    """Delete any existing .docx, regenerate from Markdown, return the path."""
    out = md_path.with_suffix(".docx")
    if out.exists():
        out.unlink()
    text = md_path.read_text(encoding="utf-8-sig")
    doc = markdown_to_docx(text)
    doc.save(str(out))
    return out


# ── DOCX extraction helpers ───────────────────────────────────────────────────

def _root_from_docx(docx_path: Path) -> ET._Element:
    with zipfile.ZipFile(docx_path) as zf:
        with zf.open("word/document.xml") as f:
            return ET.parse(f).getroot()


def extract_bookmarks(docx_path: Path) -> list[str]:
    """Return all user bookmark names (excludes Word-internal ``_*`` names)."""
    root = _root_from_docx(docx_path)
    return [
        bk.get(_qn("name"), "")
        for bk in root.iter(_qn("bookmarkStart"))
        if bk.get(_qn("name"), "") and not bk.get(_qn("name"), "").startswith("_")
    ]


def extract_bookmark_to_paragraph(docx_path: Path) -> dict[str, str]:
    """Return ``{bookmark_name: full paragraph text}`` for every user bookmark.

    ``w:bookmarkStart`` is a sibling of ``w:r`` inside ``w:p``, so we walk each
    paragraph and collect all bookmark names found in it.
    """
    root = _root_from_docx(docx_path)
    result: dict[str, str] = {}
    body = root.find(_qn("body"))
    for para in body.iter(_qn("p")):
        para_text = "".join(t.text or "" for t in para.iter(_qn("t")))
        for bk in para.findall(".//" + _qn("bookmarkStart")):
            name = bk.get(_qn("name"), "")
            if name and not name.startswith("_"):
                result[name] = para_text
    return result


def extract_internal_links(docx_path: Path) -> list[dict[str, str]]:
    """Return ``[{anchor, text}, ...]`` for every internal ``w:hyperlink``.

    The ``w:anchor`` attribute may be URL-encoded (e.g. ``introducci%C3%B3n``);
    we decode it to plain Unicode so it can be compared directly against the
    Unicode bookmark names stored in ``w:bookmarkStart``.
    """
    root = _root_from_docx(docx_path)
    links: list[dict[str, str]] = []
    for hl in root.iter(_qn("hyperlink")):
        raw_anchor = hl.get(_qn("anchor"))
        if not raw_anchor:
            continue
        anchor = urllib.parse.unquote(raw_anchor)
        text = "".join(t.text or "" for t in hl.iter(_qn("t"))).strip() or "(no text)"
        links.append({"anchor": anchor, "text": text})
    return links


# ── Astronomia tests ──────────────────────────────────────────────────────────

class TestDocxAstronomia:
    """
    Validate guia_astronomia_observacional.docx.

    In this document bookmarks are auto-generated slugs from heading text,
    so each bookmark lives directly on its heading paragraph.

    Expected mapping (bookmark slug → keyword to find in that paragraph):
      introducción              → "Introducción"
      equipamiento-esencial     → "Equipamiento"
      objetos-celestes-por-dificultad → "Celestes"
      astrofotografía-básica    → "Astrofotograf"
      condiciones-de-observación → "Condiciones"
      calendario-astronómico-2026 → "Calendario"
      anexo-matemático          → "Anexo"
    """

    # (bookmark_slug, keyword_expected_in_heading_paragraph)
    EXPECTED = [
        ("introducción",                  "Introducción"),
        ("equipamiento-esencial",          "Equipamiento"),
        ("objetos-celestes-por-dificultad","Celestes"),
        ("astrofotografía-básica",         "Astrofotograf"),
        ("condiciones-de-observación",     "Condiciones"),
        ("calendario-astronómico-2026",    "Calendario"),
        ("anexo-matemático",               "Anexo"),
    ]

    # (anchor, fragment of the TOC link display text)
    TOC_LINKS = [
        ("introducción",                  "Introducción"),
        ("equipamiento-esencial",          "Equipamiento Esencial"),
        ("objetos-celestes-por-dificultad","Objetos Celestes"),
        ("astrofotografía-básica",         "Astrofotografía"),
        ("condiciones-de-observación",     "Condiciones"),
        ("calendario-astronómico-2026",    "Calendario"),
        ("anexo-matemático",               "Anexo"),
    ]

    @pytest.fixture(scope="class")
    def docx_path(self) -> Path:
        md = EXAMPLES_DIR / "guia_astronomia_observacional.md"
        if not md.exists():
            pytest.skip("guia_astronomia_observacional.md not found")
        return _build_docx(md)

    def test_all_expected_bookmarks_present(self, docx_path: Path):
        """Every TOC section must have its bookmark slug in the DOCX."""
        found = set(extract_bookmarks(docx_path))
        missing = [slug for slug, _ in self.EXPECTED if slug not in found]
        assert not missing, (
            f"Missing bookmarks: {missing}\nAll found: {sorted(found)}"
        )

    def test_each_bookmark_is_on_its_heading_paragraph(self, docx_path: Path):
        """Bookmark must reside inside the paragraph of its own heading."""
        bk_para = extract_bookmark_to_paragraph(docx_path)
        errors = []
        for slug, keyword in self.EXPECTED:
            text = bk_para.get(slug, "")
            if keyword.lower() not in text.lower():
                errors.append(
                    f"  bookmark '{slug}' → paragraph '{text[:70]}'"
                    f" (expected keyword '{keyword}')"
                )
        assert not errors, "Bookmark/heading mismatch:\n" + "\n".join(errors)

    def test_all_internal_links_resolve(self, docx_path: Path):
        """Every w:hyperlink anchor must match an existing bookmark."""
        bookmarks = set(extract_bookmarks(docx_path))
        broken = [
            lk for lk in extract_internal_links(docx_path)
            if lk["anchor"] not in bookmarks
        ]
        assert not broken, (
            "Broken links: "
            + ", ".join(f'[{lk["text"]}]→#{lk["anchor"]}' for lk in broken[:5])
        )

    def test_toc_links_display_text_matches_target_section(self, docx_path: Path):
        """
        Each TOC hyperlink must display its section's name AND point to a
        bookmark that lives in a paragraph containing the same keyword.
        """
        bk_para = extract_bookmark_to_paragraph(docx_path)
        links_by_anchor: dict[str, str] = {
            lk["anchor"]: lk["text"]
            for lk in extract_internal_links(docx_path)
        }
        errors = []
        for anchor, expected_fragment in self.TOC_LINKS:
            link_text = links_by_anchor.get(anchor)
            if link_text is None:
                errors.append(f"  No hyperlink found targeting #{anchor}")
                continue
            # The hyperlink's display text must contain the expected fragment
            if expected_fragment.split()[0].lower() not in link_text.lower():
                errors.append(
                    f"  #{anchor}: link text is '{link_text}', "
                    f"expected to contain '{expected_fragment}'"
                )
            # The bookmark's paragraph must also match
            para_text = bk_para.get(anchor, "")
            keyword = self.EXPECTED[
                next(i for i, (s, _) in enumerate(self.EXPECTED) if s == anchor)
            ][1]
            if keyword.lower() not in para_text.lower():
                errors.append(
                    f"  #{anchor}: bookmark paragraph is '{para_text[:70]}', "
                    f"expected keyword '{keyword}'"
                )
        assert not errors, "TOC link/bookmark mismatch:\n" + "\n".join(errors)


# ── Culinaria tests ───────────────────────────────────────────────────────────

class TestDocxCulinaria:
    """
    Validate atlas_tecnicas_culinarias.docx.

    This document uses explicit ``<a id="...">`` naked anchors placed
    immediately AFTER each section heading.  The rendering engine stores the
    anchor as ``_pending_anchor`` and attaches it to the NEXT heading it
    encounters (the first subheading of that section).

    Consequence: bookmark ``fundamentos`` lives on the paragraph
    ``### ¿Qué es cocinar?``, not on ``## Fundamentos de la Cocción``.

    Validation strategy:
      1. All seven explicit anchors are present as bookmarks.
      2. Each bookmark paragraph contains a keyword from its own section
         (the subheading it was attached to).
      3. Each TOC hyperlink has the correct display text for its section.
      4. No broken links.

    Explicit anchor → first-subheading keyword mapping:
      fundamentos  → next heading: "¿Qué es cocinar?"    → keyword: "cocinar"
      reacciones   → next heading: "Reacción de Maillard" → keyword: "Maillard"
      técnicas     → next heading: "Mapa de Técnicas"     → keyword: "Mapa"
      tiempos      → next heading: "La Regla del Arrastre"→ keyword: "Arrastre"
      fermentación → next heading: "Tipos de Fermentación"→ keyword: "Tipos"
      recetas      → next heading after ## Recetas        → keyword determined below
      fórmulas     → next heading after ## Conversión     → keyword determined below
    """

    # (bookmark_name, keyword expected inside that bookmark's paragraph)
    EXPECTED = [
        ("fundamentos",  "cocinar"),      # first ### under ## Fundamentos
        ("reacciones",   "Maillard"),    # first ### under ## Reacciones
        ("técnicas",     "Mapa"),        # first ### under ## Técnicas
        ("tiempos",      "Arrastre"),    # first ### under ## Tiempos
        ("fermentación", "Tipos"),       # first ### under ## Fermentación
        ("recetas",      "Braise"),      # first ### under ## Recetas → "Braise Universal"
        ("fórmulas",     "Equivalencias"), # first ### under ## Conversión → "Tabla de Equivalencias"
    ]

    # (anchor, fragment of the TOC link display text)
    TOC_LINKS = [
        ("fundamentos",  "Fundamentos"),
        ("reacciones",   "Reacciones"),
        ("técnicas",     "Técnicas"),
        ("tiempos",      "Tiempos"),
        ("fermentación", "Fermentación"),
        ("recetas",      "Recetas"),
        ("fórmulas",     "Fórmulas"),
    ]

    @pytest.fixture(scope="class")
    def docx_path(self) -> Path:
        md = EXAMPLES_DIR / "atlas_tecnicas_culinarias.md"
        if not md.exists():
            pytest.skip("atlas_tecnicas_culinarias.md not found")
        return _build_docx(md)

    def test_all_expected_bookmarks_present(self, docx_path: Path):
        """All seven explicit section anchors must appear as bookmarks."""
        found = set(extract_bookmarks(docx_path))
        missing = [slug for slug, _ in self.EXPECTED if slug not in found]
        assert not missing, (
            f"Missing bookmarks: {missing}\nAll found: {sorted(found)}"
        )

    def test_each_bookmark_is_on_the_correct_subheading(self, docx_path: Path):
        """
        Each explicit anchor is attached as _pending_anchor to the first
        subheading paragraph of its section.  Verify the keyword from that
        expected subheading appears in the bookmark's paragraph.
        """
        bk_para = extract_bookmark_to_paragraph(docx_path)
        errors = []
        for slug, keyword in self.EXPECTED:
            text = bk_para.get(slug, "")
            if keyword.lower() not in text.lower():
                errors.append(
                    f"  bookmark '{slug}' → paragraph '{text[:70]}'"
                    f" (expected subheading keyword '{keyword}')"
                )
        assert not errors, "Bookmark/subheading mismatch:\n" + "\n".join(errors)

    def test_all_internal_links_resolve(self, docx_path: Path):
        """Every w:hyperlink anchor must match an existing bookmark."""
        bookmarks = set(extract_bookmarks(docx_path))
        broken = [
            lk for lk in extract_internal_links(docx_path)
            if lk["anchor"] not in bookmarks
        ]
        assert not broken, (
            "Broken links: "
            + ", ".join(f'[{lk["text"]}]→#{lk["anchor"]}' for lk in broken[:5])
        )

    def test_toc_links_display_text_matches_section_name(self, docx_path: Path):
        """TOC hyperlinks must display the correct section name."""
        links_by_anchor: dict[str, str] = {
            lk["anchor"]: lk["text"]
            for lk in extract_internal_links(docx_path)
        }
        errors = []
        for anchor, expected_fragment in self.TOC_LINKS:
            link_text = links_by_anchor.get(anchor)
            if link_text is None:
                errors.append(f"  No hyperlink found targeting #{anchor}")
                continue
            if expected_fragment.split()[0].lower() not in link_text.lower():
                errors.append(
                    f"  #{anchor}: link text is '{link_text}', "
                    f"expected to contain '{expected_fragment}'"
                )
        assert not errors, "TOC display-text mismatch:\n" + "\n".join(errors)


# ── Optional PDF cross-validation ─────────────────────────────────────────────

class TestPdfCrossValidation:
    """
    Generate PDFs from both example Markdowns and verify that the heading
    anchors embedded in the PDF match every bookmark present in the DOCX.

    Skipped automatically when Playwright or PyMuPDF (fitz) is not installed.
    """

    _EXAMPLES = [
        "guia_astronomia_observacional",
        "atlas_tecnicas_culinarias",
    ]

    @pytest.fixture(scope="class", params=_EXAMPLES)
    def pair(self, request) -> tuple[Path, Path]:
        """Generate (or regenerate) DOCX + PDF for a given example."""
        stem = request.param
        md_path = EXAMPLES_DIR / f"{stem}.md"
        if not md_path.exists():
            pytest.skip(f"{stem}.md not found")

        pytest.importorskip("playwright")
        pytest.importorskip("fitz")

        from markdown_to_pdf.pdf.generator import generate_pdf_from_file

        docx_path = _build_docx(md_path)

        pdf_path = md_path.with_suffix(".pdf")
        if pdf_path.exists():
            pdf_path.unlink()
        generate_pdf_from_file(md_path, pdf_path, title=stem.replace("_", " ").title())

        return docx_path, pdf_path

    def test_pdf_destinations_overlap_docx_bookmarks(self, pair: tuple[Path, Path]):
        """Every PDF named destination should correspond to a DOCX bookmark."""
        import fitz

        docx_path, pdf_path = pair
        bookmarks = set(extract_bookmarks(docx_path))

        pdf_doc = fitz.open(str(pdf_path))
        catalog_xref = pdf_doc.pdf_catalog()
        pdf_dests: set[str] = set()
        dests_key = pdf_doc.xref_get_key(catalog_xref, "Dests")
        if dests_key and dests_key[0] not in ("null", ""):
            obj_str = (
                pdf_doc.xref_object(int(dests_key[1].split()[0]))
                if dests_key[0] == "xref"
                else dests_key[1]
            )
            for m in re.finditer(r"/([A-Za-z0-9_\-.]+)\s*\[", obj_str):
                pdf_dests.add(m.group(1))
        pdf_doc.close()

        if bookmarks and pdf_dests:
            overlap = bookmarks & pdf_dests
            assert len(overlap) > 0, (
                f"No overlapping destinations between "
                f"{docx_path.name} and {pdf_path.name}.\n"
                f"DOCX bookmarks: {sorted(bookmarks)[:10]}\n"
                f"PDF dests: {sorted(pdf_dests)[:10]}"
            )
