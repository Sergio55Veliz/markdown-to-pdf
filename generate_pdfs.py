#!/usr/bin/env python3
"""
PDF Generator for Feature Store documentation.

Converts two Markdown files to A4 PDFs with:
  - Professional corporate styling (Banco Bolivariano)
  - KaTeX-rendered math equations (consistent font size)
  - Tables that stay on one page (page-break-inside: avoid)
  - "Matriz de Cobertura" table: allowed to split across pages, forced to start on page 2
  - Bullets / numerals rendered correctly (including inside blockquotes)
  - Fenced code blocks with dark-theme styling

Usage:
    conda run -n pdf_gen python scripts/pdf_generator/generate_pdfs.py
"""

import asyncio
import base64
import html as html_lib
import re
from pathlib import Path

import markdown_it
from mdit_py_plugins.dollarmath import dollarmath_plugin
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

try:
    import fitz  # PyMuPDF — for PDF outline/bookmarks
    _FITZ_AVAILABLE = True
except ImportError:
    _FITZ_AVAILABLE = False

try:
    from pygments import highlight as _pygments_highlight
    from pygments.lexers import get_lexer_by_name as _get_lexer_by_name
    from pygments.formatters import HtmlFormatter as _HtmlFormatter
    _PYGMENTS_AVAILABLE = True
except ImportError:
    _PYGMENTS_AVAILABLE = False

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
OUTPUT_DIR = SCRIPT_DIR

DOCS = [
    {
        "input": REPO_ROOT / "propuesta_nuevas_features.md",
        "output": OUTPUT_DIR / "propuesta_nuevas_features.pdf",
        "title": "Propuesta de Nuevas Features — Feature Store",
        "doc_id": "propuesta",
    },
    {
        "input": REPO_ROOT / "dashboard_riesgo_juridico.md",
        "output": OUTPUT_DIR / "dashboard_riesgo_juridico.pdf",
        "title": "Dashboard de Riesgo — Clientes Jurídicos",
        "doc_id": "dashboard",
    },
]


# ── Pre-processing ─────────────────────────────────────────────────────────────

def fix_blockquote_continuation_lists(text: str) -> str:
    """Re-indent list items following a blockquote into the blockquote.

    Some blockquotes end with a colon and their list items are written on
    the following lines with 8-space indentation but **without** a ``>``
    prefix, for example::

        > …para evaluar la viabilidad de su uso:
                1. ¿Esta tabla ya existe en algún servidor ON-PREMISE?
                2. …

    CommonMark does **not** consider those continuation lines part of the
    blockquote, so they are parsed as an indented code-block.  This
    function rewrites them as proper blockquote list items::

        > …para evaluar la viabilidad de su uso:
        > 1. ¿Esta tabla ya existe en algún servidor ON-PREMISE?
        > 2. …

    Only lines that are indented ≥ 4 spaces **and** match a list-item
    pattern (``N. …`` or ``- / * / + …``) are re-prefixed.  Any other
    non-empty line after a blockquote resets the continuation state.

    Args:
        text: Raw Markdown source string.

    Returns:
        Modified Markdown string with blockquote continuations fixed.
    """
    lines = text.split("\n")
    result: list[str] = []
    after_blockquote = False

    for line in lines:
        if line.startswith(">"):
            after_blockquote = True
            result.append(line)
        elif after_blockquote and line.strip():
            stripped = line.strip()
            leading = len(line) - len(line.lstrip())
            is_list = bool(re.match(r"^\d+\.\s+", stripped)) or bool(
                re.match(r"^[-*+]\s+", stripped)
            )
            if leading >= 4 and is_list:
                result.append("> " + stripped)
            else:
                after_blockquote = False
                result.append(line)
        else:
            if line.strip():
                after_blockquote = False
            result.append(line)

    return "\n".join(result)


