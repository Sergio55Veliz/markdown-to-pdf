"""Measure actual rendered font sizes from both PDFs to detect scaling differences."""
import fitz

for name in [
    "scripts/pdf_generator/propuesta_nuevas_features.pdf",
    "scripts/pdf_generator/dashboard_riesgo_juridico.pdf",
]:
    doc = fitz.open(name)
    page = doc[0]
    data = page.get_text("dict")
    sizes = {}
    for block in data["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                sz = round(span["size"], 2)
                text = span["text"].strip()[:40]
                if text and sz not in sizes:
                    sizes[sz] = text
    print(f"\n=== {name.split('/')[-1]} — unique font sizes on page 1 ===")
    for sz in sorted(sizes):
        print(f"  {sz:6.2f}pt  {repr(sizes[sz])}")
    doc.close()
