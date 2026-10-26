import fitz
import os

doc = fitz.open("1-p-1922.pdf")

# Check pages 325 to 336: let's see which pages are part of the table
print("=== Checking pages 320 to 336 ===")
for p in range(324, 337):
    txt = doc[p].get_text().strip()
    print(f"Page {p+1}: {len(txt)} chars")
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if lines:
        print("   First 3 lines:", lines[:3])
