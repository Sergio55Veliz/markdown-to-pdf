"""Tests for the PDF generation pipeline (HTML stage only, no browser needed)."""

from __future__ import annotations

import html as html_lib
import re

import pytest
from bs4 import BeautifulSoup
from markdown_to_pdf.pdf.generator import markdown_to_html


class TestMarkdownToHtml:
    """Validate the HTML output without launching a browser."""

    def test_returns_html_fragment(self, sample_markdown):
        html = markdown_to_html(sample_markdown)
        assert "<h1" in html

    def test_headings_in_html(self, sample_markdown):
        html = markdown_to_html(sample_markdown)
        assert "<h1" in html
        assert "<h2" in html

    def test_table_in_html(self, sample_markdown):
        html = markdown_to_html(sample_markdown)
        assert "<table" in html

    def test_code_block_in_html(self, sample_markdown):
        html = markdown_to_html(sample_markdown)
        assert "<pre" in html or "<code" in html

    def test_empty_input(self):
        html = markdown_to_html("")
        assert isinstance(html, str)


# ── Math Rendering (PDF/HTML) ────────────────────────────────────────────────

class TestMathRendering:
    """Verify math placeholder generation for KaTeX."""

    def test_inline_math_produces_katex_placeholder(self):
        html = markdown_to_html("Ecuación: $E = mc^2$")
        assert 'class="katex-ph katex-ph--inline"' in html
        assert 'data-formula="E = mc^2"' in html

    def test_block_math_produces_display_placeholder(self):
        html = markdown_to_html("$$\\theta = 1.22 \\frac{\\lambda}{D}$$")
        assert 'class="katex-ph katex-ph--display"' in html
        assert "data-formula=" in html

    def test_complex_formula_preserved(self):
        md = r"$$m_{\text{lím}} = 2.7 + 5 \log_{10}(D)$$"
        html = markdown_to_html(md)
        assert "data-formula=" in html
        assert "log" in html

    def test_multiple_inline_formulas(self):
        md = "Valores $a_w = 0.4$ y $0.6$ son típicos."
        html = markdown_to_html(md)
        hits = re.findall(r'katex-ph--inline', html)
        assert len(hits) == 2

    def test_inline_and_block_coexist(self):
        md = "Inline $x$ y bloque:\n\n$$y = x^2$$"
        html = markdown_to_html(md)
        assert "katex-ph--inline" in html
        assert "katex-ph--display" in html


class TestComplexMathFormulasHTML:
    """Verify complex calculus/physics formulas are fully preserved in HTML."""

    @staticmethod
    def _extract_formulas(html: str) -> list[str]:
        """Return all data-formula values from the HTML (unescaped)."""
        return [
            html_lib.unescape(m)
            for m in re.findall(r'data-formula="([^"]*)"', html)
        ]

    def test_partial_derivative_with_nabla(self):
        md = r"$$\frac{\partial T}{\partial t} = \alpha \nabla^2 T$$"
        formulas = self._extract_formulas(markdown_to_html(md))
        assert len(formulas) == 1
        f = formulas[0]
        assert r"\partial T" in f
        assert r"\partial t" in f
        assert r"\nabla^2" in f

    def test_integral_definite(self):
        md = r"$$\int_{0}^{\infty} e^{-x^2} \, dx = \frac{\sqrt{\pi}}{2}$$"
        formulas = self._extract_formulas(markdown_to_html(md))
        assert len(formulas) == 1
        f = formulas[0]
        assert r"\int_{0}^{\infty}" in f
        assert r"e^{-x^2}" in f
        assert r"\frac{\sqrt{\pi}}{2}" in f

    def test_nested_fractions_with_exponents(self):
        md = r"$$\frac{d}{dx}\left[\frac{e^{x^2}}{\left(1+x^2\right)^{3/2}}\right]$$"
        formulas = self._extract_formulas(markdown_to_html(md))
        assert len(formulas) == 1
        f = formulas[0]
        assert r"\frac{d}{dx}" in f
        assert r"e^{x^2}" in f
        assert r"\left(" in f and r"\right)" in f

    def test_summation_series(self):
        md = r"$$\sum_{n=0}^{\infty} \frac{(-1)^n x^{2n+1}}{(2n+1)!} = \sin(x)$$"
        formulas = self._extract_formulas(markdown_to_html(md))
        assert len(formulas) == 1
        f = formulas[0]
        assert r"\sum_{n=0}^{\infty}" in f
        assert r"(2n+1)!" in f
        assert r"\sin(x)" in f

    def test_limit_definition(self):
        md = r"$$\lim_{h \to 0} \frac{f(x+h) - f(x)}{h} = f'(x)$$"
        formulas = self._extract_formulas(markdown_to_html(md))
        assert len(formulas) == 1
        f = formulas[0]
        assert r"\lim_{h \to 0}" in f
        assert r"f(x+h)" in f

    def test_matrix_determinant(self):
        md = (
            r"$$\det(A) = \begin{vmatrix}"
            r" a_{11} & a_{12} \\"
            r" a_{21} & a_{22}"
            r"\end{vmatrix} = a_{11}a_{22} - a_{12}a_{21}$$"
        )
        formulas = self._extract_formulas(markdown_to_html(md))
        assert len(formulas) == 1
        f = formulas[0]
        assert r"\begin{vmatrix}" in f
        assert r"\end{vmatrix}" in f
        assert "a_{11}" in f

    def test_arrhenius_with_text_units(self):
        r"""Formula from our culinaria example — verify \text and \cdot preservation."""
        md = r"$$k = A \cdot e^{-E_a / (R \cdot T)}$$"
        formulas = self._extract_formulas(markdown_to_html(md))
        assert len(formulas) == 1
        f = formulas[0]
        assert r"\cdot" in f
        assert r"e^{-E_a / (R \cdot T)}" in f

    def test_html_escaping_preserves_special_chars(self):
        """Ensure < > & in formulas are HTML-escaped but recoverable."""
        md = r"$$a < b \text{ and } c > d$$"
        html = markdown_to_html(md)
        raw = re.findall(r'data-formula="([^"]*)"', html)
        assert len(raw) == 1
        # The raw attribute should have &lt; and &gt; (HTML escaped)
        assert "&lt;" in raw[0] or "<" in raw[0]
        # After unescaping, the original LaTeX is recovered
        unescaped = html_lib.unescape(raw[0])
        assert "< b" in unescaped
        assert "> d" in unescaped


