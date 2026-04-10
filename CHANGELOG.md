# Changelog

Todos los cambios notables del proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa [Versionado Semántico](https://semver.org/lang/es/).

---

## [1.0.0] — 2026-04-10

### Añadido

- **Estructura de paquete Python** con `src/` layout y `pyproject.toml`.
- **Pipeline PDF**: Markdown → HTML (markdown-it) → Chromium headless (Playwright) → PDF con bookmarks (PyMuPDF).
- **Pipeline Word**: Markdown → HTML → BeautifulSoup → python-docx , con soporte completo de estilos.
- **CLI interactivo** (`markdown-to-pdf`) con selector de archivo gráfico (tkinter) y fallback a consola.
- **`constants.py`**: archivo centralizado con toda la paleta de colores, fuentes, tamaños y mapas de emoji.
- **Preprocesamiento compartido**: corrección de listas en blockquotes y strikethrough `~~texto~~`.
- **Soporte de ecuaciones matemáticas**: KaTeX en PDF, LaTeX → OMML (vía XSLT de Office) en Word.
- **Syntax highlighting** para bloques de código Python y SQL (Pygments).
- **Emoji con color**: círculos de color mapeados a `●`, emoji comunes con colores semánticos.
- **Blockquotes en Word** renderizados como cajas DrawingML con bordes redondeados y fondo.
- **Tablas** con filas alternas (zebra striping), ancho automático de primera columna.
- **Bookmarks/TOC** en PDF (PyMuPDF) y Word (bookmarks + hyperlinks internos).
- **Script de setup** (`scripts/setup_env.py`): descarga de fuentes Inter + instalación de Chromium.
- **Suite de tests** con pytest: constantes, preprocesamiento, generación HTML, generación DOCX, validación de enlaces.
- **Documentación** completa: README, arquitectura, guía de estilos, guía de extensión, CONTRIBUTING.

### Migrado

- Código original de `generate_pdfs.py` (script raíz ~940 líneas) → `src/markdown_to_pdf/pdf/`.
- Código original de `generate_word.py` (script raíz ~2130 líneas) → `src/markdown_to_pdf/word/`.
- Lógica de `_validate_links.py` y `_validate_links_cross.py` → `tests/test_validate_links.py`.
- Lógica de `_download_fonts.py` → `src/markdown_to_pdf/fonts.py`.

### Eliminado

- Scripts de utilidad en raíz (`_*.py`, `_*.txt`, `_*.json`): 48 archivos de debug/análisis.
- Imágenes PNG de preview.
- Directorios `__pycache__/` y `.pytest_cache/` del repositorio.
