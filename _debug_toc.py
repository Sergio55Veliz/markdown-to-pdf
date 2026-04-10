import sys
sys.path.insert(0, ".")
from scripts.pdf_generator.generate_pdfs import _extract_headings_from_html
from pathlib import Path
import fitz

# Check extracted headings
html = Path("scripts/pdf_generator/dashboard_riesgo_juridico.html").read_text("utf-8")
headings = _extract_headings_from_html(html)
print(f"Extracted {len(headings)} headings from HTML:")
for lvl, txt in headings:
    print(f"  L{lvl}: {repr(txt[:70])}")

# Check what search_for finds for first 3 headings
doc = fitz.open("scripts/pdf_generator/dashboard_riesgo_juridico.pdf")
print(f"\nSearching in PDF ({doc.page_count} pages):")
for lvl, title in headings[:5]:
    search_text = title[:60]
    found = False
    for page_num in range(doc.page_count):
        hits = doc[page_num].search_for(search_text)
        if hits:
            print(f"  FOUND p{page_num+1}: {repr(title[:40])}")
            found = True
            break
    if not found:
        print(f"  NOT FOUND: {repr(title[:40])}")
        # Try shorter search
        for n in [20, 10, 5]:
            short = title[:n]
            for pn in range(doc.page_count):
                if doc[pn].search_for(short):
                    print(f"    -> partial ({n} chars) found on p{pn+1}: {repr(short)}")
                    break
doc.close()
