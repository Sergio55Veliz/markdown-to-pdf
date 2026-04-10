"""
Low-level OOXML helper functions for Word document generation.

Functions that directly manipulate ``lxml`` / OOXML elements: paragraph
shading, borders, indentation, cell formatting, fonts, and bookmarks.
"""

from __future__ import annotations

from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from markdown_to_pdf.constants import (
    rgb_docx,
    rgb_hex_upper,
    COLOR_H1_BORDER,
    COLOR_H2_BORDER,
    WordFonts,
)


# ── Paragraph helpers ──────────────────────────────────────────────────────────

def set_para_shading(para, fill_color: tuple[int, int, int]) -> None:
    """Add a solid background shading to a paragraph."""
    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  rgb_hex_upper(fill_color))
    pPr.append(shd)


def set_para_border_left(para, color: tuple[int, int, int], width_eighths: int = 24) -> None:
    """Add a left border to a paragraph."""
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"),   "single")
    left.set(qn("w:sz"),    str(width_eighths))
    left.set(qn("w:space"), "4")
    left.set(qn("w:color"), rgb_hex_upper(color))
    pBdr.append(left)
    pPr.append(pBdr)


def set_para_indent(para, left_twips: int = 360) -> None:
    """Set left indentation of a paragraph in twips."""
    pPr = para._p.get_or_add_pPr()
    ind = OxmlElement("w:ind")
    ind.set(qn("w:left"), str(left_twips))
    pPr.append(ind)


def no_space_before(para) -> None:
    """Remove all space-before from a paragraph."""
    pPr = para._p.get_or_add_pPr()
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:before"), "0")
    pPr.append(spacing)


def set_para_space_after(para, pt: float) -> None:
    """Set the spacing-after value on a paragraph (pt → twips)."""
    pPr = para._p.get_or_add_pPr()
    spacing = pPr.find(qn("w:spacing"))
    if spacing is None:
        spacing = OxmlElement("w:spacing")
        pPr.append(spacing)
    spacing.set(qn("w:after"), str(int(pt * 20)))


def set_para_page_break_before(para) -> None:
    """Force a page break immediately before the given paragraph."""
    pPr = para._p.get_or_add_pPr()
    pb = OxmlElement("w:pageBreakBefore")
    pb.set(qn("w:val"), "1")
    pPr.append(pb)


# ── Heading border helpers ────────────────────────────────────────────────────

def set_h1_bottom_border(para) -> None:
    """Add H1-weight bottom border (2.25 pt) to a paragraph."""
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"),   "single")
    bottom.set(qn("w:sz"),    "18")
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), rgb_hex_upper(COLOR_H1_BORDER))
    pBdr.append(bottom)
    pPr.append(pBdr)


def set_h2_bottom_border(para) -> None:
    """Add H2-weight bottom border (0.75 pt) to a paragraph."""
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"),   "single")
    bottom.set(qn("w:sz"),    "6")
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), rgb_hex_upper(COLOR_H2_BORDER))
    pBdr.append(bottom)
    pPr.append(pBdr)


# ── Cell helpers ──────────────────────────────────────────────────────────────

def set_cell_shading(cell, fill_color: tuple[int, int, int]) -> None:
    """Apply a solid background fill to a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  rgb_hex_upper(fill_color))
    tcPr.append(shd)


def set_cell_border(cell, border_color: tuple[int, int, int]) -> None:
    """Set a hairline bottom border on a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"),   "none" if side != "bottom" else "single")
        el.set(qn("w:sz"),    "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), rgb_hex_upper(border_color))
        tcBorders.append(el)
    tcPr.append(tcBorders)


# ── Font helpers ──────────────────────────────────────────────────────────────

def set_run_font(run, font_name: str) -> None:
    """Set the font family on a run for all character sets."""
    run.font.name = font_name
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:cs"),    font_name)
    for attr in (qn("w:asciiTheme"), qn("w:hAnsiTheme"), qn("w:cstheme")):
        if rFonts.get(attr) is not None:
            del rFonts.attrib[attr]


def set_style_font(style, font_name: str) -> None:
    """Set the font family on a paragraph style for all character sets."""
    style.font.name = font_name
    rPr = style.font._element
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:cs"),    font_name)
    for attr in (qn("w:asciiTheme"), qn("w:hAnsiTheme"), qn("w:cstheme")):
        if rFonts.get(attr) is not None:
            del rFonts.attrib[attr]


def set_style_bottom_border(style, color: tuple[int, int, int], sz: str) -> None:
    """Add a bottom paragraph border to a paragraph style."""
    style_elem = style._element
    pPr = style_elem.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        style_elem.append(pPr)
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    existing = pBdr.find(qn("w:bottom"))
    if existing is not None:
        pBdr.remove(existing)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"),   "single")
    bottom.set(qn("w:sz"),    sz)
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), rgb_hex_upper(color))
    pBdr.append(bottom)


# ── Bookmark helpers ──────────────────────────────────────────────────────────

_bookmark_id: int = 0


def reset_bookmark_counter() -> None:
    """Reset the global bookmark ID counter (call once per document)."""
    global _bookmark_id
    _bookmark_id = 0


def add_bookmark(para, name: str) -> None:
    """Wrap a paragraph in a named Word bookmark."""
    global _bookmark_id
    _bookmark_id += 1
    bid = str(_bookmark_id)

    p = para._p
    bk_start = OxmlElement("w:bookmarkStart")
    bk_start.set(qn("w:id"),   bid)
    bk_start.set(qn("w:name"), name)
    bk_end = OxmlElement("w:bookmarkEnd")
    bk_end.set(qn("w:id"), bid)

    pPr = p.find(qn("w:pPr"))
    insert_at = (list(p).index(pPr) + 1) if pPr is not None else 0
    p.insert(insert_at, bk_start)
    p.append(bk_end)
