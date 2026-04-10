"""
Cross-validate internal hyperlinks between the generated PDF and DOCX for each document.

For each document pair (PDF + DOCX):

  PDF side (via PyMuPDF / fitz):
    • Link annotations  : every /Annot/Subtype/Link whose Dest is a named string
                          → these are the *sources* (where a link starts).
    • Named destinations: every /Names/Dests entry
                          → these are the *targets* (where a link lands).

  DOCX side (via zipfile + lxml):
    • <w:hyperlink w:anchor="..."> → link sources
    • <w:bookmarkStart w:name="..."> → link targets

Reports for each pair:
  1. Links present in PDF but missing in DOCX (and vice versa).
  2. Targets (anchors) present in PDF but missing in DOCX (and vice versa).
  3. For every link source: whether its target exists in BOTH documents.
"""

import re
import zipfile
from pathlib import Path
import lxml.etree as ET
import fitz  # PyMuPDF

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent

PAIRS = [
    {
        "label": "propuesta_nuevas_features",
        "pdf":  BASE / "propuesta_nuevas_features.pdf",
        "docx": BASE / "propuesta_nuevas_features.docx",
    },
    {
        "label": "dashboard_riesgo_juridico",
        "pdf":  BASE / "dashboard_riesgo_juridico.pdf",
        "docx": BASE / "dashboard_riesgo_juridico.docx",
    },
]

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _qn(local: str) -> str:
    return f"{{{W}}}{local}"


# ── PDF extraction ─────────────────────────────────────────────────────────────

def _pdf_named_dests(doc: fitz.Document) -> set[str]:
    """
    Extract all named destinations from the PDF catalog.

    Chromium-generated PDFs store them in /Catalog/Dests as a flat dict:
      << /name1 [pageRef /XYZ ...] /name2 [...] ... >>

    Some PDFs (especially those using a Names tree) store them under
    /Catalog/Names/Dests. We handle both cases.
    """
    dests: set[str] = set()
    catalog_xref = doc.pdf_catalog()

    # ── Case 1: /Catalog/Dests (flat dict, Chromium style) ────────────────────
    dests_key = doc.xref_get_key(catalog_xref, "Dests")
    if dests_key and dests_key[0] not in ("null", ""):
        # dests_key is (type, value).  type="xref" → resolve; type="dict" → inline
        if dests_key[0] == "xref":
            dests_xref = int(dests_key[1].split()[0])
            obj_str = doc.xref_object(dests_xref)
        else:
            obj_str = dests_key[1]
        # Each PDF Name entry looks like: /somename [...]
        for m in re.finditer(r"/([A-Za-z0-9_\-.]+)\s*\[", obj_str):
            dests.add(m.group(1))

    # ── Case 2: /Catalog/Names/Dests (Names tree, general style) ──────────────
    names_key = doc.xref_get_key(catalog_xref, "Names")
    if names_key and names_key[0] not in ("null", ""):
        try:
            if names_key[0] == "xref":
                names_xref = int(names_key[1].split()[0])
                subdests_key = doc.xref_get_key(names_xref, "Dests")
            else:
                subdests_key = ("null", "")
            if subdests_key and subdests_key[0] not in ("null", ""):
                if subdests_key[0] == "xref":
                    arr_xref = int(subdests_key[1].split()[0])
                    arr_obj = doc.xref_object(arr_xref)
                else:
                    arr_obj = subdests_key[1]
                # Names array alternates (string_dest, dest_value, ...)
                # Strings can be (name) or <hex>
                for m in re.finditer(r"\(([^)]+)\)", arr_obj):
                    dests.add(m.group(1))
        except Exception:
            pass

    return dests


def _pdf_links_and_dests(pdf_path: Path) -> tuple[list[dict], set[str]]:
    """
    Returns:
      links : list of {text, dest, page} for every internal named-dest link.
      dests : set of all named destination strings defined in the PDF.
    """
    doc = fitz.open(str(pdf_path))
    links: list[dict] = []

    dests = _pdf_named_dests(doc)

    # ── Link annotations (sources) ────────────────────────────────────────────
    # get_links() kind=4 means LINK_NAMED; the destination name is in "nameddest"
    for page_num in range(doc.page_count):
        page = doc[page_num]
        for lk in page.get_links():
            if lk.get("kind") != fitz.LINK_NAMED:
                continue
            dest_name = lk.get("nameddest", "") or lk.get("name", "")
            if not dest_name:
                continue
            rect = lk.get("from")
            text = page.get_text("text", clip=rect).strip().replace("\n", " ") if rect else ""
            links.append({"text": text or "(no text)", "dest": dest_name, "page": page_num + 1})

    doc.close()
    return links, dests


# ── DOCX extraction ────────────────────────────────────────────────────────────

