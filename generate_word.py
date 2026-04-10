#!/usr/bin/env python3
"""
Word Generator for Feature Store documentation.

Converts Markdown files to styled .docx files with:
  - Banco Bolivariano corporate typography (Inter font family)
  - Headings h1–h6 with matching color scheme
  - Bold, italic, inline code, strikethrough inline formatting
  - Fenced code blocks (with optional language label)
  - Tables with header row styling
  - Blockquotes
  - Ordered and unordered lists (nested)
  - Horizontal rules
  - Math expressions rendered as plain text (LaTeX source preserved)

Usage:
    conda run -n pdf_gen python scripts/pdf_generator/generate_word.py
"""

import html as html_lib
import re
from pathlib import Path

from lxml import etree as _lxml_etree
import markdown_it
from mdit_py_plugins.dollarmath import dollarmath_plugin
from bs4 import BeautifulSoup, NavigableString, Tag
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import docx.opc.constants

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent.parent
OUTPUT_DIR  = SCRIPT_DIR

DOCS = [
    {
        "input":  REPO_ROOT / "propuesta_nuevas_features.md",
        "output": OUTPUT_DIR / "propuesta_nuevas_features.docx",
        "title":  "Propuesta de Nuevas Features — Feature Store",
        "doc_id": "propuesta",
    },
    {
        "input":  REPO_ROOT / "dashboard_riesgo_juridico.md",
        "output": OUTPUT_DIR / "dashboard_riesgo_juridico.docx",
        "title":  "Dashboard de Riesgo — Clientes Jurídicos",
        "doc_id": "dashboard",
    },
]

# ── Color palette (matches generate_pdfs.py) ──────────────────────────────────
C_H1_TEXT    = RGBColor(0x0F, 0x17, 0x2A)
C_H1_BORDER  = RGBColor(0x1E, 0x40, 0xAF)
C_H2_TEXT    = RGBColor(0x1E, 0x40, 0xAF)
C_H2_BORDER  = RGBColor(0xBF, 0xDB, 0xFE)
C_H3_TO_H5   = RGBColor(0x1D, 0x4E, 0xD8)
C_H6_TEXT    = RGBColor(0x47, 0x55, 0x69)
C_BODY       = RGBColor(0x1E, 0x29, 0x3B)
C_EM         = RGBColor(0x47, 0x55, 0x69)
C_LINK       = RGBColor(0x25, 0x63, 0xEB)
C_CODE_BG    = RGBColor(0xF1, 0xF5, 0xF9)   # light bg for inline code
C_CODE_TEXT  = RGBColor(0x0F, 0x17, 0x2A)
C_PRE_BG     = RGBColor(0x1E, 0x20, 0x30)   # dark bg for code blocks
C_PRE_TEXT   = RGBColor(0xC8, 0xD3, 0xF5)
C_BQ_BG      = RGBColor(0xEF, 0xF6, 0xFF)
C_BQ_BORDER  = RGBColor(0x25, 0x63, 0xEB)
C_BQ_TEXT    = RGBColor(0x33, 0x41, 0x55)
C_DEL        = RGBColor(0x6B, 0x72, 0x80)
C_TH_BG      = RGBColor(0x1E, 0x3A, 0x8A)
C_TH_TEXT    = RGBColor(0xFF, 0xFF, 0xFF)
C_TD_BORDER  = RGBColor(0xCB, 0xD5, 0xE1)
C_TD_ALT_BG  = RGBColor(0xF1, 0xF5, 0xF9)
C_HR         = RGBColor(0xE2, 0xE8, 0xF0)


# ── Heading font sizes (pt) ────────────────────────────────────────────────────
# H1 22 pt (≈ 2.1× body) — prominent document title / major section break.
# H2 14 pt (≈ 1.3× body) — primary within-section heading.
# H3 12 pt, H4–H5 11 pt — progressive sub-section levels.
# H6 10 pt (= body size) — lowest label, differentiated only by bold + color.
# All sizes mirror generate_pdfs.py so Word and PDF outputs look visually consistent.
HEADING_SIZE = {1: 22, 2: 14, 3: 12, 4: 11, 5: 11, 6: 10}
# H1 bold: maximum contrast for the top hierarchy level.
# H2–H5 not bold: Calibri Light at large sizes already reads as display weight.
# H6 bold: distinguishes it from body text at the same 10 pt size.
HEADING_BOLD = {1: True, 2: False, 3: False, 4: False, 5: False, 6: True}

# Body text: Segoe UI is pre-installed on every modern Windows machine and is the
# closest commonly available match to Inter (same clean, geometric proportions).
FONT_BODY      = "Segoe UI"
# Headings: Calibri Light gives a lighter, display-weight feel for large headings
# while remaining universally available on any Windows machine with Office.
FONT_HEADING   = "Calibri Light"
FONT_MONO      = "Consolas"      # pre-installed on Windows/Office, true monospace, good readability at 9 pt
FONT_BODY_PT   = 10.5    # 10.5 pt: comfortable reading size on A4 at 2.5 cm margins (~85 chars/line)
FONT_CODE_PT   = 9.0     # 9.0 pt: Consolas is wider per em than Segoe UI; a 1.5 pt
                         # reduction keeps code within the same column width as body text
PARA_SPACING   = Pt(7)   # 7 pt after body paragraphs (≈ 0.67× font size); provides visual
                         # rhythm without wasting space with a full blank line

# ── Emoji rendering ────────────────────────────────────────────────────────────
# Word renders emojis in black-and-white (Segoe UI has no color emoji support in
# print mode).  We compensate with two strategies:
#   1. Color-circle / color-square emojis → replaced with ● (U+25CF) and the
#      run's font color set to the circle's original hue.
#   2. All other emojis → kept as-is but rendered with the "Segoe UI Emoji" font
#      and a representative run color so they appear tinted instead of plain black.

# Replacement character for strategy 1 (solid filled circle, size-neutral).
_BLACK_CIRCLE = "\u25CF"

# Map: emoji codepoint → RGBColor it represents.
# Color-circle / color-square emojis (strategy 1)
_CIRCLE_EMOJI: dict[str, RGBColor] = {
    "\U0001F534": RGBColor(0xDC, 0x26, 0x26),  # 🔴 red
    "\U0001F535": RGBColor(0x29, 0x63, 0xEB),  # 🔵 blue
    "\U0001F7E0": RGBColor(0xEA, 0x58, 0x0C),  # 🟠 orange
    "\U0001F7E1": RGBColor(0xCA, 0x8A, 0x04),  # 🟡 yellow
    "\U0001F7E2": RGBColor(0x16, 0xA3, 0x4A),  # 🟢 green
    "\U0001F7E3": RGBColor(0x7C, 0x3A, 0xED),  # 🟣 purple
    "\U0001F7E4": RGBColor(0x78, 0x35, 0x6F),  # 🟤 brown
    "\U000026AB": RGBColor(0x6B, 0x72, 0x80),  # ⚫ black
    "\U000026AA": RGBColor(0xD1, 0xD5, 0xDB),  # ⚪ white
    "\U0001F7E5": RGBColor(0xDC, 0x26, 0x26),  # 🟥 red square
    "\U0001F7E6": RGBColor(0x29, 0x63, 0xEB),  # 🟦 blue square
    "\U0001F7E7": RGBColor(0xEA, 0x58, 0x0C),  # 🟧 orange square
    "\U0001F7E8": RGBColor(0xCA, 0x8A, 0x04),  # 🟨 yellow square
    "\U0001F7E9": RGBColor(0x16, 0xA3, 0x4A),  # 🟩 green square
    "\U0001F7EA": RGBColor(0x7C, 0x3A, 0xED),  # 🟪 purple square
    "\U0001F7EB": RGBColor(0x78, 0x35, 0x6F),  # 🟫 brown square
}

# Other common emojis: kept as character, colored with representative hue (strategy 2)
_EMOJI_COLOR: dict[str, RGBColor] = {
    "\u2705": RGBColor(0x16, 0xA3, 0x4A),   # ✅ check mark  → green
    "\u274C": RGBColor(0xDC, 0x26, 0x26),   # ❌ cross mark  → red
    "\u26A0": RGBColor(0xD9, 0x77, 0x06),   # ⚠  warning     → amber
    "\u2757": RGBColor(0xDC, 0x26, 0x26),   # ❗ exclamation → red
    "\u2714": RGBColor(0x16, 0xA3, 0x4A),   # ✔  check       → green
    "\u2716": RGBColor(0xDC, 0x26, 0x26),   # ✖  cross       → red
    "\u26A1": RGBColor(0xCA, 0x8A, 0x04),   # ⚡ lightning   → yellow
    "\u2B50": RGBColor(0xCA, 0x8A, 0x04),   # ⭐ star        → yellow
    "\U0001F4A1": RGBColor(0xD9, 0x77, 0x06),  # 💡 bulb        → amber
    "\U0001F680": RGBColor(0x29, 0x63, 0xEB),  # 🚀 rocket      → blue
    "\U0001F4CC": RGBColor(0xDC, 0x26, 0x26),  # 📌 pin         → red
    "\U0001F4CD": RGBColor(0xDC, 0x26, 0x26),  # 📍 location    → red
    "\U0001F4B0": RGBColor(0x16, 0xA3, 0x4A),  # 💰 money       → green
    "\U0001F4CA": RGBColor(0x29, 0x63, 0xEB),  # 📊 bar chart   → blue
    "\U0001F3AF": RGBColor(0xDC, 0x26, 0x26),  # 🎯 target      → red
    "\U0001F3C6": RGBColor(0xCA, 0x8A, 0x04),  # 🏆 trophy      → gold
    "\U0001F4C8": RGBColor(0x16, 0xA3, 0x4A),  # 📈 chart up    → green
    "\U0001F4C9": RGBColor(0xDC, 0x26, 0x26),  # 📉 chart down  → red
    "\U0001F511": RGBColor(0xCA, 0x8A, 0x04),  # 🔑 key         → yellow
    "\U0001F4DD": RGBColor(0x29, 0x63, 0xEB),  # 📝 memo        → blue
    "\U0001F31F": RGBColor(0xCA, 0x8A, 0x04),  # 🌟 glow star   → yellow
    "\U0001F4BC": RGBColor(0x29, 0x63, 0xEB),  # 💼 briefcase   → blue
    "\U0001F4CB": RGBColor(0x29, 0x63, 0xEB),  # 📋 clipboard   → blue
    "\U0001F514": RGBColor(0xCA, 0x8A, 0x04),  # 🔔 bell        → yellow
    "\U0001F310": RGBColor(0x29, 0x63, 0xEB),  # 🌐 globe       → blue
    "\U0001F504": RGBColor(0x29, 0x63, 0xEB),  # 🔄 arrows      → blue
    "\u27A1": RGBColor(0x29, 0x63, 0xEB),   # ➡ arrow right  → blue
    "\u2B05": RGBColor(0x29, 0x63, 0xEB),   # ⬅ arrow left   → blue
    "\u2B06": RGBColor(0x29, 0x63, 0xEB),   # ⬆ arrow up     → blue
    "\u2B07": RGBColor(0x29, 0x63, 0xEB),   # ⬇ arrow down   → blue
    "\U0001F6AB": RGBColor(0xDC, 0x26, 0x26),  # 🚫 no entry    → red
    "\U0001F4AF": RGBColor(0xDC, 0x26, 0x26),  # 💯 100         → red
    "\U0001F50D": RGBColor(0x29, 0x63, 0xEB),  # 🔍 magnifier   → blue
}

