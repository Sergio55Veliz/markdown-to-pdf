"""
PDF outline (bookmarks) via PyMuPDF.
"""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

try:
    import fitz
    _FITZ_AVAILABLE = True
except ImportError:
    _FITZ_AVAILABLE = False


def extract_headings_from_html(html_content: str) -> list[tuple[int, str]]:
    """Extract ``(level, text)`` heading pairs from an HTML string."""
    soup = BeautifulSoup(html_content, "lxml")
    headings: list[tuple[int, str]] = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        level = int(tag.name[1])
        text = tag.get_text(" ", strip=True)
        if text:
            headings.append((level, text))
    return headings


def add_pdf_outline(pdf_path: Path, headings: list[tuple[int, str]]) -> None:
    """Inject a bookmark tree into an existing PDF using PyMuPDF."""
    if not _FITZ_AVAILABLE or not headings:
        return
    doc = fitz.open(str(pdf_path))
    toc: list[list] = []
    for level, title in headings:
        search_text = title[:60]
        for page_num in range(doc.page_count):
            if doc[page_num].search_for(search_text):
                toc.append([level, title, page_num + 1])
                break

    if toc:
        normalized: list[list] = [toc[0][:]]
        for entry in toc[1:]:
            lvl, ttl, pg = entry
            prev_lvl = normalized[-1][0]
            if lvl > prev_lvl + 1:
                lvl = prev_lvl + 1
            normalized.append([lvl, ttl, pg])

        doc.set_toc(normalized)
        tmp = pdf_path.with_suffix(".tmp.pdf")
        doc.save(str(tmp))
        doc.close()
        tmp.replace(pdf_path)
    else:
        doc.close()
