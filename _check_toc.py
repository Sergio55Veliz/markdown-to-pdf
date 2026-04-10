import fitz

for name in [
    "scripts/pdf_generator/propuesta_nuevas_features.pdf",
    "scripts/pdf_generator/dashboard_riesgo_juridico.pdf",
]:
    doc = fitz.open(name)
    toc = doc.get_toc()
    print(f"\n=== {name.split('/')[-1]}  ({len(toc)} bookmarks) ===")
    for level, title, page in toc[:30]:
        indent = "  " * (level - 1)
        print(f"  {indent}[L{level}] p{page}  {title[:70]}")
    doc.close()