# Regex that matches a single emoji codepoint (U+2600–U+27BF misc symbols and
# U+1F300–U+1FBFF main/supplemental emoji), optionally followed by the variation
# selector U+FE0F which should be consumed but not rendered.
_EMOJI_RE = re.compile(
    r'([\u2600-\u27BF\U0001F300-\U0001FBFF])\uFE0F?',
    re.UNICODE,
)


def _split_by_emoji(text: str) -> list[tuple[str, str]]:
    """Split text into alternating plain-text and emoji segments.

    Uses ``_EMOJI_RE`` to locate emoji codepoints (U+2600–U+27BF and
    U+1F300–U+1FBFF) and splits the input around each match so callers
    can render plain segments and emoji segments with different fonts or
    colours.

    Args:
        text: Raw Unicode string that may contain emoji characters.

    Returns:
        A list of ``(kind, value)`` 2-tuples where ``kind`` is either
        ``'text'`` (a plain-text segment) or ``'emoji'`` (a single emoji
        codepoint with the variation selector U+FE0F already stripped).
        Adjacent segments always alternate in kind; each tuple contains
        a non-empty string.
    """
    result: list[tuple[str, str]] = []
    last = 0
    for m in _EMOJI_RE.finditer(text):
        if m.start() > last:
            result.append(("text", text[last:m.start()]))
        result.append(("emoji", m.group(1)))  # group(1) strips trailing FE0F
        last = m.end()
    if last < len(text):
        result.append(("text", text[last:]))
    return result


# ── Internal-link state (reset per document in markdown_to_docx) ──────────────
# Maps base slug → occurrence count, so duplicate headings get unique suffixes
# (same deduplication rule as GitHub: "heading", "heading-1", "heading-2", …).
_slug_counts: dict[str, int] = {}
# Incrementing integer ID for <w:bookmarkStart>/<w:bookmarkEnd> w:id attributes.
# OOXML requires each bookmark in a document to have a unique non-negative integer ID.
_bookmark_id: int = 0
# When the parser encounters a naked <a id="..."> anchor element (e.g. <a id="p1"></a>)
# it stores the id here so the NEXT rendered block can adopt it as an extra bookmark.
# This is how markdown authors define explicit anchor targets before headings.
_pending_anchor: str | None = None


def _heading_slug(text: str) -> str:
    """Compute a GitHub-style anchor slug for a heading and register it globally.

    Converts a heading's plain-text content into the URL fragment identifier
    that markdown-it (and GitHub) assign to it, then updates ``_slug_counts``
    so that identical headings receive unique numeric suffixes.

    Algorithm (matches GitHub Flavored Markdown / markdown-it defaults):

    1. Strip leading/trailing whitespace and lowercase.
    2. Remove every character that is not ``\\w`` (``[a-zA-Z0-9_]``),
       a space, or a hyphen.
    3. Replace whitespace runs with a single hyphen.
    4. Append ``-1``, ``-2``, … when the same base slug appears more
       than once in the document.

    Args:
        text: Plain-text string of the heading (HTML tags stripped).

    Returns:
        The unique anchor slug for this heading occurrence, e.g.
        ``"introduction"`` or ``"introduction-1"``.
    """
    global _slug_counts
    base = re.sub(r'\s+', '-', re.sub(r'[^\w\s-]', '', text.lower().strip()))
    count = _slug_counts.get(base, 0)
    _slug_counts[base] = count + 1
    return base if count == 0 else f"{base}-{count}"


def _is_naked_anchor(node) -> str | None:
    """Detect a naked HTML anchor element used as an explicit bookmark target.

    Returns the ``id`` attribute value when *node* is a zero-content
    ``<a id="...">`` tag (no ``href``, no visible text).  These are
    commonly placed immediately before headings in Markdown to create
    stable, author-controlled bookmark targets::

        <a id="p1"></a>
        ### Propuesta 1: …

    Two structural forms are recognised:

    * **Case 1** — bare block-level anchor: ``<a id="…"></a>``.
    * **Case 2** — anchor wrapped in a paragraph by the HTML parser:
      ``<p><a id="…"></a></p>`` (lxml and BeautifulSoup may wrap inline
      elements appearing at block level).

    Args:
        node: A BeautifulSoup element to test.

    Returns:
        The ``id`` string if the element is a naked anchor, otherwise
        ``None``.
    """
    # Case 1: the node itself is a bare <a id="…"> at block level
    if node.name == "a" and node.get("id") and not node.get("href") \
            and not node.get_text(strip=True):
        return node.get("id")
    # Case 2: lxml wraps the inline <a> in a <p> when it appears at block level →
    #   <p><a id="…"></a></p>  or  <p>\n<a id="…"></a>\n</p>
    if node.name == "p":
        meaningful = [
            c for c in node.children
            if not (isinstance(c, NavigableString) and not c.strip())
        ]
        if len(meaningful) == 1:
            child = meaningful[0]
            if hasattr(child, "name") and child.name == "a" \
                    and child.get("id") and not child.get("href") \
                    and not child.get_text(strip=True):
                return child.get("id")
    return None


# ── Low-level OOXML helpers ────────────────────────────────────────────────────

def _set_para_shading(para, fill_color: RGBColor) -> None:
    """Add a solid background shading to a paragraph.

    Inserts a ``<w:shd>`` element into the paragraph's ``<w:pPr>`` block using
    the OOXML "clear" fill type, which applies a uniformly filled background
    (no pattern).  Used primarily for blockquote and code-block paragraphs.

    Args:
        para: The ``docx.text.paragraph.Paragraph`` whose background to set.
        fill_color: The ``RGBColor`` to use as the solid fill colour.
    """
    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    hex_color = f"{fill_color[0]:02X}{fill_color[1]:02X}{fill_color[2]:02X}"
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color)
    pPr.append(shd)


def _set_para_border_left(para, color: RGBColor, width_eighths: int = 24) -> None:
    """Add a visible left border to a paragraph.

    Inserts ``<w:pBdr><w:left>`` into the paragraph's ``<w:pPr>`` block.
    Primarily used for blockquote styling to replicate the CSS
    ``border-left`` visual cue.

    Args:
        para: The ``docx.text.paragraph.Paragraph`` to style.
        color: ``RGBColor`` for the border line.
        width_eighths: Border width in OOXML ``w:sz`` units (eighths-of-a-point).
            The default ``24`` equals 3 pt, matching the visual weight of a
            4 px CSS border rendered at 96 dpi.
    """
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    hex_color = f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"
    left.set(qn("w:val"),   "single")
    left.set(qn("w:sz"),    str(width_eighths))
    left.set(qn("w:space"), "4")    # 4 pt gap between paragraph text and the border line
    left.set(qn("w:color"), hex_color)
    pBdr.append(left)
    pPr.append(pBdr)


def _set_para_indent(para, left_twips: int = 360) -> None:
    """Set the left indentation of a paragraph.

    Inserts or updates the ``<w:ind w:left="..."/>`` element inside
    ``<w:pPr>``.  Used to indent blockquote text and code-block text.

    Args:
        para: The ``docx.text.paragraph.Paragraph`` to indent.
        left_twips: Indentation in twips (twentieths-of-a-point).
            The default ``360`` twips equals 0.25 in (≈ 6.35 mm).
    """
    pPr = para._p.get_or_add_pPr()
    ind = OxmlElement("w:ind")
    ind.set(qn("w:left"), str(left_twips))
    pPr.append(ind)


def _set_cell_shading(cell, fill_color: RGBColor) -> None:
    """Apply a solid background fill to a table cell.

    Inserts a ``<w:shd>`` element into the cell's ``<w:tcPr>`` block using
    the OOXML "clear" fill type.  Used to colour the header row
    (``C_TH_BG``) and alternate data rows (``C_TD_ALT_BG``) of rendered
    Markdown tables.

    Args:
        cell: The ``docx.table._Cell`` instance to shade.
        fill_color: The ``RGBColor`` to use as the solid fill colour.
    """
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    hex_color = f"{fill_color[0]:02X}{fill_color[1]:02X}{fill_color[2]:02X}"
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color)
    tcPr.append(shd)


def _set_cell_border(cell, border_color: RGBColor) -> None:
    """Set a hairline bottom border on a table cell and clear all other borders.

    Inserts ``<w:tcBorders>`` into the cell's ``<w:tcPr>`` element, setting
    every side individually: top, left, and right are set to ``none`` while
    ``bottom`` receives a ``single`` 0.5 pt line in the given colour.
    This produces the horizontal-rule effect used in data rows.

    Args:
        cell: The ``docx.table._Cell`` instance to style.
        border_color: ``RGBColor`` for the bottom border line.
    """
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"),   "none" if side != "bottom" else "single")
        el.set(qn("w:sz"),    "4")    # 4 eighths-of-a-pt = 0.5 pt thin hairline border
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), f"{border_color[0]:02X}{border_color[1]:02X}{border_color[2]:02X}")
        tcBorders.append(el)
    tcPr.append(tcBorders)


def _no_space_before(para) -> None:
    """Remove all space-before from a paragraph.

    Inserts ``<w:spacing w:before="0"/>`` into ``<w:pPr>`` so that the
    paragraph does not inherit theme or style default spacing above it.
    Called on every rendered block element so vertical rhythm is controlled
    exclusively through ``_set_para_space_after``.

    Args:
        para: The ``docx.text.paragraph.Paragraph`` to modify.
    """
    pPr = para._p.get_or_add_pPr()
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:before"), "0")
    pPr.append(spacing)


def _set_para_space_after(para, pt: float) -> None:
    """Set the spacing-after value on a paragraph.

    Creates or updates the ``<w:spacing w:after="…"/>`` attribute inside
    ``<w:pPr>``.  The value is converted from points to OOXML twips
    (twentieths-of-a-point) internally.

    Args:
        para: The ``docx.text.paragraph.Paragraph`` to modify.
        pt: Spacing in points to apply after the paragraph.
    """
    pPr = para._p.get_or_add_pPr()
    spacing = pPr.find(qn("w:spacing"))
    if spacing is None:
        spacing = OxmlElement("w:spacing")
        pPr.append(spacing)
    spacing.set(qn("w:after"), str(int(pt * 20)))  # 1 pt = 20 twips (twentieths-of-a-point, OOXML unit)


