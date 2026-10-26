import fitz
import re

doc = fitz.open("1-p-1922.pdf")

party_terms = ["lencin", "rubilar", "alvear", "democrata", "liberal", "socialista", "correa llano", "calzolari", "gomez", "ocupato", "votos"]

found_lines = []

for p_no in range(len(doc)):
    txt = doc[p_no].get_text()
    for line in txt.splitlines():
        line_clean = line.strip()
        # look for lines with numbers and political party or candidates
        if any(pt in line_clean.lower() for pt in party_terms):
            nums = re.findall(r'\b\d+\b', line_clean)
            if nums:
                found_lines.append((p_no + 1, line_clean))

print(f"Total matching lines found: {len(found_lines)}")
for p, l in found_lines[:50]:
    print(f"P.{p:3d}: {l}")
