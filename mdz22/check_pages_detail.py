import fitz

doc = fitz.open("1-p-1922.pdf")

for p in range(320, 336):
    txt = doc[p].get_text()
    print(f"Page {p+1}: {len(txt)} chars | {repr(txt[:60])}")