def _set_h1_bottom_border(para) -> None:
    """Add an H1-weight bottom paragraph border to an individual paragraph.

    Inserts ``<w:pBdr><w:bottom>`` styled with the ``C_H1_BORDER`` colour and
    a 2.25 pt (18 eighths-of-a-point) line weight.  This function is a
    paragraph-level override; the style-level equivalent is set by
    ``_set_style_bottom_border`` when heading styles are initialised.

    Args:
        para: The ``docx.text.paragraph.Paragraph`` to decorate.
    """
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    hex_color = f"{C_H1_BORDER[0]:02X}{C_H1_BORDER[1]:02X}{C_H1_BORDER[2]:02X}"
    bottom.set(qn("w:val"),   "single")
    bottom.set(qn("w:sz"),    "18")   # 18 eighths-of-a-pt ≈ 2.25pt
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), hex_color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def _set_h2_bottom_border(para) -> None:
    """Add an H2-weight bottom paragraph border to an individual paragraph.

    Inserts ``<w:pBdr><w:bottom>`` styled with the ``C_H2_BORDER`` colour and
    a 0.75 pt (6 eighths-of-a-point) line weight — a lighter underline than
    H1's 2.25 pt border, reflecting the lower hierarchy level.  This function
    is a paragraph-level override; the style-level equivalent is set by
    ``_set_style_bottom_border`` during heading-style initialisation.

    Args:
        para: The ``docx.text.paragraph.Paragraph`` to decorate.
    """
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    hex_color = f"{C_H2_BORDER[0]:02X}{C_H2_BORDER[1]:02X}{C_H2_BORDER[2]:02X}"
    bottom.set(qn("w:val"),   "single")
    bottom.set(qn("w:sz"),    "6")    # 6 eighths-of-a-pt = 0.75 pt — lighter underline than H1's 2.25 pt
    bottom.set(qn("w:space"), "4")    # 4 pt gap between heading baseline and the border line
    bottom.set(qn("w:color"), hex_color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def _set_para_page_break_before(para) -> None:
    """Force a page break immediately before the given paragraph.

    Sets ``<w:pageBreakBefore w:val="1"/>`` inside ``<w:pPr>``.  Equivalent
    to Word's "Page break before" paragraph option.  Currently unused in the
    main conversion pipeline (page breaks are handled via the heading style
    ``keep_with_next``) but available for explicit forced-page-break cases.

    Args:
        para: The ``docx.text.paragraph.Paragraph`` before which to insert
            the page break.
    """
    pPr = para._p.get_or_add_pPr()
    pb = OxmlElement("w:pageBreakBefore")
    pb.set(qn("w:val"), "1")
    pPr.append(pb)


def _add_bookmark(para, name: str) -> None:
    """Wrap a paragraph in a named Word bookmark for internal navigation.

    Inserts ``<w:bookmarkStart>`` immediately after ``<w:pPr>`` (or at index 0
    if no pPr is present) and ``<w:bookmarkEnd>`` at the tail of the paragraph
    element.  Both elements share a document-unique integer ``w:id`` taken from
    the module-level ``_bookmark_id`` counter.

    The resulting bookmark can be targeted by a ``<w:hyperlink w:anchor="name">``
    element, enabling clickable internal links within the generated ``.docx``.

    Args:
        para: The ``docx.text.paragraph.Paragraph`` to wrap.
        name: The bookmark name / anchor identifier (must be unique within the
            document; typically the heading slug produced by ``_heading_slug``).
    """
    global _bookmark_id
    _bookmark_id += 1
    bid = str(_bookmark_id)

    p = para._p
    bk_start = OxmlElement("w:bookmarkStart")
    bk_start.set(qn("w:id"),   bid)
    bk_start.set(qn("w:name"), name)
    bk_end = OxmlElement("w:bookmarkEnd")
    bk_end.set(qn("w:id"), bid)

    # bookmarkStart must come after pPr so Word's paragraph properties are read first.
    pPr = p.find(qn("w:pPr"))
    insert_at = (list(p).index(pPr) + 1) if pPr is not None else 0
    p.insert(insert_at, bk_start)
    p.append(bk_end)


# ── Font helpers ───────────────────────────────────────────────────────────────

def _set_run_font(run, font_name: str) -> None:
    """Set the font family on a run for all character sets.

    Sets ``w:ascii``, ``w:hAnsi``, and ``w:cs`` on the run's ``<w:rFonts>``
    element and removes any theme-font attributes (``w:asciiTheme``,
    ``w:hAnsiTheme``, ``w:cstheme``) that would otherwise let Word's document
    theme override the explicit font name (typically substituting Calibri or
    Calibri Light).

    Args:
        run: The ``docx.text.run.Run`` whose font to set.
        font_name: The font family name to apply, e.g. ``"Inter"`` or
            ``"JetBrains Mono"``.
    """
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


def _set_style_font(style, font_name: str) -> None:
    """Set the font family on a paragraph style for all character sets.

    Mirrors the logic of ``_set_run_font`` but operates on a style element
    rather than a run.  Sets ``w:ascii``, ``w:hAnsi``, and ``w:cs`` and
    strips all theme-font overrides, ensuring the heading and body styles
    consistently use the specified typeface.

    Args:
        style: A ``docx.styles.style._ParagraphStyle`` to update.
        font_name: The font family name to apply.
    """
    style.font.name = font_name           # sets w:ascii + w:hAnsi
    rPr = style.font._element             # w:rPr element inside w:style
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


def _set_style_bottom_border(style, color: RGBColor, sz: str) -> None:
    """Add a bottom paragraph border to a named paragraph style.

    Creates or replaces the ``<w:pBdr><w:bottom>`` element inside the style's
    ``<w:pPr>`` block.  If ``<w:pPr>`` or ``<w:pBdr>`` do not yet exist they
    are inserted automatically.  A pre-existing ``<w:bottom>`` child is removed
    before the new one is appended so the call is idempotent.

    Used during style initialisation to give Heading 1 (18 eighths-of-a-pt
    line) and Heading 2 (6 eighths-of-a-pt line) their characteristic
    underlines at the style level, avoiding paragraph-level overrides for
    every heading instance.

    Args:
        style: A ``docx.styles.style._ParagraphStyle`` to update.
        color: ``RGBColor`` for the border line.
        sz: Border width in OOXML ``w:sz`` units (eighths-of-a-point) as a
            decimal string, e.g. ``"18"`` for 2.25 pt or ``"6"`` for 0.75 pt.
    """
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
    hex_color = f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"
    bottom.set(qn("w:val"),   "single")
    bottom.set(qn("w:sz"),    sz)
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), hex_color)
    pBdr.append(bottom)


# Space before/after headings, in points.
# H1 has 0 before: always at the top of a section (page-break or document start).
# H2 24 pt before ≈ 2 blank lines — clearly separates major sections.
# H3–H6 taper proportionally with their visual weight.
# Space-after is small (4–8 pt) so the heading stays close to its following content.
_HEADING_SPACE_BEFORE = {1: 0,  2: 24, 3: 18, 4: 14, 5: 10, 6: 10}
_HEADING_SPACE_AFTER  = {1: 8,  2: 8,  3: 6,  4: 5,  5: 4,  6: 4}
_HEADING_COLORS = {
    1: C_H1_TEXT,
    2: C_H2_TEXT,
    3: C_H3_TO_H5,
    4: C_H3_TO_H5,
    5: C_H3_TO_H5,
    6: C_H6_TEXT,
}


def _customize_heading_styles(doc: Document) -> None:
    """Apply corporate typography to Word's built-in Heading 1–6 styles.

    Iterates over heading levels 1–6 and for each present style sets:

    * Font family (``FONT_HEADING``), size (``HEADING_SIZE[level]``),
      weight (``HEADING_BOLD[level]``), and colour (``_HEADING_COLORS[level]``).
    * Paragraph spacing-before / spacing-after from ``_HEADING_SPACE_BEFORE``
      and ``_HEADING_SPACE_AFTER``.
    * ``keep_with_next = True`` so headings are never orphaned at page breaks.
    * A bottom paragraph border for H1 (2.25 pt, ``C_H1_BORDER``) and H2
      (0.75 pt, ``C_H2_BORDER``) via ``_set_style_bottom_border``.

    Operating at the style level ensures compatibility with Word's Navigation
    Pane, automatic table-of-contents generation, and heading-numbering
    cross-references.

    Args:
        doc: The ``Document`` whose heading styles to customise.  Must have
            been freshly created by ``_setup_document``.
    """
    for level in range(1, 7):
        try:
            style = doc.styles[f"Heading {level}"]
        except KeyError:
            continue
        _set_style_font(style, FONT_HEADING)
        style.font.size    = Pt(HEADING_SIZE[level])
        style.font.bold    = HEADING_BOLD[level]
        style.font.italic  = False
        style.font.color.rgb = _HEADING_COLORS[level]
        pf = style.paragraph_format
        pf.space_before   = Pt(_HEADING_SPACE_BEFORE[level])
        pf.space_after    = Pt(_HEADING_SPACE_AFTER[level])
        pf.keep_with_next = True
        if level == 1:
            _set_style_bottom_border(style, C_H1_BORDER, "18")
        elif level == 2:
            _set_style_bottom_border(style, C_H2_BORDER, "6")


# ── Run-level formatting helpers ───────────────────────────────────────────────

def _apply_run_style(run, *, bold=False, italic=False, strike=False,
                     color: RGBColor | None = None,
                     font_name: str | None = None,
                     font_size: float | None = None,
                     highlight_color: RGBColor | None = None) -> None:
    """Apply visual formatting attributes to a run in a single call.

    Centralises all run-level style mutations so callers do not need to
    interact with ``run.font`` directly. Only non-``None`` / truthy arguments
    are applied; omitted keyword arguments leave the corresponding run
    attribute unchanged.

    Note:
        Word does not support arbitrary highlight colours via the high-level
        font API.  When ``highlight_color`` is provided the run's **font
        colour** is set to ``C_CODE_TEXT`` instead, which approximates the
        visual intent of a shaded inline-code background without requiring
        complex character-level OOXML shading (``<w:rPrChange>``).

    Args:
        run: The ``docx.text.run.Run`` to style.
        bold: If ``True``, set the run bold.
        italic: If ``True``, set the run italic.
        strike: If ``True``, apply single strikethrough.
        color: ``RGBColor`` for the run's font colour.  ``None`` leaves
            the colour inherited from the paragraph style.
        font_name: Font family name.  When provided, ``_set_run_font`` is
            called to also clear theme-font overrides.
        font_size: Font size in points.  ``None`` leaves the size inherited.
        highlight_color: Accepted for API symmetry but redirected to
            ``C_CODE_TEXT`` as described in the note above.
    """
    if font_name:
        _set_run_font(run, font_name)
    if font_size is not None:
        run.font.size = Pt(font_size)
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    if strike:
        run.font.strike = True
    if color:
        run.font.color.rgb = color
    if highlight_color:
        # Word doesn't support arbitrary highlight colours via the font API;
        # we embed inline code by shading the character run with an rPrChange.
        # The simplest approach is to just set the *font colour* for inline code
        # since a character-level shading requires complex OOXML.
        run.font.color.rgb = C_CODE_TEXT


# ── Inline HTML → runs ─────────────────────────────────────────────────────────

