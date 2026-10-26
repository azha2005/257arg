import fitz

doc = fitz.open("1-p-1922.pdf")

# Check pages 337 to 346
for p in range(336, len(doc)):
    txt = doc[p].get_text().strip()
    print(f"Page {p+1} ({len(txt)} chars):")
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if lines:
        print("  ", lines[:3])
