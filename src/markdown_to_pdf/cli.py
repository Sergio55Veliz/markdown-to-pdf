"""
CLI entry point — select a Markdown file and generate PDF and/or Word output.
"""

from __future__ import annotations

import sys

from markdown_to_pdf.file_selector import select_markdown_file


def main() -> None:
    """Interactive entry point: pick a file and choose output format."""
    print("=" * 60)
    print("  markdown-to-pdf  —  Generador de documentos")
    print("=" * 60)

    md_path = select_markdown_file()
    print(f"\nArchivo seleccionado: {md_path}")

    print("\n¿Qué formato desea generar?")
    print("  1) PDF")
    print("  2) Word (.docx)")
    print("  3) Ambos")
    choice = input("  Seleccione [1/2/3]: ").strip()

    if choice not in ("1", "2", "3"):
        print("Opción no válida. Saliendo.")
        sys.exit(1)

    if choice in ("1", "3"):
        from markdown_to_pdf.pdf.generator import generate_pdf_from_file
        generate_pdf_from_file(md_path)

    if choice in ("2", "3"):
        from markdown_to_pdf.word.generator import generate_docx_from_file
        generate_docx_from_file(md_path)

    print("\n✅ Proceso completado.")


if __name__ == "__main__":
    main()