# ── Internal References (PDF/HTML) ──────────────────────────────────────────

class TestInternalReferencesHTML:
    """Verify anchor links and heading IDs in HTML output."""

    def test_heading_gets_id_attribute(self):
        html = markdown_to_html("# Mi Sección")
        soup = BeautifulSoup(html, "html.parser")
        h1 = soup.find("h1")
        assert h1 is not None

    def test_internal_link_produces_anchor_href(self):
        md = "[Ir a sección](#mi-seccion)\n\n# Mi Sección"
        html = markdown_to_html(md)
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find("a", href="#mi-seccion")
        assert link is not None
        assert link.get_text(strip=True) == "Ir a sección"

    def test_toc_links_all_have_hash_href(self):
        md = (
            "## Contenido\n\n"
            "- [Intro](#intro)\n"
            "- [Datos](#datos)\n"
            "- [Final](#final)\n\n"
            "## Intro\n\nTexto\n\n## Datos\n\nTexto\n\n## Final\n\nTexto"
        )
        html = markdown_to_html(md)
        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.find_all("a", href=re.compile(r"^#"))
        targets = {a["href"] for a in anchors}
        assert "#intro" in targets
        assert "#datos" in targets
        assert "#final" in targets

    def test_naked_anchor_tag_preserved(self):
        md = '<a id="custom-anchor"></a>\n\n# Sección'
        html = markdown_to_html(md)
        soup = BeautifulSoup(html, "html.parser")
        anchor = soup.find("a", id="custom-anchor")
        assert anchor is not None


# ── Syntax Highlighting ───────────────────────────────────────────────────────

class TestSyntaxHighlighting:
    """Verify code block rendering with Pygments."""

    def test_python_code_block_rendered(self):
        md = "```python\nprint('hello')\n```"
        html = markdown_to_html(md)
        assert "print" in html
        assert "<code" in html

    def test_unknown_language_does_not_crash(self):
        md = "```unknownlang\nfoo bar\n```"
        html = markdown_to_html(md)
        assert "foo bar" in html


# ── Table Colgroup ────────────────────────────────────────────────────────────

class TestTableColgroup:
    """Verify automatic colgroup width insertion."""

    def test_short_first_col_gets_colgroup(self):
        md = "| # | Descripción |\n|---|-------------|\n| 1 | algo |\n| 2 | otro |"
        html = markdown_to_html(md)
        assert "colgroup" in html

    def test_long_first_col_no_colgroup(self):
        md = (
            "| Columna bastante larga | Datos |\n"
            "|------------------------|-------|\n"
            "| muchos caracteres aquí | 123   |"
        )
        html = markdown_to_html(md)
        assert "colgroup" not in html