def preprocess_strikethrough(text: str) -> str:
    """Convert ``~~text~~`` Markdown strikethrough to ``<del>text</del>`` HTML.

    CommonMark does not define the ``~~…~~`` strikethrough syntax (it is a
    GFM extension).  Since ``markdown-it-py`` is used with ``html=True``, raw
    HTML passes through the parser unchanged, so this pre-processing step
    converts the notation before the parser sees it.

    The regex uses ``re.DOTALL`` so multi-line strikethrough spans (uncommon
    but syntactically valid) are handled correctly.

    Args:
        text: Raw Markdown source string.

    Returns:
        String with all ``~~…~~`` patterns replaced by ``<del>…</del>``.
    """
    return re.sub(r"~~(.+?)~~", lambda m: f"<del>{m.group(1)}</del>", text, flags=re.DOTALL)


# ── Markdown → HTML ────────────────────────────────────────────────────────────

# ── Math render rules ─────────────────────────────────────────────────────────
# These override the default dollarmath renderers.  The function signature
# must include `self` (the RendererHTML instance) as the first argument,
# matching the markdown-it-py v4 add_render_rule API.

def _render_math_inline(self, tokens, idx, options, env) -> str:  # type: ignore[override]
    """markdown-it render rule: convert a ``$…$`` inline math token to HTML.

    Produces a ``<span class="math-inline">`` wrapper containing a
    ``<span class="katex-ph katex-ph--inline" data-formula="…">`` placeholder.
    The client-side JavaScript in the generated HTML page calls
    ``katex.render`` on each placeholder at load time.

    Args:
        self: The ``markdown_it`` ``RendererHTML`` instance.
        tokens: Full token list from the parser.
        idx: Index of the current ``math_inline`` token.
        options: Renderer options dict.
        env: Renderer environment object.

    Returns:
        HTML string for the rendered inline math placeholder.
    """
    content = str(tokens[idx].content).strip()
    escaped = html_lib.escape(content, quote=True)
    return (
        f'<span class="math-inline">'
        f'<span class="katex-ph katex-ph--inline" data-formula="{escaped}"></span>'
        f"</span>"
    )


def _render_math_inline_double(self, tokens, idx, options, env) -> str:  # type: ignore[override]
    """markdown-it render rule: convert a ``$$…$$`` inline-context block to HTML.

    The ``double_inline`` flag in ``dollarmath_plugin`` allows ``$$…$$``
    within inline context.  This rule produces a block-style KaTeX display
    placeholder (``katex-ph--display``) so it renders as a centred display
    equation even when the source is inline.

    Args:
        self: The ``markdown_it`` ``RendererHTML`` instance.
        tokens: Full token list from the parser.
        idx: Index of the current ``math_inline_double`` token.
        options: Renderer options dict.
        env: Renderer environment object.

    Returns:
        HTML ``<div class="math-block">…</div>\\n`` string.
    """
    content = str(tokens[idx].content).strip()
    escaped = html_lib.escape(content, quote=True)
    return (
        f'<div class="math-block">'
        f'<span class="katex-ph katex-ph--display" data-formula="{escaped}"></span>'
        f"</div>\n"
    )


def _render_math_block(self, tokens, idx, options, env) -> str:  # type: ignore[override]
    """markdown-it render rule: convert a ``$$…$$`` block math token to HTML.

    Produces a ``<div class="math-block">`` wrapper with a
    ``katex-ph--display`` placeholder.  The same HTML structure is shared
    with ``_render_math_inline_double`` and the alias
    ``_render_math_block_label``.

    Args:
        self: The ``markdown_it`` ``RendererHTML`` instance.
        tokens: Full token list from the parser.
        idx: Index of the current ``math_block`` or ``math_block_label``
            token.
        options: Renderer options dict.
        env: Renderer environment object.

    Returns:
        HTML ``<div class="math-block">…</div>\\n`` string.
    """
    content = str(tokens[idx].content).strip()
    escaped = html_lib.escape(content, quote=True)
    return (
        f'<div class="math-block">'
        f'<span class="katex-ph katex-ph--display" data-formula="{escaped}"></span>'
        f"</div>\n"
    )


