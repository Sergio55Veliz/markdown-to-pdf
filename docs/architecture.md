# Arquitectura del sistema

## Visión general

`markdown-to-pdf` transforma archivos Markdown en documentos PDF y Word con estilo corporativo. Ambos pipelines comparten el parsing inicial y el preprocesamiento, pero divergen en la fase de renderizado.

```mermaid
flowchart LR
    MD["📄 archivo.md"]
    PRE["preprocessing.py<br/>Bloques, strikethrough"]
    PARSE["markdown-it-py<br/>+ dollarmath"]
    HTML["HTML intermedio"]

    MD --> PRE --> PARSE --> HTML

    HTML --> PDF_PATH
    HTML --> WORD_PATH

    subgraph PDF_PATH ["Pipeline PDF"]
        direction TB
        STYLES["styles.py<br/>CSS + KaTeX"]
        CHROM["Playwright<br/>Chromium headless"]
        OUTLINE["outline.py<br/>PyMuPDF bookmarks"]
        PDF_OUT["📕 archivo.pdf"]
        STYLES --> CHROM --> OUTLINE --> PDF_OUT
    end

    subgraph WORD_PATH ["Pipeline Word"]
        direction TB
        BS4["BeautifulSoup<br/>parseo HTML"]
        RENDER["rendering.py<br/>Bloques + inline"]
        DOCX_OUT["📘 archivo.docx"]
        BS4 --> RENDER --> DOCX_OUT
    end
```

---

## Pipeline PDF en detalle

```mermaid
flowchart TB
    A["Markdown bruto"] --> B["preprocess_markdown()<br/><small>blockquotes + strikethrough</small>"]
    B --> C["markdown-it render()<br/><small>math → placeholders KaTeX</small>"]
    C --> D["BeautifulSoup<br/><small>post-procesado de tablas</small>"]
    D --> E["Pygments<br/><small>syntax highlighting python/sql</small>"]
    E --> F["build_html_page()<br/><small>CSS completo + @font-face + KaTeX JS</small>"]
    F --> G["Playwright async<br/><small>Chromium → PDF A4</small>"]
    G --> H["add_pdf_outline()<br/><small>PyMuPDF: inyecta bookmarks</small>"]
    H --> I["📕 archivo.pdf"]

    style A fill:#f0f9ff,stroke:#2563eb
    style I fill:#fef2f2,stroke:#dc2626
```

### Detalle de cada fase

| Fase | Módulo | Función principal | Qué hace |
|------|--------|-------------------|----------|
| 1. Preprocesamiento | `preprocessing.py` | `preprocess_markdown()` | Corrige listas en blockquotes, convierte `~~texto~~` a `<del>` |
| 2. Parsing | `pdf/generator.py` | `_build_md_parser()` | Configura markdown-it con tabla + dollarmath, custom render rules para math |
| 3. Post-procesado HTML | `pdf/generator.py` | `markdown_to_html()` | Añade `class="no-break"` a tablas, `colgroup` para anchos, syntax highlighting |
| 4. Template HTML | `pdf/styles.py` | `build_html_page()` | Envuelve el body con CSS completo, @font-face Inter, KaTeX auto-render |
| 5. Renderizado | `pdf/generator.py` | `_render_pdf()` | Playwright abre HTML → imprime PDF A4 con márgenes |
| 6. Bookmarks | `pdf/outline.py` | `add_pdf_outline()` | Extrae headings del HTML, inyecta TOC vía PyMuPDF |

---

## Pipeline Word en detalle

```mermaid
flowchart TB
    A["Markdown bruto"] --> B["preprocess_markdown()"]
    B --> C["markdown-it render()<br/><small>math → spans/divs</small>"]
    C --> D["BeautifulSoup<br/><small>parsea HTML a árbol</small>"]
    D --> E["walk_block()<br/><small>despacha cada nodo</small>"]

    E --> F1["render_heading()"]
    E --> F2["render_paragraph()"]
    E --> F3["render_code_block()"]
    E --> F4["render_table()"]
    E --> F5["render_list()"]
    E --> F6["render_blockquote()<br/><small>DrawingML shape</small>"]
    E --> F7["render_hr()"]
    E --> F8["insert_math_block()<br/><small>LaTeX → OMML</small>"]

    F1 & F2 & F3 & F4 & F5 & F6 & F7 & F8 --> G["python-docx Document"]
    G --> H["📘 archivo.docx"]

    style A fill:#f0f9ff,stroke:#2563eb
    style H fill:#eff6ff,stroke:#1e40af
```