def _inline_nodes_to_runs(para, node: Tag | NavigableString,
                           bold=False, italic=False, strike=False,
                           color: RGBColor | None = None,
                           is_code_block=False) -> None:
    """Recursively walk an inline BeautifulSoup node and add formatted runs.

    Traverses the tree rooted at ``node`` depth-first, accumulating
    formatting flags (``bold``, ``italic``, ``strike``, ``color``) as it
    descends into nested tags.  At each leaf ``NavigableString`` the
    accumulated flags are applied to a new run added to ``para``.

    Special handling per tag type:

    * ``strong`` / ``b``: sets ``bold=True`` for the subtree.
    * ``em`` / ``i``: sets ``italic=True`` for the subtree.
    * ``del``: sets ``strike=True`` for the subtree.
    * ``code`` (inline): renders a single run in ``FONT_MONO`` at
      ``FONT_CODE_PT`` with ``C_CODE_TEXT`` colour, ignoring inherited colour.
    * ``a`` with ``href="#…"`` (internal link): wraps rendered child runs in
      a ``<w:hyperlink w:anchor="…">`` element so Word navigates to the
      bookmark when clicked.
    * ``a`` with external / no ``href``: renders children in ``C_LINK`` blue
      (no clickable relationship added).
    * ``span.math-inline``: delegates to ``_insert_math_inline`` for
      Word-native OMML equation rendering.
    * Plain ``NavigableString``: split by emoji via ``_split_by_emoji``,
      then each segment is assigned the appropriate font and colour
      (color-circle strategy 1 / generic-emoji strategy 2 / plain text).

    Args:
        para: The ``docx.text.paragraph.Paragraph`` to append runs to.
        node: A BeautifulSoup ``Tag`` or ``NavigableString`` to process.
        bold: Inherited bold flag from an ancestor ``<strong>`` / ``<b>``.
        italic: Inherited italic flag from an ancestor ``<em>`` / ``<i>``.
        strike: Inherited strikethrough flag from an ancestor ``<del>``.
        color: Inherited font colour from an ancestor tag (e.g. heading
            colour, blockquote colour, or ``C_LINK`` for links).
        is_code_block: When ``True`` the leaf runs use ``FONT_MONO`` and
            ``FONT_CODE_PT`` regardless of other flags.  Used when rendering
            content inside fenced code blocks.
    """
    if isinstance(node, NavigableString):
        text = str(node)
        if not text:
            return
        fn         = FONT_MONO if is_code_block else FONT_BODY
        fpt        = FONT_CODE_PT if is_code_block else FONT_BODY_PT
        base_color = color or C_BODY
        for kind, val in _split_by_emoji(text):
            if kind == "text":
                run = para.add_run(val)
                _apply_run_style(
                    run,
                    bold=bold, italic=italic, strike=strike,
                    color=base_color, font_name=fn, font_size=fpt,
                )
            elif val in _CIRCLE_EMOJI:
                # Strategy 1: replace color-circle with ● and apply its color
                run = para.add_run(_BLACK_CIRCLE)
                _apply_run_style(
                    run, bold=bold, font_name=fn, font_size=fpt,
                    color=_CIRCLE_EMOJI[val],
                )
            else:
                # Strategy 2: keep emoji char, use Segoe UI Emoji + repr. color
                emoji_color = _EMOJI_COLOR.get(val, base_color)
                run = para.add_run(val)
                _apply_run_style(
                    run, bold=bold, font_name="Segoe UI Emoji",
                    font_size=fpt, color=emoji_color,
                )
        return

    tag = node.name
    new_bold   = bold   or tag in ("strong", "b")
    new_italic = italic or tag in ("em", "i")
    new_strike = strike or tag == "del"
    new_color  = color

    if tag == "code":
        # Inline code run
        run = para.add_run(node.get_text())
        _apply_run_style(
            run,
            bold=bold,
            italic=italic,
            color=C_CODE_TEXT,
            font_name=FONT_MONO,
            font_size=FONT_CODE_PT,
        )
        return

    if tag == "a":
        href = node.get("href", "")
        if href.startswith("#"):
            # ── Internal hyperlink ────────────────────────────────────────────
            # w:anchor references the bookmark name placed on the target heading.
            # No relationship entry (r:id) is needed — w:anchor is self-contained.
            anchor = href[1:]   # strip leading "#"; the fragment is already a slug
            hyperlink = OxmlElement("w:hyperlink")
            hyperlink.set(qn("w:anchor"), anchor)

            # Render the link text as normal runs appended to para, then move
            # every newly-added element into the hyperlink wrapper.
            p_elem = para._p
            idx_before = len(p_elem)
            for child in node.children:
                _inline_nodes_to_runs(
                    para, child,
                    bold=bold, italic=italic, strike=strike,
                    color=C_LINK, is_code_block=is_code_block,
                )
            new_els = list(p_elem)[idx_before:]
            for el in new_els:
                p_elem.remove(el)
                hyperlink.append(el)
            p_elem.append(hyperlink)
            return
        # External link: keep current behavior (blue text, no clickable hyperlink)
        new_color = C_LINK

    if tag in ("strong", "b"):
        new_color = new_color  # keep parent color for bold inside headings

    if tag == "span" and "math-inline" in node.get("class", []):
        # Inline math: render as Word-native OMML equation
        _insert_math_inline(para, node.get_text())
        return

    for child in node.children:
        _inline_nodes_to_runs(
            para, child,
            bold=new_bold,
            italic=new_italic,
            strike=new_strike,
            color=new_color or color,
            is_code_block=is_code_block,
        )


# ── Block-level rendering ──────────────────────────────────────────────────────

def _render_heading(doc: Document, tag: Tag, level: int) -> None:
    """Render a Markdown heading as a Word built-in Heading style.

    Uses ``doc.add_paragraph(style=f"Heading {level}")`` so the generated
    document supports Word's Navigation Pane and automatic table-of-contents
    insertion.  Colour, font size, spacing, and bottom borders are all
    inherited from the style configured in ``_customize_heading_styles``;
    this function only adds run-level overrides for inline elements such as
    links, inline code, and emoji.

    After rendering all child runs it:

    1. Re-applies ``FONT_HEADING`` (or ``FONT_MONO`` where appropriate) on
       every run to prevent Word's theme-font mechanism from substituting
       Calibri / Calibri Light.
    2. Registers a slug-based bookmark (``_add_bookmark``) so
       ``[text](#slug)`` internal links can navigate here.
    3. If a naked ``<a id="...">`` anchor immediately preceded this heading
       in the Markdown source, adopts that explicit id as a second bookmark
       target (allows both auto-generated and author-defined fragments).

    Args:
        doc: The ``Document`` to append the heading paragraph to.
        tag: The BeautifulSoup heading ``Tag`` (e.g. ``<h1>``, ``<h2>``).
        level: Heading depth, 1–6, mapping to ``Heading 1`` – ``Heading 6``.
    """
    para = doc.add_paragraph(style=f"Heading {level}")
    color = _HEADING_COLORS[level]
    for child in tag.children:
        _inline_nodes_to_runs(para, child, bold=HEADING_BOLD[level], color=color)

    # Enforce the correct font on every run so theme-font fallback is avoided.
    for run in para.runs:
        fn = run.font.name
        _set_run_font(run, FONT_MONO if fn == FONT_MONO else FONT_HEADING)

    # Add a bookmark so internal links ([text](#slug)) can jump to this heading.
    # Always register a slug-based bookmark for links that use auto-generated fragments.
    # If a naked <a id="..."> anchor immediately preceded this heading in the source,
    # also register that explicit id (e.g. "p1") — which is what table links typically use.
    global _pending_anchor
    slug = _heading_slug(tag.get_text(" ", strip=True))
    _add_bookmark(para, slug)
    if _pending_anchor:
        _add_bookmark(para, _pending_anchor)
        _pending_anchor = None


def _render_paragraph(doc: Document, tag: Tag,
                       indent_twips: int = 0,
                       extra_color: RGBColor | None = None,
                       is_blockquote: bool = False) -> None:
    """Render a ``<p>`` tag as a styled body paragraph.

    Creates a new paragraph using the document's ``Normal`` style, then
    calls ``_inline_nodes_to_runs`` for each child to populate it.  After
    all runs are created, any run that lacks an explicit font name or size
    receives the body defaults (``FONT_BODY`` / ``FONT_BODY_PT``) as a
    safety net.

    When ``is_blockquote=True`` the paragraph also receives:

    * A solid background shading (``C_BQ_BG``) via ``_set_para_shading``.
    * A left border (``C_BQ_BORDER``) via ``_set_para_border_left``.

    Note:
        This function is called only when the ``<p>`` appears **outside** a
        blockquote text-box.  Paragraphs inside blockquotes are written to the
        scratch ``Document`` used by ``_render_blockquote``.

    Args:
        doc: The ``Document`` to append the paragraph to.
        tag: The BeautifulSoup ``<p>`` ``Tag`` whose children to render.
        indent_twips: Optional left indentation in twips.  Used when the
            paragraph belongs to a list continuation block.
        extra_color: Override run colour.  When ``None`` the default body
            colour (``C_BODY``) is used.
        is_blockquote: When ``True`` applies blockquote visual styling
            (background shading + left border).
    """
    para = doc.add_paragraph()
    _no_space_before(para)
    _set_para_space_after(para, 7)

    for child in tag.children:
        _inline_nodes_to_runs(para, child, color=extra_color or C_BODY)

    for run in para.runs:
        if not run.font.name:
            _set_run_font(run, FONT_BODY)
        if not run.font.size:
            run.font.size = Pt(FONT_BODY_PT)

    if indent_twips:
        _set_para_indent(para, indent_twips)
    if is_blockquote:
        _set_para_shading(para, C_BQ_BG)
        _set_para_border_left(para, C_BQ_BORDER)


def _render_code_block(doc: Document, tag: Tag) -> None:
    """Render a ``<pre><code>`` fenced code block as a dark-themed paragraph.

    Extracts the plain-text content from the ``<code>`` child (or directly
    from ``<pre>`` if no ``<code>`` child exists), strips the trailing
    newline that markdown-it appends, and renders the block as a single
    paragraph with:

    * Dark background shading (``C_PRE_BG``, ``#1E2030``).
    * Monospace font (``FONT_MONO`` / ``FONT_CODE_PT``).
    * Light text colour (``C_PRE_TEXT``, ``#C8D3F5``).
    * Single-line spacing (240 twentieths-of-a-pt = 12 pt, ``lineRule="auto"``).
    * Slight left indent (180 twips = 0.125 in) to lift text off the shading
      edge.

    Syntax highlighting (Pygments) is applied at the HTML level in
    ``generate_pdfs.py`` only; in the Word pipeline the raw source text is
    rendered unstyled to avoid injecting HTML-specific span tags into OOXML.

    Args:
        doc: The ``Document`` to append the code block paragraph to.
        tag: The BeautifulSoup ``<pre>`` ``Tag`` containing the code content.
    """
    code_tag = tag.find("code")
    text = code_tag.get_text() if code_tag else tag.get_text()
    # Remove trailing newline added by markdown-it
    text = text.rstrip("\n")

    para = doc.add_paragraph()
    _no_space_before(para)
    _set_para_space_after(para, 8)
    _set_para_shading(para, C_PRE_BG)
    _set_para_indent(para, 180)  # 180 twips = 0.125 in — slight left indent lifts code off the shading edge

    run = para.add_run(text)
    _set_run_font(run, FONT_MONO)
    run.font.size  = Pt(FONT_CODE_PT)
    run.font.color.rgb = C_PRE_TEXT

    pPr = para._p.get_or_add_pPr()
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:line"),     "240")  # 240 twentieths-of-a-pt = 12 pt (single spacing)
    spacing.set(qn("w:lineRule"), "auto") # "auto": Word scales line height from font; prevents clipping
    pPr.append(spacing)