def _docx_links_and_bookmarks(docx_path: Path) -> tuple[list[dict], set[str]]:
    """
    Returns:
      links     : list of {text, anchor} for every <w:hyperlink w:anchor="...">.
      bookmarks : set of all bookmark names (excluding Word-internal _ prefixed ones).
    """
    with zipfile.ZipFile(docx_path) as zf:
        with zf.open("word/document.xml") as f:
            root = ET.parse(f).getroot()

    bookmarks: set[str] = set()
    for bk in root.iter(_qn("bookmarkStart")):
        name = bk.get(_qn("name"), "")
        if name and not name.startswith("_"):
            bookmarks.add(name)

    links: list[dict] = []
    for hl in root.iter(_qn("hyperlink")):
        anchor = hl.get(_qn("anchor"))
        if not anchor:
            continue
        text = "".join(t.text or "" for t in hl.iter(_qn("t"))).strip() or "(no text)"
        links.append({"text": text, "anchor": anchor})

    return links, bookmarks


# ── Reporter ───────────────────────────────────────────────────────────────────

def _report(label: str, pdf_path: Path, docx_path: Path) -> None:
    sep = "=" * 72
    print(f"\n{sep}")
    print(f"  {label}")
    print(sep)

    if not pdf_path.exists():
        print(f"  ✗ PDF not found:  {pdf_path.name}")
        return
    if not docx_path.exists():
        print(f"  ✗ DOCX not found: {docx_path.name}")
        return

    pdf_links, pdf_dests = _pdf_links_and_dests(pdf_path)
    docx_links, docx_bk  = _docx_links_and_bookmarks(docx_path)

    pdf_link_dests  = {lk["dest"]   for lk in pdf_links}
    docx_link_dests = {lk["anchor"] for lk in docx_links}

    # ── 1. Destination sets ───────────────────────────────────────────────────
    print(f"\n  PDF  named destinations ({len(pdf_dests)}):  {sorted(pdf_dests)}")
    print(f"  DOCX bookmarks          ({len(docx_bk)}):  {sorted(docx_bk)}")

    only_pdf  = pdf_dests  - docx_bk
    only_docx = docx_bk   - pdf_dests

    if only_pdf:
        print(f"\n  ⚠  Destinations in PDF but NOT in DOCX ({len(only_pdf)}):")
        for d in sorted(only_pdf):
            print(f"       • {d}")
    if only_docx:
        print(f"\n  ℹ  Destinations in DOCX but NOT in PDF ({len(only_docx)}):")
        for d in sorted(only_docx):
            print(f"       • {d}")
    if not only_pdf and not only_docx:
        print("\n  ✅ Destination sets match perfectly between PDF and DOCX.")

    # ── 2. Link sources ───────────────────────────────────────────────────────
    print(f"\n  PDF  internal links ({len(pdf_links)}):")
    for lk in pdf_links:
        mark = "✅" if lk["dest"] in docx_bk else "❌"
        print(f"    {mark}  [{lk['text']:30s}]  →  #{lk['dest']}  (PDF p.{lk['page']})")

    only_pdf_links  = pdf_link_dests  - docx_link_dests
    only_docx_links = docx_link_dests - pdf_link_dests

    print(f"\n  DOCX internal links ({len(docx_links)}):")
    for lk in docx_links:
        mark = "✅" if lk["anchor"] in pdf_dests else "⚠ (no PDF dest)"
        print(f"    {mark}  [{lk['text']:30s}]  →  #{lk['anchor']}")

    # ── 3. Summary ────────────────────────────────────────────────────────────
    print(f"\n  {'─'*60}")
    if only_pdf_links:
        print(f"  ⚠  Links in PDF pointing to destinations missing in DOCX: {sorted(only_pdf_links)}")
    if only_docx_links:
        print(f"  ℹ  Links in DOCX pointing to destinations missing in PDF:  {sorted(only_docx_links)}")

    all_pdf_ok   = all(lk["dest"]   in docx_bk   for lk in pdf_links)
    all_docx_ok  = all(lk["anchor"] in pdf_dests  for lk in docx_links)

    if all_pdf_ok and all_docx_ok:
        print("  🎉 All links resolve in BOTH PDF and DOCX.")
    else:
        if not all_pdf_ok:
            broken = [lk for lk in pdf_links  if lk["dest"]   not in docx_bk]
            print(f"  ❌ {len(broken)} PDF link(s) resolve in PDF but have no DOCX bookmark.")
        if not all_docx_ok:
            broken = [lk for lk in docx_links if lk["anchor"] not in pdf_dests]
            print(f"  ❌ {len(broken)} DOCX link(s) resolve in DOCX but have no PDF named destination.")
    print()


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    for pair in PAIRS:
        _report(pair["label"], pair["pdf"], pair["docx"])
