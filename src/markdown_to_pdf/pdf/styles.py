"""
PDF-specific CSS, KaTeX JS, and HTML page assembly.

The CSS string and JavaScript here are injected into the HTML page that
Playwright renders to produce the final PDF.  All color and font values
are derived from ``markdown_to_pdf.constants``.
"""

from __future__ import annotations

import html as html_lib

from markdown_to_pdf.constants import (
    KATEX_CSS,
    KATEX_JS,
    PdfFonts,
    rgb_hex,
    COLOR_BODY,
    COLOR_EM,
    COLOR_LINK,
    COLOR_H1_TEXT,
    COLOR_H1_BORDER,
    COLOR_H2_TEXT,
    COLOR_H2_BORDER,
    COLOR_H3_TO_H5,
    COLOR_H6_TEXT,
    COLOR_CODE_BG,
    COLOR_CODE_TEXT,
    COLOR_PRE_BG,
    COLOR_PRE_TEXT,
    COLOR_BQ_BG,
    COLOR_BQ_BORDER,
    COLOR_BQ_TEXT,
    COLOR_TH_BG,
    COLOR_TH_TEXT,
    COLOR_TD_BORDER,
    COLOR_TD_ALT_BG,
    COLOR_HR,
    COLOR_DEL,
)
from markdown_to_pdf.fonts import build_inter_font_face


