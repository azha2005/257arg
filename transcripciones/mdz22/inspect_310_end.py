import fitz
import os

doc = fitz.open("1-p-1922.pdf")

# Check pages 310 to 346: what type of document is each page?
for p in range(310, len(doc)):
    txt = doc[p].get_text().strip()
    first_line = txt.splitlines()[0] if txt else "(EMPTY / SCANNED IMAGE)"
    print(f"Page {p+1}: {len(txt)} chars | {first_line[:50]}")
