"""Download Inter font woff2 files from jsDelivr to local fonts/ directory."""
import os
import sys
import warnings
from pathlib import Path

import requests

warnings.filterwarnings("ignore")

FONT_DIR = Path(__file__).parent / "fonts"
FONT_DIR.mkdir(exist_ok=True)

BASE = "https://cdn.jsdelivr.net/npm/@fontsource/inter@5.1.1/files/"
FILES = [
    "inter-latin-300-normal.woff2",
    "inter-latin-400-normal.woff2",
    "inter-latin-500-normal.woff2",
    "inter-latin-600-normal.woff2",
    "inter-latin-700-normal.woff2",
    "inter-latin-400-italic.woff2",
]

for name in FILES:
    out = FONT_DIR / name
    if out.exists():
        print(f"  exists : {name}")
        continue
    try:
        r = requests.get(BASE + name, timeout=30, verify=False)
        r.raise_for_status()
        out.write_bytes(r.content)
        print(f"  ok     : {name}  ({len(r.content):,} bytes)")
    except Exception as e:
        print(f"  FAILED : {name} — {e}", file=sys.stderr)

print("Done")
