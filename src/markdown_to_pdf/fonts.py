"""
Font utilities — download Inter woff2 fonts and build CSS ``@font-face`` blocks.
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path

import requests

from markdown_to_pdf.constants import FONT_BASE_URL, FONT_FILES, FONT_SPECS


def get_fonts_dir() -> Path:
    """Return the ``fonts/`` directory at the project root."""
    return Path(__file__).resolve().parent.parent.parent / "fonts"


def download_fonts(fonts_dir: Path | None = None) -> None:
    """Download missing Inter woff2 files from jsDelivr."""
    if fonts_dir is None:
        fonts_dir = get_fonts_dir()
    fonts_dir.mkdir(exist_ok=True)

    for name in FONT_FILES:
        out = fonts_dir / name
        if out.exists():
            print(f"  exists : {name}")
            continue
        try:
            r = requests.get(
                FONT_BASE_URL + name,
                timeout=30,
            )
            r.raise_for_status()
            out.write_bytes(r.content)
            print(f"  ok     : {name}  ({len(r.content):,} bytes)")
        except Exception as e:
            print(f"  FAILED : {name} — {e}", file=sys.stderr)

    print("Descarga de fuentes completada.")


def build_inter_font_face(fonts_dir: Path | None = None) -> str:
    """Build CSS ``@font-face`` blocks embedding Inter woff2 files as base64."""
    if fonts_dir is None:
        fonts_dir = get_fonts_dir()
    blocks: list[str] = []
    for filename, weight, style in FONT_SPECS:
        path = fonts_dir / filename
        if not path.exists():
            continue
        data = base64.b64encode(path.read_bytes()).decode()
        blocks.append(
            f"@font-face {{\n"
            f"  font-family: 'Inter';\n"
            f"  font-style: {style};\n"
            f"  font-weight: {weight};\n"
            f"  src: url('data:font/woff2;base64,{data}') format('woff2');\n"
            f"}}"
        )
    return "\n".join(blocks)