def _render_table(doc: Document, tag: Tag) -> None:
    """Render a Markdown table (``<table>``) as a python-docx ``Table``.

    Builds a ``doc.add_table``\u2060() grid sized to the maximum column count
    found across all ``<tr>`` rows, then fills each cell by calling
    ``_inline_nodes_to_runs`` on its BeautifulSoup children.

    Styling applied per row type:

    * **Header row** (any ``<th>`` cell): solid ``C_TH_BG`` background;
      white (``C_TH_TEXT``) bold text; no bottom border override.
    * **Even data rows** (0-indexed): alternating ``C_TD_ALT_BG`` shading.
    * **Odd data rows**: no shading (transparent / white).
    * **All data cells**: hairline bottom border (``C_TD_BORDER``) via
      ``_set_cell_border``.

    Cell text is rendered at ``FONT_CODE_PT`` (9 pt) — 1.5 pt smaller than
    body text — so multi-column tables fit within the A4 text column without
    horizontal overflow.

    Args:
        doc: The ``Document`` to append the table to.
        tag: The BeautifulSoup ``<table>`` ``Tag`` to convert.
    """
    rows_tags = tag.find_all("tr")
    if not rows_tags:
        return

    # Count max columns
    num_cols = max(
        len(r.find_all(["th", "td"])) for r in rows_tags
    )
    if num_cols == 0:
        return

    tbl = doc.add_table(rows=len(rows_tags), cols=num_cols)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT

    for r_idx, row_tag in enumerate(rows_tags):
        cells_tags = row_tag.find_all(["th", "td"])
        is_header  = any(c.name == "th" for c in cells_tags)

        for c_idx, cell_tag in enumerate(cells_tags):
            if c_idx >= num_cols:
                break
            cell = tbl.cell(r_idx, c_idx)

            if is_header:
                _set_cell_shading(cell, C_TH_BG)
            elif r_idx % 2 == 0:
                _set_cell_shading(cell, C_TD_ALT_BG)

            # Clear default empty paragraph and write content
            para = cell.paragraphs[0]
            para.clear()
            _no_space_before(para)
            _set_para_space_after(para, 4)

            txt_color = C_TH_TEXT if is_header else C_BODY
            for child in cell_tag.children:
                _inline_nodes_to_runs(para, child, color=txt_color,
                                      bold=is_header)

            for run in para.runs:
                _set_run_font(run, FONT_BODY)
                run.font.size = Pt(FONT_CODE_PT)  # FONT_CODE_PT (9.0 pt) — slightly smaller than body to fit more columns
                if is_header:
                    run.font.color.rgb = C_TH_TEXT
                    run.bold = True

            if not is_header:
                _set_cell_border(cell, C_TD_BORDER)


def _render_list(doc: Document, tag: Tag, level: int = 0) -> None:
    """Render a ``<ul>`` or ``<ol>`` element, including nested lists.

    Iterates over ``<li>`` children and creates one bullet paragraph per item.
    Nesting up to three levels is supported: each deeper level adds 0.25 in
    (360 twips) to the absolute left indent.

    CommonMark *loose* list items (where a blank line separates items) are
    handled explicitly:

    * The first ``<p>`` inside a ``<li>`` becomes the bullet-run text appended
      to the same paragraph as the bullet symbol / number prefix.
    * Subsequent block-level children (``<p>``, ``<div class="math-block">``,
      ``<table>``, ``<hr>``, nested ``<ul>`` / ``<ol>``) are rendered as
      independent Word paragraphs indented to the text column
      (``indent_text = indent_left + hanging_indent``).

    Indent constants (in OOXML twips, 1 twip = 1/20 pt):

    * ``indent_left``  = ``360 + level * 360``  (absolute left edge of block).
    * ``indent_hang``  = ``360``  (hanging indent; bullet stays at left edge).
    * ``indent_text``  = ``indent_left + indent_hang``  (wrapped-text column).

    Args:
        doc: The ``Document`` to append list paragraphs to.
        tag: The BeautifulSoup ``<ul>`` or ``<ol>`` ``Tag`` to render.
        level: Current nesting depth (0-based).  Passed recursively when a
            ``<li>`` contains a nested list.
    """
    is_ordered = tag.name == "ol"
    counter    = 1

    # Block-level tag names that may appear as direct children of a <li>
    _BLOCK_IN_LI = {"p", "div", "table", "hr", "pre", "blockquote", "ul", "ol"}

    for child in tag.children:
        if isinstance(child, NavigableString):
            continue
        if child.name != "li":
            continue

        # 360 twips = 0.25 in: the standard indent step used by Word's built-in list styles.
        # indent_left: absolute left edge of the item block (shifts right per nesting level).
        # indent_hang: hanging indent — the bullet/number sits at indent_left while wrapped
        #              text aligns at indent_left + indent_hang (= indent_text).
        indent_left = 360 + level * 360   # 0.25 in base + 0.25 in per nesting level
        indent_hang = 360                 # 0.25 in hanging indent — matches Word's built-in list hang
        indent_text = indent_left + indent_hang   # absolute column where item text begins

        if is_ordered:
            prefix = f"{counter}.\t"
            counter += 1
        else:
            prefix = "•\t"

        # ── Bullet paragraph ──────────────────────────────────────────────────
        para = doc.add_paragraph()
        _no_space_before(para)
        _set_para_space_after(para, 3)   # 3 pt — tighter than body (7 pt) to keep list items visually grouped
        pPr = para._p.get_or_add_pPr()
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"),    str(indent_text))
        ind.set(qn("w:hanging"), str(indent_hang))
        pPr.append(ind)

        run_prefix = para.add_run(prefix)
        _set_run_font(run_prefix, FONT_BODY)
        run_prefix.font.size      = Pt(FONT_BODY_PT)
        run_prefix.font.color.rgb = C_BODY

        # ── Walk <li> children ────────────────────────────────────────────────
        # In CommonMark "loose" lists each <li> wraps its first paragraph in a
        # <p> tag.  Subsequent block-level siblings (more <p>s, math divs,
        # tables, rules, nested lists) must be rendered as separate Word objects
        # indented to the text column, not stuffed into the bullet paragraph.
        first_block_done = False

        for li_child in child.children:

            # ── Plain text node ───────────────────────────────────────────────
            if isinstance(li_child, NavigableString):
                text = str(li_child)
                if text.strip():
                    run = para.add_run(text)
                    _set_run_font(run, FONT_BODY)
                    run.font.size      = Pt(FONT_BODY_PT)
                    run.font.color.rgb = C_BODY
                    first_block_done = True
                continue

            # ── Block children ────────────────────────────────────────────────
            if li_child.name not in _BLOCK_IN_LI:
                # Inline element: add to current bullet paragraph
                _inline_nodes_to_runs(para, li_child, color=C_BODY)
                continue

            if li_child.name == "p":
                if not first_block_done:
                    # First <p> → inline with bullet
                    for sub in li_child.children:
                        _inline_nodes_to_runs(para, sub, color=C_BODY)
                    first_block_done = True
                else:
                    # Continuation <p> → new indented paragraph
                    cont = doc.add_paragraph()
                    _no_space_before(cont)
                    _set_para_space_after(cont, 3)
                    _set_para_indent(cont, indent_text)
                    for sub in li_child.children:
                        _inline_nodes_to_runs(cont, sub, color=C_BODY)
                    for run in cont.runs:
                        if not run.font.size:
                            run.font.size = Pt(FONT_BODY_PT)

            elif li_child.name == "div" and "math-block" in li_child.get("class", []):
                # Display equation inside a list item
                _insert_math_block(doc, li_child.get_text(strip=True))

            elif li_child.name in ("ul", "ol"):
                _render_list(doc, li_child, level=level + 1)

            elif li_child.name == "table":
                _render_table(doc, li_child)

            elif li_child.name == "hr":
                _render_hr(doc)

            elif li_child.name == "pre":
                _render_code_block(doc, li_child)

            elif li_child.name == "blockquote":
                _render_blockquote(doc, li_child)

            else:
                # Unknown block — fall back to plain text
                text = li_child.get_text(" ", strip=True)
                if text:
                    cont = doc.add_paragraph(text)
                    _set_para_space_after(cont, 3)

            first_block_done = True

        for run in para.runs:
            if not run.font.size:
                run.font.size = Pt(FONT_BODY_PT)