### Detalle de cada fase

| Fase | Módulo | Función principal | Qué hace |
|------|--------|-------------------|----------|
| 1. Preprocesamiento | `preprocessing.py` | `preprocess_markdown()` | Igual que PDF |
| 2. Parsing | `word/generator.py` | `_build_md_parser()` | markdown-it + dollarmath con render rules Word-específicas |
| 3. Árbol HTML | `word/generator.py` | `markdown_to_docx()` | BeautifulSoup parsea, `setup_document()` configura A4/márgenes/estilos |
| 4. Dispatch | `word/rendering.py` | `walk_block()` | Recorre nodos hijo del `<body>` y despacha al renderer correcto |
| 5. Inline | `word/rendering.py` | `inline_nodes_to_runs()` | Convierte HTML inline → Runs con formato (negrita, cursiva, emoji, links) |
| 6. Math | `word/math_rendering.py` | `latex_to_omml()` | LaTeX → MathML (latex2mathml) → OMML (Office XSLT) |
| 7. OOXML | `word/ooxml.py` | Múltiples helpers | Sombreado, bordes, indentación, bookmarks a nivel XML |

---

## Mapa de dependencias entre módulos

```mermaid
graph TB
    CLI["cli.py"] --> FS["file_selector.py"]
    CLI --> PDF_GEN["pdf/generator.py"]
    CLI --> WORD_GEN["word/generator.py"]

    PDF_GEN --> PREP["preprocessing.py"]
    PDF_GEN --> PDF_STYLES["pdf/styles.py"]
    PDF_GEN --> PDF_OUTLINE["pdf/outline.py"]
    PDF_GEN --> CONST["constants.py"]

    PDF_STYLES --> CONST
    PDF_STYLES --> FONTS["fonts.py"]
    PDF_OUTLINE --> CONST

    WORD_GEN --> PREP
    WORD_GEN --> WORD_DOC["word/document.py"]
    WORD_GEN --> WORD_RENDER["word/rendering.py"]
    WORD_GEN --> WORD_OOXML["word/ooxml.py"]

    WORD_DOC --> CONST
    WORD_DOC --> WORD_OOXML

    WORD_RENDER --> CONST
    WORD_RENDER --> WORD_OOXML
    WORD_RENDER --> WORD_MATH["word/math_rendering.py"]
    WORD_RENDER --> WORD_DOC

    WORD_MATH --> CONST

    FONTS --> CONST

    style CONST fill:#fef3c7,stroke:#d97706,stroke-width:2px
    style CLI fill:#dcfce7,stroke:#16a34a,stroke-width:2px
```

> **`constants.py`** (amarillo) es el nodo central — todos los módulos de estilo dependen de él.
> **`cli.py`** (verde) es el único punto de entrada del usuario.

---

## Flujo de ejecución del CLI

```mermaid
sequenceDiagram
    participant U as Usuario
    participant CLI as cli.py
    participant FS as file_selector.py
    participant PDF as pdf/generator.py
    participant PW as Playwright
    participant WORD as word/generator.py

    U->>CLI: markdown-to-pdf
    CLI->>FS: select_markdown_file()
    FS-->>U: Ventana tkinter (o input)
    U-->>FS: archivo.md
    FS-->>CLI: Path("archivo.md")
    CLI-->>U: ¿Formato? [1/2/3]
    U-->>CLI: "3" (ambos)

    CLI->>PDF: generate_pdf_from_file()
    PDF->>PDF: markdown_to_html()
    PDF->>PW: _render_pdf() — Chromium
    PW-->>PDF: archivo.pdf (raw)
    PDF->>PDF: add_pdf_outline()
    PDF-->>CLI: archivo.pdf ✓

    CLI->>WORD: generate_docx_from_file()
    WORD->>WORD: markdown_to_docx()
    WORD-->>CLI: archivo.docx ✓

    CLI-->>U: ✅ Proceso completado
```
