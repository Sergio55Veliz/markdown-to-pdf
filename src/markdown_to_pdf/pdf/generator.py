"""
PDF generation pipeline.

Markdown → HTML (with math placeholders) → Chromium headless → PDF.
"""

from __future__ import annotations

import asyncio
import html as html_lib
import re
from pathlib import Path

import markdown_it
from mdit_py_plugins.dollarmath import dollarmath_plugin
from bs4 import BeautifulSoup

try:
    from pygments import highlight as _pygments_highlight
    from pygments.lexers import get_lexer_by_name as _get_lexer_by_name
    from pygments.formatters import HtmlFormatter as _HtmlFormatter
    _PYGMENTS_AVAILABLE = True
except ImportError:
    _PYGMENTS_AVAILABLE = False

from markdown_to_pdf.constants import HIGHLIGHT_LANGS
from markdown_to_pdf.preprocessing import preprocess_markdown
from markdown_to_pdf.pdf.styles import build_html_page
from markdown_to_pdf.pdf.outline import extract_headings_from_html, add_pdf_outline


# ── Math render rules ─────────────────────────────────────────────────────────

def _render_math_inline(self, tokens, idx, options, env) -> str:
    content = str(tokens[idx].content).strip()
    escaped = html_lib.escape(content, quote=True)
    return (
        f'<span class="math-inline">'
        f'<span class="katex-ph katex-ph--inline" data-formula="{escaped}"></span>'
        f"</span>"
    )


def _render_math_inline_double(self, tokens, idx, options, env) -> str:
    content = str(tokens[idx].content).strip()
    escaped = html_lib.escape(content, quote=True)
    return (
        f'<div class="math-block">'
        f'<span class="katex-ph katex-ph--display" data-formula="{escaped}"></span>'
        f"</div>\n"
    )


def _render_math_block(self, tokens, idx, options, env) -> str:
    content = str(tokens[idx].content).strip()
    escaped = html_lib.escape(content, quote=True)
    return (
        f'<div class="math-block">'
        f'<span class="katex-ph katex-ph--display" data-formula="{escaped}"></span>'
        f"</div>\n"
    )


_render_math_block_label = _render_math_block


def _build_md_parser() -> markdown_it.MarkdownIt:
    """Build the markdown-it parser configured for the PDF pipeline."""
    md = markdown_it.MarkdownIt(
        "commonmark",
        {"html": True, "typographer": False, "breaks": False},
    )
    md.enable("table")
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


# ── Syntax highlighting ──────────────────────────────────────────────────────

def _apply_syntax_highlighting(html_str: str) -> str:
    """Apply Pygments syntax highlighting to fenced code blocks in HTML."""
    if not _PYGMENTS_AVAILABLE:
        return html_str

    formatter = _HtmlFormatter(noclasses=True, style="monokai", nowrap=True)

    def replacer(m: re.Match) -> str:
        lang = m.group(1).lower()
        if lang not in HIGHLIGHT_LANGS:
            return m.group(0)
        raw_code = html_lib.unescape(m.group(2))
        try:
            lexer = _get_lexer_by_name(lang, stripall=False)
            highlighted = _pygments_highlight(raw_code, lexer, formatter)
            return f'<code class="language-{lang}">{highlighted}</code>'
        except Exception:
            return m.group(0)

    return re.sub(
        r'<code class="language-([^"]+)">(.*?)</code>',
        replacer,
        html_str,
        flags=re.DOTALL,
    )


# ── Markdown → HTML ─────────────────────────────────────────────────────────

def markdown_to_html(md_text: str, doc_id: str = "") -> str:
    """Convert Markdown source to a styled HTML body fragment."""
    text = preprocess_markdown(md_text)
    md = _build_md_parser()
    html_body = md.render(text)

    soup = BeautifulSoup(html_body, "lxml")

    for tbl in soup.find_all("table"):
        cls = list(tbl.get("class", []))
        if "allow-break" not in cls:
            tbl["class"] = cls + ["no-break"]

    if doc_id == "propuesta":
        for h2 in soup.find_all("h2"):
            if "Matriz de Cobertura" in h2.get_text():
                h2["class"] = list(h2.get("class", [])) + ["page-break-before"]
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
            continue
        colgroup = soup.new_tag("colgroup")
        colgroup.append(soup.new_tag("col", style=f"width:{pct}"))
        tbl.insert(0, colgroup)

    body = soup.body
    return _apply_syntax_highlighting(body.decode_contents() if body else "")


# ── PDF rendering ────────────────────────────────────────────────────────────

async def _render_pdf(html_content: str, output_path: Path) -> None:
    """Render HTML to PDF using Playwright / headless Chromium."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 794, "height": 1123})
        await page.set_content(html_content, wait_until="networkidle")
        await page.wait_for_timeout(2500)

        await page.pdf(
            path=str(output_path),
            format="A4",
            margin={"top": "2.2cm", "bottom": "2.2cm", "left": "2.5cm", "right": "2.5cm"},
            print_background=True,
            display_header_footer=False,
        )
        await browser.close()


async def generate_pdf(html_content: str, output_path: Path, doc_title: str = "") -> None:
    """Generate a PDF from a complete HTML string and add bookmarks."""
    await _render_pdf(html_content, output_path)
    headings = extract_headings_from_html(html_content)
    add_pdf_outline(output_path, headings)
    print(f"  ✓ PDF saved  →  {output_path}")


def generate_pdf_from_file(
    md_path: Path,
    output_path: Path | None = None,
    title: str = "",
    doc_id: str = "",
) -> Path:
    """High-level: read a Markdown file and produce a PDF.

    Returns the path to the generated PDF.
    """
    if output_path is None:
        output_path = md_path.with_suffix(".pdf")
    if not title:
        title = md_path.stem.replace("_", " ").title()

    print(f"\n→ Processing: {md_path.name}")
    md_text = md_path.read_text(encoding="utf-8-sig")
    content_html = markdown_to_html(md_text, doc_id=doc_id)
    full_html = build_html_page(content_html, title)

    html_debug = output_path.with_suffix(".html")
    html_debug.write_text(full_html, encoding="utf-8")
    print(f"  · HTML saved →  {html_debug}")

    asyncio.run(generate_pdf(full_html, output_path, doc_title=title))
    return output_path