_render_math_block_label = _render_math_block  # labelled $$...$$ is treated the same


def _build_md_parser() -> markdown_it.MarkdownIt:
    """Build and configure the markdown-it parser for the PDF pipeline.

    Creates a ``commonmark``-preset ``MarkdownIt`` instance, enables the
    ``table`` rule, loads the ``dollarmath`` plugin, and registers the four
    PDF-specific render rules that emit KaTeX placeholder HTML instead of
    raw LaTeX.

    Returns:
        A fully configured ``markdown_it.MarkdownIt`` instance ready for
        ``md.render(text)``.
    """
    md = markdown_it.MarkdownIt(
        "commonmark",
        {"html": True, "typographer": False, "breaks": False},
    )
    md.enable("table")
    # dollarmath_plugin registers the tokenization rules; we override rendering
    dollarmath_plugin(
        md,
        allow_labels=True,
        allow_space=True,
        allow_digits=True,
        double_inline=True,
    )
    md.add_render_rule("math_inline", _render_math_inline)
    md.add_render_rule("math_inline_double", _render_math_inline_double)
    md.add_render_rule("math_block", _render_math_block)
    md.add_render_rule("math_block_label", _render_math_block_label)
    return md


_HIGHLIGHT_LANGS = {"python", "sql"}


def _apply_syntax_highlighting(html_str: str) -> str:
    """Apply Pygments syntax highlighting to fenced code blocks in HTML.

    Operates on the final HTML **string** (not the BeautifulSoup tree) so
    that whitespace-only indentation spans produced by Pygments are never
    touched by an HTML parser and are preserved exactly.

    Only blocks whose ``class`` language attribute appears in
    ``_HIGHLIGHT_LANGS`` (``python``, ``sql``) are processed; all other
    code blocks are returned unchanged to avoid misidentifying unlabelled
    or unsupported blocks.

    If Pygments is not installed (``_PYGMENTS_AVAILABLE`` is ``False``) the
    function returns the input string unmodified.

    Args:
        html_str: The complete HTML body string to process.

    Returns:
        HTML string with matching code blocks replaced by Pygments-
        highlighted equivalents using the ``monokai`` style.
    """
    if not _PYGMENTS_AVAILABLE:
        return html_str

    formatter = _HtmlFormatter(noclasses=True, style="monokai", nowrap=True)

    def replacer(m: re.Match) -> str:
        lang = m.group(1).lower()
        if lang not in _HIGHLIGHT_LANGS:
            return m.group(0)
        # decode_contents() only escapes &, <, > — unescape to recover original source
        raw_code = html_lib.unescape(m.group(2))
        try:
            lexer = _get_lexer_by_name(lang, stripall=False)
            highlighted = _pygments_highlight(raw_code, lexer, formatter)
            return f'<code class="language-{lang}">{highlighted}</code>'
        except Exception:
            return m.group(0)  # fall back to plain unstyled code

    return re.sub(
        r'<code class="language-([^"]+)">(.*?)</code>',
        replacer,
        html_str,
        flags=re.DOTALL,
    )


