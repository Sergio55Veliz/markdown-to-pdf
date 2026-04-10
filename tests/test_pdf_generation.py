"""Tests for the PDF generation pipeline (HTML stage only, no browser needed)."""

from __future__ import annotations

import pytest
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


class TestRealExamples:
    """Integration-style HTML checks on real example Markdown files."""

    def test_propuesta_html(self, propuesta_markdown):
        if propuesta_markdown is None:
            pytest.skip("propuesta_nuevas_features.md not found")
        html = markdown_to_html(propuesta_markdown)
        assert "<h" in html

    def test_dashboard_html(self, dashboard_markdown):
        if dashboard_markdown is None:
            pytest.skip("dashboard_riesgo_juridico.md not found")
        html = markdown_to_html(dashboard_markdown)
        assert "<h" in html

    def test_astronomia_html(self, astronomia_markdown):
        if astronomia_markdown is None:
            pytest.skip("guia_astronomia_observacional.md not found")
        html = markdown_to_html(astronomia_markdown)
        assert "<h" in html

    def test_culinaria_html(self, culinaria_markdown):
        if culinaria_markdown is None:
            pytest.skip("atlas_tecnicas_culinarias.md not found")
        html = markdown_to_html(culinaria_markdown)
        assert "<h" in html
