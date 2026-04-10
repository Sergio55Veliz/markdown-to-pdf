"""
Word generation pipeline.

Markdown → HTML (via markdown-it) → BeautifulSoup → python-docx Document.
"""

from __future__ import annotations

import html as html_lib
import re
from pathlib import Path

import markdown_it
from mdit_py_plugins.dollarmath import dollarmath_plugin
from bs4 import BeautifulSoup
from docx import Document

from markdown_to_pdf.preprocessing import preprocess_markdown
from markdown_to_pdf.word.document import setup_document
from markdown_to_pdf.word.ooxml import reset_bookmark_counter
from markdown_to_pdf.word.rendering import (
    walk_block,
    reset_rendering_state,
    reset_bq_counter,
)


# ── Math render rules (Word-specific) ────────────────────────────────────────

def _render_math_inline_word(self, tokens, idx, options, env) -> str:
    content = html_lib.escape(str(tokens[idx].content).strip(), quote=True)
    return f'<span class="math-inline">{content}</span>'


def _render_math_block_word(self, tokens, idx, options, env) -> str:
    content = html_lib.escape(str(tokens[idx].content).strip(), quote=True)
    return f'<div class="math-block">{content}</div>\n'


def _build_md_parser() -> markdown_it.MarkdownIt:
    """Build the markdown-it parser configured for the Word pipeline."""
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


# ── Main conversion ──────────────────────────────────────────────────────────

def markdown_to_docx(md_text: str) -> Document:
    """Convert a Markdown string to a styled ``Document``."""
    reset_rendering_state()
    reset_bookmark_counter()
    reset_bq_counter()

    text    = preprocess_markdown(md_text)
    parser  = _build_md_parser()
    html    = parser.render(text)
    soup    = BeautifulSoup(html, "lxml")
    doc     = setup_document()

    body = soup.body or soup
    for child in body.children:
        walk_block(doc, child)

    return doc


def generate_docx_from_file(
    md_path: Path,
    output_path: Path | None = None,
) -> Path:
    """High-level: read a Markdown file and produce a ``.docx``.

    Returns the path to the generated file.
    """
    if output_path is None:
        output_path = md_path.with_suffix(".docx")

    print(f"\n→ Processing: {md_path.name}")
    md_text = md_path.read_text(encoding="utf-8-sig")
    document = markdown_to_docx(md_text)
    document.save(str(output_path))
    print(f"  ✓ DOCX saved →  {output_path}")
    return output_path