def markdown_to_html(md_text: str, doc_id: str = "") -> str:
    """Convert Markdown source to a styled HTML body fragment.

    Full pipeline:

    1. ``fix_blockquote_continuation_lists`` — re-indent blockquote-adjacent
       list items.
    2. ``preprocess_strikethrough`` — convert ``~~…~~`` to ``<del>``.
    3. ``_build_md_parser().render`` — Markdown → HTML.
    4. BeautifulSoup post-processing:

       * Tag all tables with ``no-break`` (prevent page-splitting) unless they
         already carry ``allow-break``.
       * For ``doc_id="propuesta"``: locate the *Matriz de Cobertura* ``<h2>``
         and mark it ``page-break-before``; the immediately following table
         receives ``allow-break`` so it may span multiple pages.
       * Auto-size narrow first columns by injecting a ``<colgroup>`` with a
         percentage width.
    5. ``_apply_syntax_highlighting`` — Pygments on ``python``/``sql`` blocks.

    Args:
        md_text: Raw Markdown source string (UTF-8, BOM already stripped).
        doc_id: Optional document identifier used for document-specific
            post-processing rules (``"propuesta"`` enables the Matriz de
            Cobertura page-break logic).

    Returns:
        Inner HTML body fragment (no ``<html>``/``<body>`` wrapper) suitable
        for embedding in ``build_html_page``.
    """

    text = fix_blockquote_continuation_lists(md_text)
    text = preprocess_strikethrough(text)

    md = _build_md_parser()
    html_body = md.render(text)

    soup = BeautifulSoup(html_body, "lxml")

    # ── All tables: no page-break inside (unless overridden below) ─────────────
    for tbl in soup.find_all("table"):
        cls = list(tbl.get("class", []))
        if "allow-break" not in cls:
            tbl["class"] = cls + ["no-break"]

    # ── propuesta_nuevas_features: special handling for Matriz de Cobertura ─────
    if doc_id == "propuesta":
        for h2 in soup.find_all("h2"):
            if "Matriz de Cobertura" in h2.get_text():
                h2["class"] = list(h2.get("class", [])) + ["page-break-before"]
                # The table immediately following this heading is allowed to break
                sibling = h2.find_next_sibling()
                while sibling:
                    if sibling.name == "table":
                        cls = [c for c in sibling.get("class", []) if c != "no-break"]
                        sibling["class"] = cls + ["allow-break"]
                        break
                    if sibling.name in ("h2", "h3"):
                        break
                    sibling = sibling.find_next_sibling()
                break

    # ── First-column width: auto-size narrow columns ───────────────────────────
    # With table-layout: fixed every column would get equal width. When the
    # first column only contains short values (e.g. a row number "#"), inject a
    # <colgroup> so it gets a width proportional to its content. The remaining
    # columns share the rest equally because no explicit width is set on them.
    for tbl in soup.find_all("table"):
        first_col_texts: list[str] = []
        for row in tbl.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if cells:
                first_col_texts.append(cells[0].get_text(strip=True))
        if not first_col_texts:
            continue
        num_cols = max(
            len(row.find_all(["th", "td"])) for row in tbl.find_all("tr")
        )
        if num_cols < 2:
            continue
        max_len = max(len(t) for t in first_col_texts)
        if max_len <= 2:
            pct = "8%"
        elif max_len <= 4:
            pct = "12%"
        elif max_len <= 8:
            pct = "18%"
        elif max_len <= 12:
            pct = "22%"
        else:
            continue  # first column content is long — no override needed
        colgroup = soup.new_tag("colgroup")
        colgroup.append(soup.new_tag("col", style=f"width:{pct}"))
        tbl.insert(0, colgroup)

    # Return only inner body contents (avoid nested <html><body> wrapper from lxml)
    # Syntax highlighting is applied as a string-based post-process step to avoid
    # whitespace-only spans being stripped by BeautifulSoup's html.parser.
    return _apply_syntax_highlighting(soup.body.decode_contents())


# ── CSS ────────────────────────────────────────────────────────────────────────

