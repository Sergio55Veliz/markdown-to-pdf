"""
Constants and style definitions shared across PDF and Word generators.

All colors are defined as ``(R, G, B)`` integer tuples.  Use the helper
functions ``rgb_hex()`` and ``rgb_docx()`` to convert to the format
required by each output backend.

Font names differ between PDF (embedded Inter) and Word (system fonts).
Use ``PdfFonts`` or ``WordFonts`` depending on the target format.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docx.shared import RGBColor

# ── Color Palette ──────────────────────────────────────────────────────────────
# Canonical source of truth: (R, G, B) tuples.

COLOR_H1_TEXT    = (0x0F, 0x17, 0x2A)
COLOR_H1_BORDER  = (0x1E, 0x40, 0xAF)
COLOR_H2_TEXT    = (0x1E, 0x40, 0xAF)
COLOR_H2_BORDER  = (0xBF, 0xDB, 0xFE)
COLOR_H3_TO_H5   = (0x1D, 0x4E, 0xD8)
COLOR_H6_TEXT    = (0x47, 0x55, 0x69)
COLOR_BODY       = (0x1E, 0x29, 0x3B)
COLOR_EM         = (0x47, 0x55, 0x69)
COLOR_LINK       = (0x25, 0x63, 0xEB)
COLOR_CODE_BG    = (0xF1, 0xF5, 0xF9)
COLOR_CODE_TEXT  = (0x0F, 0x17, 0x2A)
COLOR_PRE_BG     = (0x1E, 0x20, 0x30)
COLOR_PRE_TEXT   = (0xC8, 0xD3, 0xF5)
COLOR_BQ_BG      = (0xEF, 0xF6, 0xFF)
COLOR_BQ_BORDER  = (0x25, 0x63, 0xEB)
COLOR_BQ_TEXT    = (0x33, 0x41, 0x55)
COLOR_DEL        = (0x6B, 0x72, 0x80)
COLOR_TH_BG      = (0x1E, 0x3A, 0x8A)
COLOR_TH_TEXT    = (0xFF, 0xFF, 0xFF)
COLOR_TD_BORDER  = (0xCB, 0xD5, 0xE1)
COLOR_TD_ALT_BG  = (0xF1, 0xF5, 0xF9)
COLOR_HR         = (0xE2, 0xE8, 0xF0)

HEADING_COLORS = {
    1: COLOR_H1_TEXT,
    2: COLOR_H2_TEXT,
    3: COLOR_H3_TO_H5,
    4: COLOR_H3_TO_H5,
    5: COLOR_H3_TO_H5,
    6: COLOR_H6_TEXT,
}


# ── Color helpers ──────────────────────────────────────────────────────────────

def rgb_hex(color: tuple[int, int, int]) -> str:
    """Return a CSS hex color string like ``'#1e293b'``."""
    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"


def rgb_hex_upper(color: tuple[int, int, int]) -> str:
    """Return an uppercase 6-char hex string (no ``#``) for OOXML attributes."""
    return f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"


def rgb_docx(color: tuple[int, int, int]) -> "RGBColor":
    """Convert an RGB tuple to a ``docx.shared.RGBColor``."""
    from docx.shared import RGBColor as _RGBColor
    return _RGBColor(*color)


# ── Font families ──────────────────────────────────────────────────────────────

class PdfFonts:
    """Font family names used by the PDF generator (embedded Inter woff2)."""
    BODY = "Inter"
    HEADING = "Inter"
    MONO = "Consolas"
    MONO_ALT = "Courier New"
    FALLBACK = "Segoe UI"


class WordFonts:
    """Font family names used by the Word generator (system fonts)."""
    BODY = "Segoe UI"
    HEADING = "Calibri Light"
    MONO = "Consolas"
    EMOJI = "Segoe UI Emoji"


# ── Font sizes (pt) ───────────────────────────────────────────────────────────

FONT_BODY_PT  = 10.5
FONT_CODE_PT  = 9.0
PARA_SPACING_PT = 7


# ── Heading configuration ─────────────────────────────────────────────────────

HEADING_SIZE = {1: 22, 2: 14, 3: 12, 4: 11, 5: 11, 6: 10}
HEADING_BOLD = {1: True, 2: False, 3: False, 4: False, 5: False, 6: True}
HEADING_SPACE_BEFORE = {1: 0,  2: 24, 3: 18, 4: 14, 5: 10, 6: 10}
HEADING_SPACE_AFTER  = {1: 8,  2: 8,  3: 6,  4: 5,  5: 4,  6: 4}


# ── Emoji maps ────────────────────────────────────────────────────────────────

BLACK_CIRCLE = "\u25CF"

CIRCLE_EMOJI: dict[str, tuple[int, int, int]] = {
    "\U0001F534": (0xDC, 0x26, 0x26),  # 🔴 red
    "\U0001F535": (0x29, 0x63, 0xEB),  # 🔵 blue
    "\U0001F7E0": (0xEA, 0x58, 0x0C),  # 🟠 orange
    "\U0001F7E1": (0xCA, 0x8A, 0x04),  # 🟡 yellow
    "\U0001F7E2": (0x16, 0xA3, 0x4A),  # 🟢 green
    "\U0001F7E3": (0x7C, 0x3A, 0xED),  # 🟣 purple
    "\U0001F7E4": (0x78, 0x35, 0x6F),  # 🟤 brown
    "\U000026AB": (0x6B, 0x72, 0x80),  # ⚫ black
    "\U000026AA": (0xD1, 0xD5, 0xDB),  # ⚪ white
    "\U0001F7E5": (0xDC, 0x26, 0x26),  # 🟥 red square
    "\U0001F7E6": (0x29, 0x63, 0xEB),  # 🟦 blue square
    "\U0001F7E7": (0xEA, 0x58, 0x0C),  # 🟧 orange square
    "\U0001F7E8": (0xCA, 0x8A, 0x04),  # 🟨 yellow square
    "\U0001F7E9": (0x16, 0xA3, 0x4A),  # 🟩 green square
    "\U0001F7EA": (0x7C, 0x3A, 0xED),  # 🟪 purple square
    "\U0001F7EB": (0x78, 0x35, 0x6F),  # 🟫 brown square
}

EMOJI_COLOR: dict[str, tuple[int, int, int]] = {
    "\u2705": (0x16, 0xA3, 0x4A),   # ✅ check mark  → green
    "\u274C": (0xDC, 0x26, 0x26),   # ❌ cross mark  → red
    "\u26A0": (0xD9, 0x77, 0x06),   # ⚠  warning     → amber
    "\u2757": (0xDC, 0x26, 0x26),   # ❗ exclamation → red
    "\u2714": (0x16, 0xA3, 0x4A),   # ✔  check       → green
    "\u2716": (0xDC, 0x26, 0x26),   # ✖  cross       → red
    "\u26A1": (0xCA, 0x8A, 0x04),   # ⚡ lightning   → yellow
    "\u2B50": (0xCA, 0x8A, 0x04),   # ⭐ star        → yellow
    "\U0001F4A1": (0xD9, 0x77, 0x06),  # 💡 bulb        → amber
    "\U0001F680": (0x29, 0x63, 0xEB),  # 🚀 rocket      → blue
    "\U0001F4CC": (0xDC, 0x26, 0x26),  # 📌 pin         → red
    "\U0001F4CD": (0xDC, 0x26, 0x26),  # 📍 location    → red
    "\U0001F4B0": (0x16, 0xA3, 0x4A),  # 💰 money       → green
    "\U0001F4CA": (0x29, 0x63, 0xEB),  # 📊 bar chart   → blue
    "\U0001F3AF": (0xDC, 0x26, 0x26),  # 🎯 target      → red
    "\U0001F3C6": (0xCA, 0x8A, 0x04),  # 🏆 trophy      → gold
    "\U0001F4C8": (0x16, 0xA3, 0x4A),  # 📈 chart up    → green
    "\U0001F4C9": (0xDC, 0x26, 0x26),  # 📉 chart down  → red
    "\U0001F511": (0xCA, 0x8A, 0x04),  # 🔑 key         → yellow
    "\U0001F4DD": (0x29, 0x63, 0xEB),  # 📝 memo        → blue
    "\U0001F31F": (0xCA, 0x8A, 0x04),  # 🌟 glow star   → yellow
    "\U0001F4BC": (0x29, 0x63, 0xEB),  # 💼 briefcase   → blue
    "\U0001F4CB": (0x29, 0x63, 0xEB),  # 📋 clipboard   → blue
    "\U0001F514": (0xCA, 0x8A, 0x04),  # 🔔 bell        → yellow
    "\U0001F310": (0x29, 0x63, 0xEB),  # 🌐 globe       → blue
    "\U0001F504": (0x29, 0x63, 0xEB),  # 🔄 arrows      → blue
    "\u27A1": (0x29, 0x63, 0xEB),   # ➡ arrow right  → blue
    "\u2B05": (0x29, 0x63, 0xEB),   # ⬅ arrow left   → blue
    "\u2B06": (0x29, 0x63, 0xEB),   # ⬆ arrow up     → blue
    "\u2B07": (0x29, 0x63, 0xEB),   # ⬇ arrow down   → blue
    "\U0001F6AB": (0xDC, 0x26, 0x26),  # 🚫 no entry    → red
    "\U0001F4AF": (0xDC, 0x26, 0x26),  # 💯 100         → red
    "\U0001F50D": (0x29, 0x63, 0xEB),  # 🔍 magnifier   → blue
}

EMOJI_RE = re.compile(
    r'([\u2600-\u27BF\U0001F300-\U0001FBFF])\uFE0F?',
    re.UNICODE,
)


# ── Font download configuration ───────────────────────────────────────────────

FONT_BASE_URL = "https://cdn.jsdelivr.net/npm/@fontsource/inter@5.1.1/files/"
FONT_FILES = [
    "inter-latin-300-normal.woff2",
    "inter-latin-400-normal.woff2",
    "inter-latin-500-normal.woff2",
    "inter-latin-600-normal.woff2",
    "inter-latin-700-normal.woff2",
    "inter-latin-400-italic.woff2",
]

FONT_SPECS = [
    ("inter-latin-300-normal.woff2", 300, "normal"),
    ("inter-latin-400-normal.woff2", 400, "normal"),
    ("inter-latin-400-italic.woff2", 400, "italic"),
    ("inter-latin-500-normal.woff2", 500, "normal"),
    ("inter-latin-600-normal.woff2", 600, "normal"),
    ("inter-latin-700-normal.woff2", 700, "normal"),
]


# ── KaTeX CDN ─────────────────────────────────────────────────────────────────

KATEX_CSS = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css"
KATEX_JS  = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"


# ── Syntax highlighting ───────────────────────────────────────────────────────

HIGHLIGHT_LANGS = {"python", "sql"}


# ── Office XSLT path (for Word OMML math) ─────────────────────────────────────

XSLT_PATH = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"