CSS = rf"""
html {{
    overflow-x: hidden;
}}

@page {{
    size: A4;
    margin: 2.2cm 2.5cm 2.5cm 2.5cm;
    @bottom-left {{
        content: string(doc-title);
        font-size: 9pt;
        color: #9ca3af;
        font-family: '{PdfFonts.BODY}', sans-serif;
    }}
    @bottom-right {{
        content: counter(page) " / " counter(pages);
        font-size: 9pt;
        color: #9ca3af;
        font-family: '{PdfFonts.BODY}', sans-serif;
    }}
}}

body {{
    font-family: '{PdfFonts.BODY}', '{PdfFonts.FALLBACK}', sans-serif;
    font-size: 10.5pt;
    line-height: 1.65;
    color: {rgb_hex(COLOR_BODY)};
    background: #ffffff;
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
}}
p  {{ margin: 0 0 8pt; }}
em {{ color: {rgb_hex(COLOR_EM)}; }}
a  {{ color: {rgb_hex(COLOR_LINK)}; text-decoration: none; }}

h1, h2, h3, h4, h5, h6 {{
    page-break-after: avoid;
    break-after: avoid;
    font-weight: 700;
    line-height: 1.3;
}}
h1 {{
    font-size: 22pt;
    color: {rgb_hex(COLOR_H1_TEXT)};
    border-bottom: 3px solid {rgb_hex(COLOR_H1_BORDER)};
    padding-bottom: 10pt;
    margin: 0 0 6pt;
    string-set: doc-title content();
}}
h2 {{
    font-size: 14pt;
    font-weight: 600;
    color: {rgb_hex(COLOR_H2_TEXT)};
    border-bottom: 1.5px solid {rgb_hex(COLOR_H2_BORDER)};
    padding-bottom: 4pt;
    margin: 24pt 0 8pt;
}}
h3 {{
    font-size: 12.5pt;
    font-weight: 600;
    color: {rgb_hex(COLOR_H3_TO_H5)};
    margin: 18pt 0 6pt;
}}
h4 {{
    font-size: 12pt;
    font-weight: 600;
    color: {rgb_hex(COLOR_H3_TO_H5)};
    margin: 14pt 0 5pt;
}}
h5 {{
    font-size: 11.5pt;
    font-weight: 600;
    color: {rgb_hex(COLOR_H3_TO_H5)};
    margin: 10pt 0 4pt;
}}
h6 {{
    font-size: 11pt;
    font-weight: 700;
    color: {rgb_hex(COLOR_H6_TEXT)};
    margin: 10pt 0 4pt;
}}

.page-break-before {{
    page-break-before: always !important;
    break-before: page !important;
    margin-top: 0 !important;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 9.5pt;
    table-layout: fixed;
}}
.no-break {{
    page-break-inside: avoid !important;
    break-inside: avoid !important;
}}
.allow-break {{
    page-break-inside: auto !important;
    break-inside: auto !important;
}}
thead tr {{
    background-color: {rgb_hex(COLOR_TH_BG)};
    color: {rgb_hex(COLOR_TH_TEXT)};
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}
th {{
    padding: 7pt 10pt;
    text-align: left;
    font-weight: 600;
    border: 1px solid {rgb_hex(COLOR_TH_BG)};
    font-size: 9.5pt;
    overflow-wrap: anywhere;
    word-break: break-word;
}}
td {{
    padding: 6pt 10pt;
    border-bottom: 1px solid {rgb_hex(COLOR_TD_BORDER)};
    vertical-align: top;
    line-height: 1.5;
    word-wrap: break-word;
    overflow-wrap: anywhere;
    color: {rgb_hex(COLOR_BODY)};
}}
td strong {{ color: {rgb_hex(COLOR_H1_TEXT)}; }}
td a      {{ color: {rgb_hex(COLOR_LINK)}; }}
tr:nth-child(even) td {{
    background-color: {rgb_hex(COLOR_TD_ALT_BG)};
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}

blockquote {{
    border-left: 4px solid {rgb_hex(COLOR_BQ_BORDER)};
    margin: 10pt 0;
    padding: 8pt 14pt;
    background-color: {rgb_hex(COLOR_BQ_BG)};
    color: {rgb_hex(COLOR_BQ_TEXT)};
    border-radius: 0 6px 6px 0;
    font-size: 10pt;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}
blockquote strong     {{ color: {rgb_hex(COLOR_H1_TEXT)}; }}
blockquote p          {{ margin-bottom: 4pt; }}
blockquote p:last-child {{ margin-bottom: 0; }}
blockquote ul,
blockquote ol         {{ list-style-position: inside; padding-left: 10pt; margin-bottom: 4pt; }}
blockquote li         {{ margin-bottom: 2pt; }}
blockquote > blockquote {{
    background-color: #e0ecff;
    border-left-color: {rgb_hex(COLOR_H3_TO_H5)};
}}

ul {{ list-style-type: disc;    list-style-position: outside; padding-left: 20pt; margin-bottom: 8pt; }}
ol {{ list-style-type: decimal; list-style-position: outside; padding-left: 20pt; margin-bottom: 8pt; }}
ul ul  {{ list-style-type: circle; }}
ul ul ul {{ list-style-type: square; }}
ol ol  {{ list-style-type: lower-alpha; }}
li {{ margin-bottom: 3pt; }}

pre {{
    background-color: {rgb_hex(COLOR_PRE_BG)};
    color: {rgb_hex(COLOR_PRE_TEXT)};
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
}}
pre code {{
    background: none;
    border: none;
    color: inherit;
    padding: 0;
    font-size: 9pt;
    word-break: normal;
}}
code {{
    font-family: '{PdfFonts.MONO}', '{PdfFonts.MONO_ALT}', monospace;
    font-size: 9pt;
}}
p code, li code, td code, blockquote code,
h1 code, h2 code, h3 code, h4 code, h5 code, h6 code {{
    background-color: {rgb_hex(COLOR_CODE_BG)};
    color: {rgb_hex(COLOR_CODE_TEXT)};
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 9pt;
}}

hr {{
    border: none;
    border-top: 1px solid {rgb_hex(COLOR_HR)};
    margin: 18pt 0;
}}

.math-block {{
    margin: 16px auto;
    text-align: center;
    overflow-x: auto;
    overflow-y: hidden;
}}
.math-inline {{
    display: inline;
}}
.katex              {{ font-size: 1em !important; }}
.katex-display      {{ margin: 0.4em 0 !important; overflow-x: auto; }}

del {{
    text-decoration: line-through;
    color: {rgb_hex(COLOR_DEL)};
}}
"""


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
    """Assemble a full HTML document from a body fragment, CSS, and KaTeX."""
    inter_css = build_inter_font_face()
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