CSS = r"""
/* ── Prevent Chromium auto-scale: clip any overflow so the page width stays
   at the viewport width and Chromium does not shrink-to-fit the content ─── */
html {
    overflow-x: hidden;
}

/* ── Page ───────────────────────────────────────────────────────────────────── */
@page {
    size: A4;
    margin: 2.2cm 2.5cm 2.5cm 2.5cm;
    @bottom-left {
        content: string(doc-title);
        font-size: 9pt;
        color: #9ca3af;
        font-family: 'Inter', sans-serif;
    }
    @bottom-right {
        content: counter(page) " / " counter(pages);
        font-size: 9pt;
        color: #9ca3af;
        font-family: 'Inter', sans-serif;
    }
}

/* ── Body ───────────────────────────────────────────────────────────────────── */
body {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 10.5pt;
    line-height: 1.65;
    color: #1e293b;
    background: #ffffff;
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
}
p  { margin: 0 0 8pt; }
em { color: #475569; }
a  { color: #2563eb; text-decoration: none; }

/* ── Headings ───────────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    page-break-after: avoid;
    break-after: avoid;
    font-weight: 700;
    line-height: 1.3;
}
h1 {
    font-size: 22pt;
    color: #0f172a;
    border-bottom: 3px solid #1e40af;
    padding-bottom: 10pt;
    margin: 0 0 6pt;
    string-set: doc-title content();
}
h2 {
    font-size: 14pt;
    font-weight: 600;
    color: #1e40af;
    border-bottom: 1.5px solid #bfdbfe;
    padding-bottom: 4pt;
    margin: 24pt 0 8pt;
}
h3 {
    font-size: 12.5pt;
    font-weight: 600;
    color: #1d4ed8;
    margin: 18pt 0 6pt;
}
h4 {
    font-size: 12pt;
    font-weight: 600;
    color: #1d4ed8;
    margin: 14pt 0 5pt;
}
h5 {
    font-size: 11.5pt;
    font-weight: 600;
    color: #1d4ed8;
    margin: 10pt 0 4pt;
}
h6 {
    font-size: 11pt;
    font-weight: 700;
    color: #475569;
    margin: 10pt 0 4pt;
}

/* ── Page break utilities ───────────────────────────────────────────────────── */
.page-break-before {
    page-break-before: always !important;
    break-before: page !important;
    margin-top: 0 !important;
}

/* ── Tables ─────────────────────────────────────────────────────────────────── */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 9.5pt;
    table-layout: fixed;
}
.no-break {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
}
.allow-break {
    page-break-inside: auto !important;
    break-inside: auto !important;
}
thead tr {
    background-color: #1e3a8a;
    color: #ffffff;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
th {
    padding: 7pt 10pt;
    text-align: left;
    font-weight: 600;
    border: 1px solid #1e3a8a;
    font-size: 9.5pt;
    overflow-wrap: anywhere;
    word-break: break-word;
}
td {
    padding: 6pt 10pt;
    border-bottom: 1px solid #cbd5e1;
    vertical-align: top;
    line-height: 1.5;
    word-wrap: break-word;
    overflow-wrap: anywhere;
    color: #1e293b;
}
td strong { color: #0f172a; }
td a      { color: #2563eb; }
tr:nth-child(even) td {
    background-color: #f1f5f9;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}

/* ── Blockquotes ────────────────────────────────────────────────────────────── */
blockquote {
    border-left: 4px solid #2563eb;
    margin: 10pt 0;
    padding: 8pt 14pt;
    background-color: #eff6ff;
    color: #334155;
    border-radius: 0 6px 6px 0;
    font-size: 10pt;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
blockquote strong     { color: #0f172a; }
blockquote p          { margin-bottom: 4pt; }
blockquote p:last-child { margin-bottom: 0; }
blockquote ul,
blockquote ol         { list-style-position: inside; padding-left: 10pt; margin-bottom: 4pt; }
blockquote li         { margin-bottom: 2pt; }
blockquote > blockquote {
    background-color: #e0ecff;
    border-left-color: #1d4ed8;
}

/* ── Lists ──────────────────────────────────────────────────────────────────── */
ul { list-style-type: disc;    list-style-position: outside; padding-left: 20pt; margin-bottom: 8pt; }
ol { list-style-type: decimal; list-style-position: outside; padding-left: 20pt; margin-bottom: 8pt; }
ul ul  { list-style-type: circle; }
ul ul ul { list-style-type: square; }
ol ol  { list-style-type: lower-alpha; }
li { margin-bottom: 3pt; }

/* ── Code ───────────────────────────────────────────────────────────────────── */
pre {
    background-color: #1e2030;
    color: #c8d3f5;
    padding: 12pt;
    margin: 10pt 0;
    border-radius: 8px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
    overflow-x: hidden;
    tab-size: 4;
    page-break-inside: avoid;
    break-inside: avoid;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
pre code {
    background: none;
    border: none;
    color: inherit;
    padding: 0;
    font-size: 9pt;
    word-break: normal;
}
code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
}
p code, li code, td code, blockquote code,
h1 code, h2 code, h3 code, h4 code, h5 code, h6 code {
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 9pt;
}

/* ── Horizontal rule ────────────────────────────────────────────────────────── */
hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 18pt 0;
}

/* ── Math ───────────────────────────────────────────────────────────────────── */
.math-block {
    margin: 16px auto;
    text-align: center;
    overflow-x: auto;
    overflow-y: hidden;
}
.math-inline {
    display: inline;
}
/* Consistent KaTeX size — matches body text */
.katex              { font-size: 1em !important; }
.katex-display      { margin: 0.4em 0 !important; overflow-x: auto; }

/* ── Deleted / strikethrough ────────────────────────────────────────────────── */
del {
    text-decoration: line-through;
    color: #6b7280;
}
"""

