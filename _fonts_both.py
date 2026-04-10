import fitz

for name in [
    "scripts/pdf_generator/propuesta_nuevas_features.pdf",
    "scripts/pdf_generator/dashboard_riesgo_juridico.pdf",
]:
    doc = fitz.open(name)
    fonts = {}
    for page in doc:
        for f in page.get_fonts(full=True):
            key = f[3]
            fonts[key] = f[2]
    print(f"\n=== {name.split('/')[-1]} ===")
    for n, t in sorted(fonts.items()):
        print(f"  {t:12s}  {n}")
    doc.close()
