import fitz

doc = fitz.open("1-p-1922.pdf")

for p in range(88, 134):
    txt = doc[p].get_text().strip()
    if len(txt) > 50:
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        print(f"=== Page {p+1} ({len(txt)} chars) ===")
        print("\n".join(lines[:8]))
        print("-" * 30)
