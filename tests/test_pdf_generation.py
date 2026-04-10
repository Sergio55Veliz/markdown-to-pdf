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
