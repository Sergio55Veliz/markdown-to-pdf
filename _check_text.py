import fitz

doc = fitz.open("scripts/pdf_generator/dashboard_riesgo_juridico.pdf")
print("Pages:", doc.page_count)

# Dump text from first 3 pages
for i in range(min(3, doc.page_count)):
    txt = doc[i].get_text()
    print(f"\n--- page {i+1} ---")
    print(repr(txt[:400]))

doc.close()
