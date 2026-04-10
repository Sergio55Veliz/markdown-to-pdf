"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


@pytest.fixture
def sample_markdown() -> str:
    """Minimal Markdown string exercising headings, lists, code, and math."""
    return (
        "# Título Principal\n\n"
        "Párrafo de prueba con **negrita** y *cursiva*.\n\n"
        "## Subtítulo\n\n"
        "- Elemento 1\n"
        "- Elemento 2\n\n"
        "```python\nprint('hola')\n```\n\n"
        "Ecuación: $E = mc^2$\n\n"
        "| Col A | Col B |\n"
        "|-------|-------|\n"
        "| 1     | 2     |\n\n"
        "---\n\n"
        "> Esto es un blockquote.\n\n"
        "~~tachado~~\n"
    )


@pytest.fixture
def propuesta_markdown() -> str | None:
    """Load propuesta_nuevas_features.md if available."""
    path = EXAMPLES_DIR / "propuesta_nuevas_features.md"
    if path.exists():
        return path.read_text(encoding="utf-8-sig")
    return None


@pytest.fixture
def dashboard_markdown() -> str | None:
    """Load dashboard_riesgo_juridico.md if available."""
    path = EXAMPLES_DIR / "dashboard_riesgo_juridico.md"
    if path.exists():
        return path.read_text(encoding="utf-8-sig")
    return None
