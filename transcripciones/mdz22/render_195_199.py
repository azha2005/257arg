import fitz

doc = fitz.open("1-p-1922.pdf")

# Render page 195, 196, 197, 198, 199
for p in [195, 196, 197, 198, 199]:
    page = doc[p - 1]
    pix = page.get_pixmap(dpi=150)
    pix.save(f"page_images/page_{p:03d}.png")
    print(f"Rendered page {p}")
