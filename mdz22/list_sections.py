import fitz
import re

doc = fitz.open("1-p-1922.pdf")

print("Total pages:", len(doc))

# Let's see all pages with substantial text (> 500 chars)
substantial_pages = []
for i in range(len(doc)):
    text = doc[i].get_text()
    if len(text.strip()) > 300:
        first_line = ""
        for line in text.splitlines():
            line = line.strip()
            if len(line) > 10:
                first_line = line
                break
        substantial_pages.append((i + 1, len(text.strip()), first_line))

print(f"Substantial pages count: {len(substantial_pages)}")
for p, length, line in substantial_pages:
    print(f"P.{p:3d} ({length:4d} ch): {line[:90]}")
