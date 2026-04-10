"""
Word document setup and heading style configuration.
"""

from __future__ import annotations

from docx import Document
from docx.shared import Pt, Cm

from markdown_to_pdf.constants import (
    rgb_docx,
    WordFonts,
    FONT_BODY_PT,
    HEADING_SIZE,
    HEADING_BOLD,
    HEADING_COLORS,
    HEADING_SPACE_BEFORE,
    HEADING_SPACE_AFTER,
    COLOR_BODY,
    COLOR_H1_BORDER,
    COLOR_H2_BORDER,
)
from markdown_to_pdf.word.ooxml import set_style_font, set_style_bottom_border


def customize_heading_styles(doc: Document) -> None:
    """Apply corporate typography to built-in Heading 1–6 styles."""
    for level in range(1, 7):
        try:
            style = doc.styles[f"Heading {level}"]
        except KeyError:
            continue
        set_style_font(style, WordFonts.HEADING)
        style.font.size    = Pt(HEADING_SIZE[level])
        style.font.bold    = HEADING_BOLD[level]
        style.font.italic  = False
        style.font.color.rgb = rgb_docx(HEADING_COLORS[level])
        pf = style.paragraph_format
        pf.space_before   = Pt(HEADING_SPACE_BEFORE[level])
        pf.space_after    = Pt(HEADING_SPACE_AFTER[level])
        pf.keep_with_next = True
        if level == 1:
            set_style_bottom_border(style, COLOR_H1_BORDER, "18")
        elif level == 2:
            set_style_bottom_border(style, COLOR_H2_BORDER, "6")


def setup_document() -> Document:
    """Create and configure a blank A4 Document with corporate defaults."""
    doc = Document()
    section = doc.sections[0]
    section.page_width  = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)
    section.top_margin    = Cm(2.2)
    section.bottom_margin = Cm(2.5)

    style = doc.styles["Normal"]
    set_style_font(style, WordFonts.BODY)
    style.font.size      = Pt(FONT_BODY_PT)
    style.font.color.rgb = rgb_docx(COLOR_BODY)

    customize_heading_styles(doc)
    return doc
