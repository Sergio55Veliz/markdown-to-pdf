import fitz

for pdf_name in [
    "scripts/pdf_generator/propuesta_nuevas_features.pdf",
    "scripts/pdf_generator/propuesta_modelo.pdf",
]:
    doc = fitz.open(pdf_name)
    print(f"\n=== {pdf_name} ({doc.page_count} pages) ===")
    fonts = {}
    for page in doc:
        for f in page.get_fonts(full=True):
            # f: (xref, ext, type, basefont, name, encoding, referencer)
            key = f[3]  # basefont
            if key not in fonts:
                fonts[key] = f[2]  # type
    for name, ftype in sorted(fonts.items()):
        print(f"  {ftype:12s}  {name}")