# ── CDN resources ────────────────────────────────────────────────────────────
KATEX_CSS = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css"
KATEX_JS  = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"


def _build_inter_font_face() -> str:
    """Build ``@font-face`` CSS blocks embedding Inter woff2 files as base64.

    Reads each Inter woff2 font variant from ``scripts/pdf_generator/fonts/``,
    base64-encodes it, and returns CSS ``@font-face`` declarations that embed
    the font as a ``data:font/woff2`` URI.  This removes the need for any
    network access during PDF rendering, which is important for headless
    Chromium / Playwright environments without internet access.

    Supported variants (weight, style):

    * 300 normal (Light)
    * 400 normal (Regular)
    * 400 italic (Italic)
    * 500 normal (Medium)
    * 600 normal (SemiBold)
    * 700 normal (Bold)

    Missing font files are silently skipped; the browser will fall back to
    ``Segoe UI`` or ``sans-serif``.

    Returns:
        A multi-line CSS string containing one ``@font-face`` block per
        available font file, or an empty string if the ``fonts/`` directory
        does not exist.
    """
    fonts_dir = SCRIPT_DIR / "fonts"
    specs = [
        ("inter-latin-300-normal.woff2", 300, "normal"),
        ("inter-latin-400-normal.woff2", 400, "normal"),
        ("inter-latin-400-italic.woff2", 400, "italic"),
        ("inter-latin-500-normal.woff2", 500, "normal"),
        ("inter-latin-600-normal.woff2", 600, "normal"),
        ("inter-latin-700-normal.woff2", 700, "normal"),
    ]
    blocks: list[str] = []
    for filename, weight, style in specs:
        path = fonts_dir / filename
        if not path.exists():
            continue
        data = base64.b64encode(path.read_bytes()).decode()
        blocks.append(
            f"@font-face {{\n"
            f"  font-family: 'Inter';\n"
            f"  font-style: {style};\n"
            f"  font-weight: {weight};\n"
            f"  src: url('data:font/woff2;base64,{data}') format('woff2');\n"
            f"}}"
        )
    return "\n".join(blocks)

