import fitz

doc = fitz.open("1-p-1922.pdf")

for p in range(134, 180):
    txt = doc[p].get_text()
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    first_few = " \n ".join(lines[:8])
    print(f"=== Page {p+1} ({len(txt)} chars) ===")
    print(first_few)
    print("-" * 40)