def _bq_estimate_height_emu(tag: Tag) -> int:
    """Estimate the rendered height of a blockquote's content in EMU.

    Performs a width-aware line-count estimation for each block element nested
    inside the blockquote, then converts the total height from points to EMU
    (English Metric Units, 1 pt = 12 700 EMU) for use as the DrawingML shape's
    initial ``cy`` attribute.

    The calculation accounts for:

    * ``<p>`` elements: line count derived from character count vs. usable
      text-box width.
    * ``<ul>`` / ``<ol>`` items: lines estimated per item using the same
      character-width model at list-item font size.
    * ``<table>`` rows: fixed row-height constant per row.
    * ``<div class="math-block">``: fixed 2.5-line height for display equations.
    * ``<pre>`` code blocks: line count from newline occurrences.
    * Nested ``<blockquote>`` elements: recursively calls itself.
    * Internal top/bottom padding of the text box (``tIns`` / ``bIns``).
    * Per-paragraph ``space_after`` (4 pt for paragraphs, 3 pt for list items).
    * A proportional 10% safety margin (minimum 4 pt) to prevent clipping.

    Note:
        The shape uses ``<a:spAutoFit>`` so Word will expand if the estimate is
        undershot.  Accuracy mainly affects the ``adj`` (corner-radius)
        calculation rather than whether text clips.

    Args:
        tag: The BeautifulSoup ``<blockquote>`` ``Tag`` whose children to
            measure.

    Returns:
        Estimated height in EMU as an integer.
    """
    # ── Constants (must stay in sync with _render_blockquote) ────────────────
    FONT_PT      = FONT_BODY_PT - 0.5          # 10.0 pt — <p> inside BQ
    FONT_LIST_PT = FONT_BODY_PT                 # 10.5 pt — list items use full body size
    # Word "single" spacing ≈ 120 % of font size (auto line-rule).
    LINE_H_PT    = FONT_PT      * 1.20         # 12.0 pt
    LINE_H_LIST  = FONT_LIST_PT * 1.20         # 12.6 pt
    SPACE_AFT_PT = 4.0    # mirrors _set_para_space_after(para, 4) used in _render_blockquote scratch paragraphs
    SPACE_AFT_LI = 3.0    # mirrors _set_para_space_after(para, 3) used in _render_list
    MATH_LINES   = 2.5    # a typical display equation (fraction, integral, sum) renders ~2.5 body lines tall in OMML
    TABLE_ROW_PT = LINE_H_PT + SPACE_AFT_PT    # one row ≈ one text line + its space_after

    # Internal text-box padding mirrors bodyPr tIns/bIns attributes in _render_blockquote.
    # 45720 EMU ÷ 12700 EMU/pt = 3.6 pt per side (both top and bottom use the same value).
    PAD_TOP_PT = 45720 / 12700    # 3.6 pt (= tIns on bodyPr, converted from EMU by / 12700)
    PAD_BOT_PT = 45720 / 12700    # 3.6 pt (= bIns on bodyPr, converted from EMU by / 12700)

    # lIns = rIns = 91440 EMU (horizontal text-box padding in _render_blockquote).
    # 91440 EMU ÷ 360000 EMU/cm = 0.254 cm per side.
    # 15.5 cm shape width − 2 × 0.254 cm padding = 14.99 cm usable text width.
    # 28.35 pt/cm: typographic conversion (1 in = 2.54 cm = 72 pt → 1 cm = 28.346 pt).
    # 0.60 × font_pt gives the average character width in pt for Segoe UI / Inter.
    # More conservative than the naive 0.52 to account for accented characters,
    # emojis and word-boundary effects that push lines over the count estimate.
    USABLE_W_CM    = 15.5 - 2 * (91440 / 360000)              # 15.5 cm − 2 × 0.254 cm ≈ 14.99 cm
    CHARS_PER_LINE = USABLE_W_CM * 28.35 / (FONT_PT      * 0.60)  # usable_pt / avg_char_pt ≈ 70.8
    CHARS_PER_LIST = USABLE_W_CM * 28.35 / (FONT_LIST_PT * 0.60)  # same for 10.5 pt list text ≈ 67.6

    def _count_lines(text: str, chars_per_line: float = CHARS_PER_LINE) -> float:
        """Estimate wrapped line count for a plain-text string.

        Args:
            text: The string whose rendered line count to estimate.
            chars_per_line: Average characters that fit on one line.  Defaults
                to ``CHARS_PER_LINE`` computed for paragraph text.

        Returns:
            Estimated number of wrapped lines as a float.  Always ≥ 1.0 for
            non-empty strings; 0.0 for blank strings.
        """
        chars = len(text.strip())
        return 0.0 if chars == 0 else max(1.0, chars / chars_per_line)

    def _li_primary_text(li_tag) -> str:
        """Extract the visible text of a list item, excluding sub-list content.

        Concatenates text from all direct children of ``li_tag`` that are not
        nested ``<ul>`` or ``<ol>`` elements.  Used so that sub-list items
        are counted separately by the caller rather than inflating the parent
        item's line estimate.

        Args:
            li_tag: A BeautifulSoup ``<li>`` ``Tag``.

        Returns:
            Space-joined plain text string of the item's own content.
        """
        parts = []
        for c in li_tag.children:
            if isinstance(c, NavigableString):
                parts.append(str(c))
            elif hasattr(c, "name") and c.name not in ("ul", "ol"):
                parts.append(c.get_text())
        return " ".join(parts)

    def _walk(node: Tag) -> float:
        """Recursively sum the estimated height (in points) for all block children.

        Traverses direct children of ``node`` and dispatches to per-element
        height formulas.  Calls itself recursively for nested ``<blockquote>``
        elements.

        Args:
            node: A BeautifulSoup ``Tag`` whose children to measure.

        Returns:
            Total estimated height in typographic points.
        """
        total = 0.0
        for child in node.children:
            if isinstance(child, NavigableString):
                txt = str(child).strip()
                if txt:
                    total += _count_lines(txt) * LINE_H_PT + SPACE_AFT_PT
                continue
            if not hasattr(child, "name") or child.name is None:
                continue
            name = child.name
            if name == "p":
                total += _count_lines(child.get_text()) * LINE_H_PT + SPACE_AFT_PT
            elif name in ("ul", "ol"):
                for li in child.find_all("li", recursive=False):
                    # Count wrapped lines for item's own text (not sub-list text)
                    li_lines = _count_lines(_li_primary_text(li), CHARS_PER_LIST)
                    total += li_lines * LINE_H_LIST + SPACE_AFT_LI
                    # One level of nested sub-lists
                    for sub in li.find_all(["ul", "ol"], recursive=False):
                        for sub_li in sub.find_all("li", recursive=False):
                            sub_lines = _count_lines(
                                _li_primary_text(sub_li), CHARS_PER_LIST
                            )
                            total += sub_lines * LINE_H_LIST + SPACE_AFT_LI
            elif name == "div" and "math-block" in child.get("class", []):
                total += MATH_LINES * LINE_H_PT + 10.0
            elif name == "table":
                rows = child.find_all("tr")
                total += len(rows) * TABLE_ROW_PT
            elif name == "hr":
                total += 12.0   # <hr> renders as a 0.5 pt line with 12 pt space_after (see _render_hr)
            elif name == "pre":
                lines = child.get_text().count("\n") + 1
                total += lines * LINE_H_PT + 8.0   # 8 pt = space_after set on code block paragraphs
            elif name == "blockquote":
                total += _bq_estimate_height_emu(child) / 12700
        return total

    content_pt = _walk(tag)

    # Safety margin: proportional (10 % of content) so long blockquotes where
    # multiple lines are underestimated still have headroom; minimum 4 pt prevents
    # very short blockquotes from having descenders touch the border.
    # NOTE: shape uses <a:spAutoFit> so Word will expand if content overflows;
    # HEIGHT_EMU is only the initial layout hint — accuracy matters most for the
    # adj (corner radius) calculation, not for whether text is clipped.
    safety_pt = max(4.0, content_pt * 0.10)
    total_pt  = PAD_TOP_PT + content_pt + PAD_BOT_PT + safety_pt

    return int(total_pt * 12700)


