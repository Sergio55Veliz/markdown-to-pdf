"""Compare font, size, and color info between model PDF and our generated PDF.
Also renders first pages as PNG images for visual comparison."""
import fitz
import sys

target = sys.argv[1] if len(sys.argv) > 1 else 'scripts/pdf_generator/propuesta_modelo.pdf'
doc = fitz.open(target)
print(f'File: {target}')
print('Pages:', doc.page_count)

# Render first page as image for visual comparison
page0 = doc[0]
mat = fitz.Matrix(2.0, 2.0)  # 2x zoom = 144 DPI
pix = page0.get_pixmap(matrix=mat)
img_path = target.replace('.pdf', '_page1.png')
pix.save(img_path)
print(f'First page image saved: {img_path}')
doc.close()
