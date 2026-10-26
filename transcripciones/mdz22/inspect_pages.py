import fitz

doc = fitz.open("1-p-1922.pdf")
print(f"Total pages: {len(doc)}")

for p in range(260, 310):
    txt = doc[p].get_text()
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    sample = " // ".join(lines[:3]) if lines else "(NO TEXT)"
    print(f"Page {p+1} ({len(txt)} chars): {sample[:120]}")