def _render_blockquote(doc: Document, tag: Tag) -> None:
    """Render a ``<blockquote>`` as a rounded-rectangle inline text box.

    Creates a DrawingML ``WordprocessingShape`` (``<wps:wsp>``) wrapped in a
    ``<wp:inline>`` element so that the box sits exactly in the text flow
    with zero positional drift (unlike floating anchors).

    Shape properties:

    * **Fill**: solid ``C_BQ_BG`` (``#EFF6FF``, light blue).
    * **Border**: 1 pt solid ``C_BQ_BORDER`` (``#2563EB``, blue).
    * **Preset**: ``roundRect`` with a fixed 6 pt corner radius (implemented
      as a proportional ``adj`` so the physical radius stays constant at any
      height).
    * **Width**: 15.5 cm (A4 with 2.5 cm margins, matching the page text
      column).
    * **Height**: calculated by ``_bq_estimate_height_emu`` from content.
    * **Vertical align**: top; **layout**: ``<wp:inline>``.

    Implementation stages:

    1. Render all blockquote children (``<p>``, ``<ul>``/``<ol>``,
       ``<div.math-block>``, ``<table>``, ``<hr>``, ``<pre>``,
       nested ``<blockquote>``) into a scratch ``Document`` using the same
       rendering functions as the main pipeline.
    2. Harvest the ``<w:body>`` XML from the scratch document.
    3. Build the full DrawingML / OOXML shape tree by string concatenation
       (no python-docx helpers exist for ``<wps:wsp>``), substituting the
       harvested body XML as the text-box content.
    4. Append the resulting ``<w:drawing>`` element to a new empty paragraph
       in ``doc``.

    Note:
        ``<wp:inline>`` vs ``<wp:anchor wrapTopAndBottom>``:
        A floating anchor's visual position is computed independently of its
        host paragraph, creating a visible gap above full-column-width shapes.
        An inline drawing is treated as a character filling the paragraph's
        height exactly, so there is no drift.

    Args:
        doc: The ``Document`` to append the blockquote shape to.
        tag: The BeautifulSoup ``<blockquote>`` ``Tag`` to render.
    """
    import copy

    # ── 1. Render blockquote children into a scratch Document ─────────────────
    scratch = _setup_document()
    for p in scratch.paragraphs:
        p._element.getparent().remove(p._element)

    for child in tag.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                para = scratch.add_paragraph()
                _no_space_before(para)
                _set_para_space_after(para, 4)
                run = para.add_run(text)
                _set_run_font(run, FONT_BODY)
                run.font.size = Pt(FONT_BODY_PT - 0.5)
                run.font.color.rgb = C_BQ_TEXT
        elif child.name == "p":
            para = scratch.add_paragraph()
            _no_space_before(para)
            _set_para_space_after(para, 4)
            for sub in child.children:
                _inline_nodes_to_runs(para, sub, color=C_BQ_TEXT)
            for run in para.runs:
                _set_run_font(run, FONT_BODY)
                run.font.size = Pt(FONT_BODY_PT - 0.5)
        elif child.name in ("ul", "ol"):
            _render_list(scratch, child)
        elif child.name == "blockquote":
            _render_blockquote(scratch, child)
        elif child.name == "div" and "math-block" in child.get("class", []):
            _insert_math_block(scratch, child.get_text(strip=True))
        elif child.name == "table":
            _render_table(scratch, child)
        elif child.name == "hr":
            _render_hr(scratch)
        elif child.name == "pre":
            _render_code_block(scratch, child)

    scratch_body = scratch.element.body

    # ── 2. OOXML namespace helpers ────────────────────────────────────────────
    _NS = {
        "a":   "http://schemas.openxmlformats.org/drawingml/2006/main",
        "wp":  "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
        "w":   "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    }

    def _sub(parent, ns_key, local, **attribs) -> _lxml_etree._Element:
        """Create a namespaced child element and set attributes on it.

        A thin convenience wrapper around ``lxml.etree.SubElement`` that
        resolves namespace prefixes from the local ``_NS`` mapping so callers
        use short keys such as ``"a"``, ``"wp"``, or ``"wps"`` instead of full
        Clark-notation URIs.

        Args:
            parent: The parent ``lxml`` element to append the new child to.
            ns_key: Namespace prefix key into ``_NS``, e.g. ``"a"`` for
                DrawingML main, ``"wp"`` for wordprocessingDrawing, ``"wps"``
                for wordprocessingShape.
            local: Local element name without namespace, e.g. ``"solidFill"``.
            **attribs: Keyword arguments converted to XML attributes on the
                new element.  Values are coerced to ``str`` automatically.

        Returns:
            The newly created ``lxml.etree._Element`` child.
        """
        for k, v in attribs.items():
            child_el.set(k, str(v))
        return child_el

    def _hex(c: RGBColor) -> str:
        """Format an ``RGBColor`` as an uppercase 6-digit hex string.

        Args:
            c: An ``RGBColor`` (subscript-indexable, ``c[0]`` = R, ``c[1]`` = G,
               ``c[2]`` = B).

        Returns:
            Six-character uppercase hex string without a leading ``#``
            (DrawingML ``val`` attribute format), e.g. ``"2563EB"``.
        """

    # ── 3. Dimensions ─────────────────────────────────────────────────────────
    WIDTH_EMU  = int(15.5 * 360000)           # 15.5 cm — fills the text column
    HEIGHT_EMU = _bq_estimate_height_emu(tag) # exact content-driven height

    # ── 4. Fixed corner radius ─────────────────────────────────────────────────
    # Target: 6 pt corner radius (absolute, independent of shape height).
    # adj = RADIUS_EMU × 200 000 / min(cx, cy)
    # Since cx (15.5 cm = 5 580 000 EMU) > cy always, min = cy = HEIGHT_EMU.
    # This gives a physically constant corner size across all blockquote heights.
    # Cap at 50 000 (DrawingML max = 50 % of the shorter dimension).
    RADIUS_EMU = int(6 * 12700)    # 76 200 EMU = 6 pt
    adj_val    = min(50000, int(RADIUS_EMU * 200000 // HEIGHT_EMU))

    # ── 5. Build <a:graphic> / <wps:wsp> ─────────────────────────────────────
    graphic     = _lxml_etree.Element(f"{{{_NS['a']}}}graphic")
    graphicData = _sub(
        graphic, "a", "graphicData",
        uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    )
    wsp = _sub(graphicData, "wps", "wsp")

    cNvSpPr = _sub(wsp, "wps", "cNvSpPr", txBx="1")
    _sub(cNvSpPr, "a", "spLocks", noChangeArrowheads="1")  # lock: prevent adding arrowheads to connectors

    spPr = _sub(wsp, "wps", "spPr")
    xfrm = _sub(spPr, "a", "xfrm")
    _sub(xfrm, "a", "off", x="0", y="0")
    _sub(xfrm, "a", "ext", cx=str(WIDTH_EMU), cy=str(HEIGHT_EMU))

    prstGeom = _sub(spPr, "a", "prstGeom", prst="roundRect")
    avLst    = _sub(prstGeom, "a", "avLst")
    _sub(avLst, "a", "gd", name="adj", fmla=f"val {adj_val}")  # fixed 6pt radius

    solidFill = _sub(spPr, "a", "solidFill")
    _sub(solidFill, "a", "srgbClr", val=_hex(C_BQ_BG))

    # Border: 1 pt = 12 700 EMU (1 pt × 12 700 EMU/pt) — absolute width, never scales with shape size.
    # cap="flat": flat line end-caps (vs round or square).
    # cmpd="sng": single-line stroke (vs double or thick-thin compound lines).
    # algn="ctr": the border stroke straddles the shape edge (vs inside/outside only).
    ln     = _sub(spPr, "a", "ln", w="12700", cap="flat", cmpd="sng", algn="ctr")
    lnFill = _sub(ln, "a", "solidFill")
    _sub(lnFill, "a", "srgbClr", val=_hex(C_BQ_BORDER))
    _sub(ln, "a", "prstDash", val="solid")

    # ── 6. Text box content ───────────────────────────────────────────────────
    txbx        = _sub(wsp, "wps", "txbx")
    txbxContent = _sub(txbx, "w", "txbxContent")

    for child_el in list(scratch_body):
        local = _lxml_etree.QName(child_el.tag).localname
        if local in ("p", "tbl"):
            txbxContent.append(copy.deepcopy(child_el))

    # Body properties: top-aligned, auto-height.
    # lIns/rIns = 91 440 EMU = 0.1 in ≈ 7.2 pt — horizontal padding inside the text box,
    #   ensuring text doesn't touch the rounded border.
    # tIns/bIns = 45 720 EMU = 0.05 in ≈ 3.6 pt — vertical padding; matches PAD_TOP/BOT_PT
    #   in _bq_estimate_height_emu so height estimate and actual rendering stay consistent.
    # spcFirstLastPara="0": do not suppress Word's extra spacing before/after the first/last paragraph.
    # anchor="t": text is top-aligned within the box (not vertically centred).
    # spAutoFit: Word expands the shape height to fit rendered content at layout time,
    #   so fill and border always enclose all text even if HEIGHT_EMU was underestimated.
    #   (normAutofit was removed because it locked the shape at HEIGHT_EMU, making the
    #    fill/border stop short of the text regardless of estimation accuracy.)
    bodyPr = _sub(wsp, "wps", "bodyPr",
                  rot="0", spcFirstLastPara="0",
                  vertOverflow="overflow", horzOverflow="overflow",
                  vert="horz", wrap="square",
                  lIns="91440", tIns="45720", rIns="91440", bIns="45720",
                  anchor="t", anchorCtr="0")
    _sub(bodyPr, "a", "spAutoFit")

    # ── 7. Inline drawing wrapper ─────────────────────────────────────────────
    # <wp:inline> places the drawing EXACTLY in the text flow (as a character).
    # The host paragraph height = HEIGHT_EMU — no separate float to drift.
    # A full-column-width inline shape is visually identical to "Top and Bottom"
    # wrapping since no text can appear beside it.
    # bq_id starts at 101: counter begins after 100 to avoid collision with drawing IDs
    # that Word assigns automatically when inserting shapes (typically starting from 1).
    _render_blockquote._bq_counter = getattr(_render_blockquote, "_bq_counter", 100) + 1
    bq_id = _render_blockquote._bq_counter

    drawing = _lxml_etree.Element(f"{{{_NS['w']}}}drawing")
    inline  = _lxml_etree.SubElement(
        drawing, f"{{{_NS['wp']}}}inline",
        distT="0", distB="0", distL="0", distR="0",  # zero gap between drawing and surrounding text
    )
    _sub(inline, "wp", "extent", cx=str(WIDTH_EMU), cy=str(HEIGHT_EMU))
    _sub(inline, "wp", "effectExtent", l="0", t="0", r="0", b="0")  # no shadow/glow extends beyond bounds
    _sub(inline, "wp", "docPr", id=str(bq_id), name=f"Blockquote{bq_id}")
    cNvGFPr = _sub(inline, "wp", "cNvGraphicFramePr")
    _sub(cNvGFPr, "a", "graphicFrameLocks", noChangeAspect="1")  # lock: prevent non-proportional resize
    inline.append(graphic)

    # ── 8. Insert into document ───────────────────────────────────────────────
    # The <w:drawing> element must live inside a <w:r> (run) per the OOXML spec.
    host_para = doc.add_paragraph()
    _no_space_before(host_para)
    _set_para_space_after(host_para, 12)   # 12 pt after the shape — same visual gap as <hr>
    run_el = OxmlElement("w:r")
    run_el.append(drawing)
    host_para._p.append(run_el)


def _render_hr(doc: Document) -> None:
    """Render a Markdown horizontal rule (``<hr>``) as a paragraph border.

    Adds an empty paragraph whose ``<w:pBdr><w:bottom>`` draws a 0.5 pt
    (4 eighths-of-a-point) hairline rule in ``C_HR`` colour (``#E2E8F0``).
    Space-after is set to 12 pt so the rule acts as a visual section
    separator with equal breathing room above and below.

    Args:
        doc: The ``Document`` to append the rule paragraph to.
    """
    para = doc.add_paragraph()
    _no_space_before(para)
    _set_para_space_after(para, 12)   # 12 pt after: visual weight of a section separator
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    hex_color = f"{C_HR[0]:02X}{C_HR[1]:02X}{C_HR[2]:02X}"
    bottom.set(qn("w:val"),   "single")
    bottom.set(qn("w:sz"),    "4")    # 4 eighths-of-a-pt = 0.5 pt thin hairline rule
    bottom.set(qn("w:space"), "1")    # 1 pt gap between paragraph baseline and the rule
    bottom.set(qn("w:color"), hex_color)
    pBdr.append(bottom)
    pPr.append(pBdr)


# ── Document setup ─────────────────────────────────────────────────────────────

def _setup_document() -> Document:
    """Create and configure a blank A4 ``Document`` with corporate defaults.

    Sets up an A4 page (21 × 29.7 cm) with 2.5 cm side margins and 2.2 cm
    top margin, then applies ``FONT_BODY`` / ``FONT_BODY_PT`` / ``C_BODY`` to
    the ``Normal`` style and calls ``_customize_heading_styles`` to configure
    Heading 1–6.

    The resulting document is used both as the main output document and as a
    temporary scratch document inside ``_render_blockquote``.

    Returns:
        A freshly configured ``docx.Document`` instance ready to receive
        rendered content.
    """
    doc = Document()

    # A4 page with matching margins
    section = doc.sections[0]
    section.page_width  = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin   = Cm(2.5)   # 2.5 cm left + right: standard A4 letter margin
    section.right_margin  = Cm(2.5)
    section.top_margin    = Cm(2.2)   # 2.2 cm top: slightly tighter to match generate_pdfs.py
    section.bottom_margin = Cm(2.5)

    # Default Normal style: clear theme-font references so Inter is always used.
    style = doc.styles["Normal"]
    _set_style_font(style, FONT_BODY)
    style.font.size      = Pt(FONT_BODY_PT)
    style.font.color.rgb = C_BODY

    # Heading 1–6: color scheme, borders, and Inter font.
    # This also enables Word's Navigation Pane and automatic Table of Contents.
    _customize_heading_styles(doc)

    return doc


# ── OMML (Word native equations) ─────────────────────────────────────────────
# LaTeX → MathML (latex2mathml) → OMML (Microsoft MML2OMML.XSL XSLT).
# OMML is inserted as raw OOXML so Word renders it as a proper equation.

_XSLT_PATH = Path(
    r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"
)
_MML_TRANSFORM = None   # lazy-loaded on first use


def _get_mml_transform():
    """Lazily load and cache the Microsoft MML2OMML XSLT transform.

    On first call checks whether the Office 16 XSLT file exists at
    ``_XSLT_PATH``, compiles it with ``lxml.etree.XSLT``, and stores the
    result in the module-level ``_MML_TRANSFORM`` cache.  Subsequent calls
    return the cached object without re-reading the disk.

    Returns:
        An ``lxml.etree.XSLT`` transform object if the file exists and
        compiles successfully, otherwise ``None``.
    """
    if _MML_TRANSFORM is None and _XSLT_PATH.exists():
        try:
            xslt_doc = _lxml_etree.parse(str(_XSLT_PATH))
            _MML_TRANSFORM = _lxml_etree.XSLT(xslt_doc)
        except Exception:
            pass
    return _MML_TRANSFORM


def _latex_to_omml(latex_src: str):
    """Convert a LaTeX expression to a Word OMML ``<m:oMath>`` element.

    Pipeline: LaTeX → MathML (via ``latex2mathml.converter.convert``)
    → OMML (via the Microsoft MML2OMML.XSL XSLT transform) → lxml element.

    Args:
        latex_src: Raw LaTeX source string, e.g. ``r"\\frac{a}{b}"``.

    Returns:
        The root ``lxml.etree._Element`` of the converted OMML tree (an
        ``<m:oMath>`` element) on success, or ``None`` if the conversion
        fails for any reason (missing XSLT, unknown LaTeX command, etc.).
        Callers should fall back to rendering the raw LaTeX source as italic
        text when ``None`` is returned.
    """
    try:
        import latex2mathml.converter
        mml_str  = latex2mathml.converter.convert(latex_src)
        transform = _get_mml_transform()
        if transform is None:
            return None
        mml_doc = _lxml_etree.fromstring(mml_str.encode())
        result  = transform(mml_doc)
        root    = result.getroot()
        if root is None or len(root) == 0:
            return None
        return root
    except Exception:
        return None


_MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def _insert_math_block(doc: Document, latex_src: str) -> None:
    """Insert a display (block) equation into the document.

    Adds a centred paragraph and attempts to insert a Word-native OMML
    ``<m:oMathPara>`` element produced by ``_latex_to_omml``.  If the OMML
    conversion fails (e.g. LaTeX syntax is unsupported or the Office XSLT is
    not installed) the paragraph falls back to a centred italic string of the
    form ``$$ latex_src $$`` in ``C_EM`` colour.

    Args:
        doc: The ``Document`` to append the equation paragraph to.
        latex_src: Raw LaTeX source string for the equation.
    """
    para = doc.add_paragraph()
    _no_space_before(para)
    _set_para_space_after(para, 10)
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    omml = _latex_to_omml(latex_src)
    if omml is not None:
        oMathPara = _lxml_etree.Element(f"{{{_MATH_NS}}}oMathPara")
        oMathPara.append(omml)
        para._p.append(oMathPara)
    else:
        run = para.add_run(f"$$ {latex_src} $$")
        run.italic = True
        _set_run_font(run, FONT_BODY)
        run.font.size = Pt(FONT_BODY_PT)
        run.font.color.rgb = C_EM


def _insert_math_inline(para, latex_src: str) -> None:
    """Append an inline equation run to an existing paragraph.

    Attempts to insert a Word-native OMML ``<m:oMath>`` element directly into
    the paragraph XML.  If the OMML conversion fails the equation is rendered
    as an italic run of the form ``$latex_src$`` in ``C_EM`` colour.

    Args:
        para: The ``docx.text.paragraph.Paragraph`` to append the equation to.
        latex_src: Raw LaTeX source string for the inline equation.
    """
    omml = _latex_to_omml(latex_src)
    if omml is not None:
        para._p.append(omml)
    else:
        run = para.add_run(f"${latex_src}$")
        run.italic = True
        _set_run_font(run, FONT_BODY)
        run.font.size = Pt(FONT_BODY_PT)
        run.font.color.rgb = C_EM


# ── Main conversion ────────────────────────────────────────────────────────────

# Math render rules: convert dollarmath tokens → simple HTML that BeautifulSoup
# can parse.  Without these, markdown-it silently drops all math content.
def _render_math_inline_word(self, tokens, idx, options, env) -> str:
    """markdown-it render rule: convert an inline math token to HTML.

    Wraps the LaTeX content in ``<span class="math-inline">…</span>`` so
    that ``_inline_nodes_to_runs`` can detect it and delegate to
    ``_insert_math_inline`` for Word-native OMML rendering.

    Args:
        self: The ``markdown_it.MarkdownIt`` renderer instance.
        tokens: The full token list.
        idx: Index of the current ``math_inline`` token.
        options: Renderer options dict passed by markdown-it.
        env: Environment object passed by markdown-it.

    Returns:
        HTML string ``'<span class="math-inline">…</span>'`` with HTML-
        escaped content.
    """
    content = html_lib.escape(str(tokens[idx].content).strip(), quote=True)
    return f'<span class="math-inline">{content}</span>'


def _render_math_block_word(self, tokens, idx, options, env) -> str:
    """markdown-it render rule: convert a block math token to HTML.

    Wraps the LaTeX content in ``<div class="math-block">…</div>`` so that
    ``_walk_block`` detects it and delegates to ``_insert_math_block`` for
    Word-native OMML rendering.

    Args:
        self: The ``markdown_it.MarkdownIt`` renderer instance.
        tokens: The full token list.
        idx: Index of the current ``math_block`` or ``math_block_label`` token.
        options: Renderer options dict passed by markdown-it.
        env: Environment object passed by markdown-it.

    Returns:
        HTML string ``'<div class="math-block">…</div>\\n'`` with HTML-
        escaped content.
    """
    content = html_lib.escape(str(tokens[idx].content).strip(), quote=True)
    return f'<div class="math-block">{content}</div>\n'


def _build_md_parser() -> markdown_it.MarkdownIt:
    """Build and configure the markdown-it parser for the Word pipeline.

    Creates a ``commonmark``-preset ``MarkdownIt`` instance, enables the
    ``table`` core rule, loads the ``dollarmath`` plugin (single and double
    dollar signs, ``$…$`` and ``$$…$$``), and registers the Word-specific
    render rules ``_render_math_inline_word`` and ``_render_math_block_word``
    that emit ``math-inline`` spans and ``math-block`` divs for subsequent
    BeautifulSoup/OOXML processing.

    Returns:
        A fully configured ``markdown_it.MarkdownIt`` instance ready for
        ``parser.render(md_text)``.
    """
    md = markdown_it.MarkdownIt(
        "commonmark",
        {"html": True, "typographer": False, "breaks": False},
    )
    md.enable("table")
    dollarmath_plugin(md, allow_labels=True, allow_space=True,
                      allow_digits=True, double_inline=True)
    md.add_render_rule("math_inline",        _render_math_inline_word)
    md.add_render_rule("math_inline_double", _render_math_inline_word)
    md.add_render_rule("math_block",         _render_math_block_word)
    md.add_render_rule("math_block_label",   _render_math_block_word)
    return md


def _preprocess(text: str) -> str:
    """Apply Markdown pre-processing before passing to the markdown-it parser.

    Performs two transformations that require plain-text manipulation rather
    than parser hooks:

    1. **Strikethrough**: converts ``~~text~~`` to ``<del>text</del>`` using
       a regex so markdown-it's default CommonMark preset (which omits GFM
       strikethrough) does not silently drop it.
    2. **Blockquote continuation lists**: re-indents list items that
       immediately follow a blockquote line (without a blank line) and are
       indented ≥ 4 spaces.  These would otherwise be parsed as literal code
       blocks; prefixing them with ``"> "`` keeps them inside the blockquote
       as proper list items.  Identical logic to ``generate_pdfs.py``.

    Args:
        text: Raw Markdown source string.

    Returns:
        Pre-processed Markdown string ready for ``_build_md_parser().render()``.
    """
    # Strikethrough ~~text~~ → <del>text</del>
    text = re.sub(r"~~(.+?)~~",
                  lambda m: f"<del>{m.group(1)}</del>",
                  text, flags=re.DOTALL)
    # Blockquote continuation lists (same logic as generate_pdfs.py)
    lines = text.split("\n")
    result: list[str] = []
    after_bq = False
    for line in lines:
        if line.startswith(">"):
            after_bq = True
            result.append(line)
        elif after_bq and line.strip():
            stripped = line.strip()
            leading  = len(line) - len(line.lstrip())
            is_list  = bool(re.match(r"^\d+\.\s+", stripped)) or \
                        bool(re.match(r"^[-*+]\s+", stripped))
            if leading >= 4 and is_list:
                result.append("> " + stripped)
            else:
                after_bq = False
                result.append(line)
        else:
            if line.strip():
                after_bq = False
            result.append(line)
    return "\n".join(result)


def _walk_block(doc: Document, node: Tag) -> None:
    """Dispatch a top-level BeautifulSoup block element to the correct renderer.

    Acts as the main routing switch for block-level HTML produced by the
    markdown-it parser.  Handles:

    * ``NavigableString``: plain bare text rendered as a body paragraph.
    * Naked anchor (``<a id="...">``) — detected by ``_is_naked_anchor``:
      saves the id in ``_pending_anchor`` so the next heading claims it.
    * ``h1``–``h6``: ``_render_heading``.
    * ``p``: ``_render_paragraph``.
    * ``div`` (``class="math-block"``): ``_insert_math_block``.
    * ``pre``: ``_render_code_block``.
    * ``table``: ``_render_table``.
    * ``ul`` / ``ol``: ``_render_list``.
    * ``blockquote``: ``_render_blockquote``.
    * ``hr``: ``_render_hr``.
    * Anything else: falls back to plain inner text.

    Args:
        doc: The ``Document`` to append rendered elements to.
        node: A BeautifulSoup ``Tag`` or ``NavigableString`` from the
            top-level body iteration.
    """
    global _pending_anchor

    if isinstance(node, NavigableString):
        text = str(node).strip()
        if text:
            para = doc.add_paragraph(text)
            _set_para_space_after(para, 7)
        return

    tag = node.name
    if tag is None:
        return

    # Naked anchor (<a id="p1"></a> or <p><a id="p1"></a></p>): stash the id so
    # the immediately following heading or paragraph adopts it as a bookmark.
    anchor_id = _is_naked_anchor(node)
    if anchor_id is not None:
        _pending_anchor = anchor_id
        return  # do not render an empty paragraph

    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        _render_heading(doc, node, int(tag[1]))

    elif tag == "p":
        # math blocks (div.math-block) inside a <p> that is actually a <div>
        # are rendered as plain text
        _render_paragraph(doc, node)

    elif tag in ("div",):
        # math-block divs: convert to Word-native display equation
        formula = node.get_text(strip=True)
        if formula:
            _insert_math_block(doc, formula)

    elif tag == "pre":
        _render_code_block(doc, node)

    elif tag == "table":
        _render_table(doc, node)

    elif tag in ("ul", "ol"):
        _render_list(doc, node)

    elif tag == "blockquote":
        _render_blockquote(doc, node)

    elif tag == "hr":
        _render_hr(doc)

    else:
        # Fallback: render inner text as plain body paragraph
        text = node.get_text(" ", strip=True)
        if text:
            para = doc.add_paragraph(text)
            _set_para_space_after(para, 7)


def markdown_to_docx(md_text: str) -> Document:
    """Convert a Markdown string to a styled ``python-docx`` ``Document``.

    Full pipeline:

    1. Reset per-document global state (``_slug_counts``, ``_bookmark_id``,
       ``_pending_anchor``) so each call is independent.
    2. Pre-process the Markdown source via ``_preprocess`` (strikethrough +
       blockquote continuation).
    3. Parse to HTML with ``_build_md_parser().render``.
    4. Parse the HTML with ``BeautifulSoup`` (lxml backend).
    5. Create a styled document via ``_setup_document``.
    6. Iterate top-level body children and dispatch each to
       ``_walk_block``.

    Args:
        md_text: UTF-8 Markdown source string.

    Returns:
        A fully populated ``docx.Document`` ready to be saved with
        ``document.save(path)``.
    """
    global _slug_counts, _bookmark_id, _pending_anchor
    # Reset per-document state so each call starts with a clean slug registry
    # and bookmark ID sequence (IDs must be unique *within* a document, not across).
    _slug_counts   = {}
    _bookmark_id   = 0
    _pending_anchor = None

    text    = _preprocess(md_text)
    parser  = _build_md_parser()
    html    = parser.render(text)
    soup    = BeautifulSoup(html, "lxml")
    doc     = _setup_document()

    body = soup.body or soup
    for child in body.children:
        _walk_block(doc, child)

    return doc


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point: convert all configured Markdown files to ``.docx``.

    Iterates over the ``DOCS`` list (defined at module level) where each
    entry is a ``dict`` with ``'input'`` (source ``Path``) and ``'output'``
    (destination ``Path``) keys.  For each spec it reads the Markdown file
    with UTF-8-BOM encoding, calls ``markdown_to_docx``, and saves the
    resulting document.

    Progress is printed to stdout and a final confirmation line is emitted
    after all files have been processed.
    """
    for doc_spec in DOCS:
        print(f"\n→ Processing: {doc_spec['input'].name}")
        md_text = doc_spec["input"].read_text(encoding="utf-8-sig")
        document = markdown_to_docx(md_text)
        document.save(str(doc_spec["output"]))
        print(f"  ✓ DOCX saved →  {doc_spec['output']}")
    print("\n✅ Done.")


if __name__ == "__main__":
    main()
