import sys
sys.path.insert(0, ".")
from scripts.pdf_generator.generate_pdfs import _extract_headings_from_html
from pathlib import Path
import fitz

html = Path("scripts/pdf_generator/dashboard_riesgo_juridico.html").read_text("utf-8")
headings = _extract_headings_from_html(html)
print(f"Headings found: {len(headings)}")

pdf_path = Path("scripts/pdf_generator/dashboard_riesgo_juridico.pdf")
doc = fitz.open(str(pdf_path))
toc = []
not_found = []
for level, title in headings:
    search_text = title[:60]
    for page_num in range(doc.page_count):
        if doc[page_num].search_for(search_text):
            toc.append([level, title, page_num + 1])
            break
    else:
        not_found.append(title[:60])

print(f"TOC entries: {len(toc)}, not found: {len(not_found)}")
if not_found:
    print("Not found:")
    for t in not_found[:10]:
        print(f"  {repr(t)}")

doc.set_toc(toc)
tmp = pdf_path.with_suffix(".tmp.pdf")
doc.save(str(tmp))
print(f"Saved to {tmp} ({tmp.stat().st_size} bytes)")
doc.close()

# Verify tmp has TOC
doc2 = fitz.open(str(tmp))
toc2 = doc2.get_toc()
print(f"TOC in tmp file: {len(toc2)} entries")
for lvl, title, pg in toc2[:5]:
    print(f"  L{lvl} p{pg}: {title[:50]}")
doc2.close()

tmp.replace(pdf_path)
print("Done — replaced original")