# ── Inline JS ─────────────────────────────────────────────────────────────────
JS = r"""
(function () {
    'use strict';
    function renderAll() {
        document.querySelectorAll('.katex-ph--display').forEach(function (el) {
            var formula = el.getAttribute('data-formula');
            if (!formula) return;
            try {
                katex.render(formula, el.parentElement, {
                    throwOnError: false,
                    displayMode: true,
                    output: 'html',
                    trust: true
                });
            } catch (e) {
                el.parentElement.textContent = formula;
            }
        });
        document.querySelectorAll('.katex-ph--inline').forEach(function (el) {
            var formula = el.getAttribute('data-formula');
            if (!formula) return;
            try {
                katex.render(formula, el.parentElement, {
                    throwOnError: false,
                    displayMode: false,
                    output: 'html',
                    trust: true
                });
            } catch (e) {
                el.parentElement.textContent = formula;
            }
        });
    }
    if (typeof katex !== 'undefined') {
        renderAll();
    } else {
        document.querySelector('script[src*="katex"]').addEventListener('load', renderAll);
    }
})();
"""


def build_html_page(content_html: str, title: str) -> str:
    """Assemble a complete HTML document from a body fragment.

    Combines the Inter font-face CSS, the project stylesheet (``CSS``), KaTeX
    CDN links, the content fragment, and the inline KaTeX rendering script
    (``JS``) into a single self-contained HTML string ready to be loaded in a
    headless browser.

    Args:
        content_html: Inner HTML body fragment produced by ``markdown_to_html``.
        title: Document title inserted into ``<title>`` (HTML-escaped) and used
            by the KaTeX ``string-set: doc-title`` CSS running header.

    Returns:
        Complete UTF-8 HTML string starting with ``<!DOCTYPE html>``.
    """
    inter_css = _build_inter_font_face()
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>{html_lib.escape(title)}</title>
  <link rel="stylesheet" href="{KATEX_CSS}">
  <script src="{KATEX_JS}"></script>
  <style>
{inter_css}
{CSS}
  </style>
