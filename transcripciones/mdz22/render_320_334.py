import fitz
import os

doc = fitz.open("1-p-1922.pdf")

os.makedirs("page_images", exist_ok=True)

for p in range(320, 335):
    page = doc[p - 1]
    pix = page.get_pixmap(dpi=150)
    pix.save(f"page_images/page_{p:03d}.png")
    print(f"Rendered page {p}")
