import fitz
import os

doc = fitz.open("1-p-1922.pdf")

os.makedirs("page_images", exist_ok=True)

pages_to_render = [89, 90, 91, 92, 126, 127, 128, 129, 130]

for p_num in pages_to_render:
    page = doc[p_num - 1]
    pix = page.get_pixmap(dpi=150)
    img_path = f"page_images/page_{p_num:03d}.png"
    pix.save(img_path)
    print(f"Rendered page {p_num} -> {img_path} ({pix.width}x{pix.height})")