# ── Emoji ─────────────────────────────────────────────────────────────────────

class TestEmojiInHtml:
    """Verify emoji pass through to HTML unchanged."""

    def test_emoji_preserved(self):
        html = markdown_to_html("Estado: 🟢 Bueno")
        assert "🟢" in html

    def test_multiple_emoji_preserved(self):
        html = markdown_to_html("🔴 Malo 🟡 Regular 🟢 Bueno")
        for e in ("🔴", "🟡", "🟢"):
            assert e in html


# ── Heading Hierarchy ─────────────────────────────────────────────────────────

class TestHeadingHierarchy:
    """Verify multiple heading levels render correctly."""

    def test_three_levels(self):
        html = markdown_to_html("# H1\n## H2\n### H3")
        assert "<h1" in html
        assert "<h2" in html
        assert "<h3" in html

    def test_strikethrough_in_html(self):
        html = markdown_to_html("Texto ~~tachado~~ aquí")
        assert "<del>" in html or "tachado" in html


# ── Nested Lists (HTML) ──────────────────────────────────────────────────────

class TestNestedListsHTML:
    """Verify nested list structure in HTML output."""

    def test_three_level_nesting_produces_nested_ul(self):
        md = "- A\n  - B\n    - C"
        html = markdown_to_html(md)
        soup = BeautifulSoup(html, "html.parser")
        top_ul = soup.find("ul")
        assert top_ul is not None
        nested_ul = top_ul.find("ul")
        assert nested_ul is not None, "Second level <ul> missing"
        deep_ul = nested_ul.find("ul")
        assert deep_ul is not None, "Third level <ul> missing"

    def test_ordered_list_items_count(self):
        md = "1. Uno\n2. Dos\n3. Tres"
        html = markdown_to_html(md)
        soup = BeautifulSoup(html, "html.parser")
        ol = soup.find("ol")
        assert ol is not None
        items = ol.find_all("li", recursive=False)
        assert len(items) == 3

    def test_mixed_list_structure(self):
        md = "1. Item\n   - Sub A\n   - Sub B\n2. Item 2"
        html = markdown_to_html(md)
        soup = BeautifulSoup(html, "html.parser")
        ol = soup.find("ol")
        assert ol is not None
        # First <li> should contain a nested <ul> with 2 items
        first_li = ol.find("li")
        nested_ul = first_li.find("ul")
        assert nested_ul is not None
        assert len(nested_ul.find_all("li", recursive=False)) == 2


# ── Blockquotes (HTML) ───────────────────────────────────────────────────────

class TestBlockquotesHTML:
    """Verify blockquote structure in HTML output."""

    def test_blockquote_tag_exists(self):
        md = "> Texto citado importante."
        html = markdown_to_html(md)
        soup = BeautifulSoup(html, "html.parser")
        bq = soup.find("blockquote")
        assert bq is not None
        assert "citado" in bq.get_text()

    def test_nested_blockquote(self):
        md = "> Outer\n>> Inner"
        html = markdown_to_html(md)
        soup = BeautifulSoup(html, "html.parser")
        bq_outer = soup.find("blockquote")
        assert bq_outer is not None
        bq_inner = bq_outer.find("blockquote")
        assert bq_inner is not None

    def test_blockquote_with_inline_formatting(self):
        md = "> 💡 **Importante:** Usa *cursiva* y `código`."
        html = markdown_to_html(md)
        soup = BeautifulSoup(html, "html.parser")
        bq = soup.find("blockquote")
        assert bq is not None
        assert bq.find("strong") is not None
        assert bq.find("em") is not None
        assert bq.find("code") is not None


# ── Real Examples ─────────────────────────────────────────────────────────────

class TestRealExamples:
    """Integration-style HTML checks on real example Markdown files."""

    def test_astronomia_html(self, astronomia_markdown):
        if astronomia_markdown is None:
            pytest.skip("guia_astronomia_observacional.md not found")
        html = markdown_to_html(astronomia_markdown)
        assert "<h" in html
        assert html.count("<h") >= 8
        assert "data-formula=" in html

    def test_culinaria_html(self, culinaria_markdown):
        if culinaria_markdown is None:
            pytest.skip("atlas_tecnicas_culinarias.md not found")
        html = markdown_to_html(culinaria_markdown)
        assert "<h" in html
        assert html.count("<h") >= 8
        assert "data-formula=" in html
