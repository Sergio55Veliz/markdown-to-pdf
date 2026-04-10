"""
Environment setup script — download fonts and install Playwright browsers.

Run with:
    python scripts/setup_env.py
Or via pyproject.toml:
    pip install -e .
    markdown-to-pdf-setup
"""

from __future__ import annotations

import subprocess
import sys


def main() -> None:
    print("=" * 60)
    print("  markdown-to-pdf  —  Configuración del entorno")
    print("=" * 60)

    # 1. Download Inter fonts
    print("\n[1/2] Descargando fuentes Inter …")
    from markdown_to_pdf.fonts import download_fonts
    download_fonts()

    # 2. Install Playwright Chromium browser
    print("\n[2/2] Instalando navegador Chromium para Playwright …")
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
        )
        print("  ✓ Chromium instalado correctamente.")
    except subprocess.CalledProcessError:
        print("  ⚠ No se pudo instalar Chromium automáticamente.")
        print("    Ejecute manualmente:  python -m playwright install chromium")
    except FileNotFoundError:
        print("  ⚠ Playwright no está instalado.  Instale las dependencias primero:")
        print("    pip install -r requirements.txt")

    print("\n✅ Configuración completada.")


if __name__ == "__main__":
    main()