</head>
<body>
{content_html}
<script>
{JS}
</script>
</body>
</html>"""


# ── PDF outline (bookmarks) ──────────────────────────────────────────────────────

def _extract_headings_from_html(html_content: str) -> list[tuple[int, str]]:
    """Extract all headings from an HTML document in document order.

    Parses the HTML string with BeautifulSoup (lxml backend) and collects
    every ``<h1>``–``<h6>`` element whose plain-text content is non-empty.

    Args:
        html_content: Complete HTML string to scan.

    Returns:
        List of ``(level, text)`` 2-tuples in document order, where ``level``
        is an integer 1–6 and ``text`` is the whitespace-normalised plain-
        text of the heading.
    """
    soup = BeautifulSoup(html_content, "lxml")
    headings: list[tuple[int, str]] = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        level = int(tag.name[1])
        text = tag.get_text(" ", strip=True)
        if text:
            headings.append((level, text))
    return headings


def _add_pdf_outline(pdf_path: Path, headings: list[tuple[int, str]]) -> None:
    """Inject a PDF outline (bookmark tree) into an existing PDF file.

    Uses PyMuPDF (``fitz``) to search each heading text in the rendered pages
    to determine the correct 1-based page number, then writes a hierarchical
    table of contents (TOC) back into the file.

    PyMuPDF requires that each TOC entry is at most one level deeper than
    the previous entry.  Any entries that would skip a level are normalised
    down (e.g. a jump from level 2 to level 4 is clamped to level 3).

    If ``fitz`` is not available (``_FITZ_AVAILABLE`` is ``False``) or the
    headings list is empty, the function returns without modifying the file.

    Note:
        The file is saved via a temporary ``.tmp.pdf`` path and then atomically
        renamed over the original to avoid corrupting the PDF on error.

    Args:
        pdf_path: Absolute ``Path`` to the PDF file to modify in-place.
        headings: List of ``(level, text)`` 2-tuples as returned by
            ``_extract_headings_from_html``.
    """
    if not _FITZ_AVAILABLE or not headings:
        return
    doc = fitz.open(str(pdf_path))
    toc: list[list] = []
    for level, title in headings:
        search_text = title[:60]  # avoid overly long search strings
        for page_num in range(doc.page_count):
            if doc[page_num].search_for(search_text):
                toc.append([level, title, page_num + 1])  # TOC uses 1-based page numbers
                break

    # PyMuPDF requires that each level is at most 1 deeper than the previous.
    # Normalize any skipped levels (e.g. h4 → h6 becomes h4 → h5).
    if toc:
        normalized: list[list] = [toc[0][:]]
        for entry in toc[1:]:
            lvl, ttl, pg = entry
            prev_lvl = normalized[-1][0]
            if lvl > prev_lvl + 1:
                lvl = prev_lvl + 1
            normalized.append([lvl, ttl, pg])

        doc.set_toc(normalized)
        tmp = pdf_path.with_suffix(".tmp.pdf")
        doc.save(str(tmp))
        doc.close()
        tmp.replace(pdf_path)
    else:
        doc.close()


# ── PDF generation ─────────────────────────────────────────────────────────────

async def generate_pdf(html_content: str, output_path: Path, doc_title: str = "") -> None:
    """Render an HTML string to a PDF file using headless Chromium.

    Launches Playwright's Chromium in headless mode, loads the HTML content,
    waits 2.5 seconds for KaTeX to finish rendering all math placeholders,
    then calls Chromium's ``Page.printToPDF`` via ``page.pdf``.

    After the PDF is saved, ``_extract_headings_from_html`` and
    ``_add_pdf_outline`` are called to inject a PDF bookmark tree so
    readers can navigate via the outline panel.

    Args:
        html_content: Complete HTML string (from ``build_html_page``) to
            render.
        output_path: Destination ``Path`` for the generated PDF file.
        doc_title: Document title string (currently unused inside this
            function; retained for logging / future use).
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 794, "height": 1123})
        # Inter is embedded as base64 data URIs → no CDN needed, font loads instantly
        await page.set_content(html_content, wait_until="networkidle")
        await page.wait_for_timeout(2500)  # let KaTeX finish all renders

        await page.pdf(
            path=str(output_path),
            format="A4",
            margin={"top": "2.2cm", "bottom": "2.2cm", "left": "2.5cm", "right": "2.5cm"},
            print_background=True,
            display_header_footer=False,
        )
        await browser.close()

    headings = _extract_headings_from_html(html_content)
    _add_pdf_outline(output_path, headings)
    print(f"  ✓ PDF saved  →  {output_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

async def main() -> None:
    """Entry point: convert all configured Markdown files to PDFs.

    Iterates over the ``DOCS`` list (defined at module level) where each
    entry is a ``dict`` with ``'input'``, ``'output'``, ``'title'``, and
    ``'doc_id'`` keys.  For each document:

    1. Reads the Markdown source with UTF-8-BOM encoding.
    2. Converts it to an HTML fragment via ``markdown_to_html``.
    3. Assembles the full HTML page via ``build_html_page``.
    4. Saves an intermediate ``.html`` file for inspection / debugging.
    5. Renders the PDF via ``generate_pdf``.

    Progress is printed to stdout and a final confirmation line is emitted
    after all files have been processed.
    """
    for doc in DOCS:
        print(f"\n→ Processing: {doc['input'].name}")

        md_text = doc["input"].read_text(encoding="utf-8-sig")  # utf-8-sig strips UTF-8 BOM
        content_html = markdown_to_html(md_text, doc_id=doc["doc_id"])
        full_html = build_html_page(content_html, doc["title"])

        # Save intermediate HTML for inspection / debugging
        html_path = doc["output"].with_suffix(".html")
        html_path.write_text(full_html, encoding="utf-8")
        print(f"  · HTML saved →  {html_path}")

        await generate_pdf(full_html, doc["output"], doc_title=doc["title"])

    print("\n✅ Done.")


if __name__ == "__main__":
    asyncio.run(main())
