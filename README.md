# markdown-to-pdf

Convierte archivos Markdown (`.md`) a **PDF** y **Word (.docx)** con estilo corporativo listo para presentar: colores, fuentes, tablas con filas alternas, ecuaciones matemáticas, emoji con color y tabla de contenidos con bookmarks.

```
mi_documento.md  ──►  mi_documento.pdf   (vía Chromium headless)
                 ──►  mi_documento.docx  (vía python-docx)
```

---

## Tabla de contenidos

- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Uso rápido](#uso-rápido)
- [Uso programático](#uso-programático)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Ejecución de tests](#ejecución-de-tests)
- [Documentación adicional](#documentación-adicional)
- [Limitaciones conocidas](#limitaciones-conocidas)

---

## Requisitos previos

| Requisito | Versión mínima | Notas |
|-----------|---------------|-------|
| Python | 3.10+ | Usa `match`, uniones `X \| Y`, etc. |
| Microsoft Office | 2016+ | Solo para el XSLT de ecuaciones en Word (`MML2OMML.XSL`) |
| Sistema operativo | Windows 10/11 | Fuentes del sistema: Segoe UI, Calibri Light, Consolas |

> **Nota:** La generación de PDF usa Chromium headless y funciona en cualquier SO que soporte Playwright. La generación de Word depende de fuentes y XSLT específicos de Windows/Office.

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/markdown-to-pdf.git
cd markdown-to-pdf

# 2. Instalar el paquete en modo editable
pip install -e .

# 3. Configurar el entorno (descargar fuentes + instalar Chromium)
markdown-to-pdf-setup
```

El paso 3 ejecuta `scripts/setup_env.py`, que:
- Descarga las fuentes **Inter** (woff2) a `fonts/`.
- Instala el navegador **Chromium** para Playwright.

---

## Uso rápido

```bash
# CLI interactivo — abre un selector de archivos
markdown-to-pdf

# También funciona como módulo
python -m markdown_to_pdf
```

El CLI presenta un menú:
1. Seleccionar archivo `.md` (ventana gráfica con fallback a consola).
2. Elegir formato de salida: PDF, Word o ambos.
3. El archivo generado se guarda junto al Markdown original.

---

## Uso programático

```python
from pathlib import Path

# Generar PDF
from markdown_to_pdf.pdf.generator import generate_pdf_from_file
generate_pdf_from_file(Path("docs/informe.md"))

# Generar Word
from markdown_to_pdf.word.generator import generate_docx_from_file
generate_docx_from_file(Path("docs/informe.md"))

# Generar desde string
from markdown_to_pdf.word.generator import markdown_to_docx
doc = markdown_to_docx("# Hola\n\nPárrafo de prueba.")
doc.save("salida.docx")
```

---

## Estructura del proyecto

```
markdown-to-pdf/
├── src/markdown_to_pdf/        # Paquete principal
│   ├── __init__.py             # Versión del paquete
│   ├── __main__.py             # python -m markdown_to_pdf
│   ├── cli.py                  # Punto de entrada interactivo
│   ├── constants.py            # Colores, fuentes, tamaños, emoji maps
│   ├── preprocessing.py        # Preprocesamiento compartido de Markdown
│   ├── file_selector.py        # Selector de archivos (tkinter + fallback)
│   ├── fonts.py                # Descarga de fuentes Inter + CSS @font-face
│   ├── pdf/                    # Sub-paquete PDF
│   │   ├── generator.py        # Pipeline: Markdown → HTML → Chromium → PDF
│   │   ├── styles.py           # Template CSS + KaTeX
│   │   └── outline.py          # Bookmarks PDF vía PyMuPDF
│   └── word/                   # Sub-paquete Word
│       ├── generator.py        # Pipeline: Markdown → HTML → python-docx
│       ├── document.py         # Configuración del documento y estilos
│       ├── ooxml.py            # Helpers OOXML de bajo nivel
│       ├── rendering.py        # Renderizado de bloques, inline y blockquotes
│       └── math_rendering.py   # LaTeX → MathML → OMML
├── tests/                      # Suite de tests (pytest)
├── scripts/setup_env.py        # Setup inicial: fuentes + Chromium
├── fonts/                      # Fuentes Inter woff2 (descargadas)
├── examples/                   # Archivos Markdown de ejemplo
├── pyproject.toml              # Configuración del proyecto
├── requirements.txt            # Dependencias
└── docs/                       # Documentación extendida
```

---

## Ejecución de tests

```bash
# Ejecutar toda la suite
pytest

# Con cobertura
pytest --cov=markdown_to_pdf

# Solo un módulo
pytest tests/test_preprocessing.py -v
```

Los tests de validación de enlaces (`test_validate_links.py`) se ejecutan automáticamente cuando existen archivos `.docx` / `.pdf` generados en la raíz del proyecto.

---

## Documentación adicional

| Documento | Descripción |
|-----------|-------------|
| [docs/architecture.md](docs/architecture.md) | Arquitectura del sistema, pipeline de generación y diagramas de flujo |
| [docs/styling-guide.md](docs/styling-guide.md) | Referencia completa de estilos: colores, fuentes, tamaños y cómo personalizarlos |
| [docs/adding-output-format.md](docs/adding-output-format.md) | Guía paso a paso para implementar un nuevo formato de salida |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Flujo de trabajo, convenciones de rama y estilo de código |
| [CHANGELOG.md](CHANGELOG.md) | Historial de versiones del proyecto |

---

## Limitaciones conocidas

### PDF

- **Fuentes** — usa Inter embebida (woff2). Las fuentes del sistema no están disponibles en el renderizado Chromium headless.
- **Syntax highlighting** — depende de la librería [Pygments](https://pygments.org/). Se pueden consultar todos los lenguajes soportados con:
  ```python
  from pygments.lexers import get_all_lexers
  for name, aliases, *_ in get_all_lexers():
      print(name, aliases)
  ```
  Sin embargo, en este proyecto se ha decidido limitarlo a `python` y `sql`. Para habilitar más lenguajes, modificar el parámetro `HIGHLIGHT_LANGS` en [`constants.py` (línea 203)](src/markdown_to_pdf/constants.py#L203). Si un lenguaje incluido en `HIGHLIGHT_LANGS` no es reconocido por Pygments, el bloque se renderiza como texto plano.

### Word

- **Ecuaciones** — requieren el archivo XSLT de Microsoft Office (`MML2OMML.XSL`) en la ruta estándar de Office 2016+.
- **Blockquotes** — se renderizan como cajas de texto inline (DrawingML); la altura se estima heurísticamente.
- **Syntax highlighting** — misma limitación que en PDF: solo `python` y `sql` por defecto (ver `HIGHLIGHT_LANGS` en [`constants.py` línea 203](src/markdown_to_pdf/constants.py#L203)).

### General

- **Selector de archivos** — usa `tkinter`. En entornos sin GUI (servidores), se usa fallback a `input()` por consola.