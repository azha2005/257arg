import fitz

doc = fitz.open("1-p-1922.pdf")

# Let's inspect page 265, 267, 269, etc.
for p in [265, 267, 269, 271, 273, 275, 281, 293, 315, 321, 335, 337, 339, 341, 345]:
    txt = doc[p-1].get_text().strip()
    print(f"=== PAGE {p} ===")
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    print("\n".join(lines[:6]))
    print("-" * 40)
