import fitz

doc = fitz.open("1-p-1922.pdf")

# Let's inspect pages 180 to 260
for p in range(180, 205):
    txt = doc[p].get_text().strip()
    if txt:
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        print(f"=== Page {p+1} ===")
        print("\n".join(lines[:10]))
        print("-" * 30)
