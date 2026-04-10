"""Tests for the Word generation pipeline (no rendering, no file I/O)."""

from __future__ import annotations

import pytest
from markdown_to_pdf.word.generator import markdown_to_docx


class TestMarkdownToDocx:
    """Smoke tests: ensure key Markdown constructs produce a document."""

    def test_returns_document(self, sample_markdown):
        doc = markdown_to_docx(sample_markdown)
        assert doc is not None
        assert len(doc.paragraphs) > 0

    def test_headings_present(self, sample_markdown):
        doc = markdown_to_docx(sample_markdown)
        heading_styles = {p.style.name for p in doc.paragraphs if "Heading" in (p.style.name or "")}
        assert "Heading 1" in heading_styles
        assert "Heading 2" in heading_styles

    def test_table_present(self, sample_markdown):
        doc = markdown_to_docx(sample_markdown)
        assert len(doc.tables) >= 1

    def test_empty_input(self):
        doc = markdown_to_docx("")
        assert doc is not None


class TestRealExamples:
    """Integration-style checks on real example Markdown files."""

    def test_propuesta_docx(self, propuesta_markdown):
        if propuesta_markdown is None:
            pytest.skip("propuesta_nuevas_features.md not found")
        doc = markdown_to_docx(propuesta_markdown)
        assert doc is not None
        assert len(doc.paragraphs) > 0

    def test_dashboard_docx(self, dashboard_markdown):
        if dashboard_markdown is None:
            pytest.skip("dashboard_riesgo_juridico.md not found")
        doc = markdown_to_docx(dashboard_markdown)
        assert doc is not None
        assert len(doc.paragraphs) > 0

    def test_astronomia_docx(self, astronomia_markdown):
        if astronomia_markdown is None:
            pytest.skip("guia_astronomia_observacional.md not found")
        doc = markdown_to_docx(astronomia_markdown)
        assert doc is not None
        assert len(doc.paragraphs) > 0

    def test_culinaria_docx(self, culinaria_markdown):
        if culinaria_markdown is None:
            pytest.skip("atlas_tecnicas_culinarias.md not found")
        doc = markdown_to_docx(culinaria_markdown)
        assert doc is not None
        assert len(doc.paragraphs) > 0
