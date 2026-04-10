"""
Validate internal hyperlinks in generated DOCX files.

For each document:
  - Collects every <w:bookmarkStart w:name="..."> (the anchor targets).
  - Collects every <w:hyperlink w:anchor="..."> (the internal links).
  - Reports which links have no matching bookmark (broken) and which do (ok).
"""

import sys
import zipfile
import lxml.etree as ET
from pathlib import Path

W  = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

DOCS = [
    Path(__file__).parent / "propuesta_nuevas_features.docx",
    Path(__file__).parent / "dashboard_riesgo_juridico.docx",
]


def _qn(local: str) -> str:
    return f"{{{W}}}{local}"


def validate(docx_path: Path) -> None:
    print(f"\n{'='*70}")
    print(f"  {docx_path.name}")
    print(f"{'='*70}")

    if not docx_path.exists():
        print("  ✗ File not found — run generate_word.py first.")
        return

    with zipfile.ZipFile(docx_path) as zf:
        with zf.open("word/document.xml") as f:
            root = ET.parse(f).getroot()

    # ── Bookmarks ────────────────────────────────────────────────────────────
    bookmarks: list[str] = []
    for bk in root.iter(_qn("bookmarkStart")):
        name = bk.get(_qn("name"), "")
        # Skip Word's internal bookmarks (prefixed with _) and the root bookmark.
        if name and not name.startswith("_"):
            bookmarks.append(name)

    print(f"\n  Bookmarks registered ({len(bookmarks)}):")
    for bm in bookmarks:
        print(f"    • {bm}")

    # ── Internal hyperlinks ───────────────────────────────────────────────────
    links: list[dict] = []
    for hl in root.iter(_qn("hyperlink")):
        anchor = hl.get(_qn("anchor"))
        if not anchor:
            continue
        # Gather visible text from all <w:t> children.
        text = "".join(
            t.text or ""
            for t in hl.iter(_qn("t"))
        ).strip() or "(no text)"
        links.append({"anchor": anchor, "text": text})

    print(f"\n  Internal hyperlinks found ({len(links)}):")

    ok:     list[dict] = []
    broken: list[dict] = []
    bm_set = set(bookmarks)

    for lk in links:
        if lk["anchor"] in bm_set:
            ok.append(lk)
        else:
            broken.append(lk)

    if ok:
        print(f"\n  ✅ Working links ({len(ok)}):")
        for lk in ok:
            print(f"    [{lk['text']}]  →  #{lk['anchor']}")

    if broken:
        print(f"\n  ❌ Broken links ({len(broken)})  — anchor has no matching bookmark:")
        for lk in broken:
            # Try to find close matches to help diagnose typos / slug mismatches.
            candidates = [b for b in bookmarks if lk["anchor"] in b or b.startswith(lk["anchor"])]
            note = f"  (closest: {candidates[:3]})" if candidates else ""
            print(f"    [{lk['text']}]  →  #{lk['anchor']}{note}")
    else:
        print("\n  🎉 All internal links resolve correctly.")

    print()


if __name__ == "__main__":
    for doc in DOCS:
        validate(doc)
