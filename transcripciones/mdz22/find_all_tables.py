import fitz
import re

doc = fitz.open("1-p-1922.pdf")

print("Checking all pages for table structure...")

possible_tables = []

for i, page in enumerate(doc):
    text = page.get_text()
    # Check if text contains "MESA" or "VOTANTES"
    if "mesa" in text.lower() and "votante" in text.lower():
        possible_tables.append((i + 1, "contains mesa & votante", len(text.strip())))
    elif "votantes" in text.lower() and re.search(r'\b\d+\s+\d+\b', text):
        possible_tables.append((i + 1, "contains votantes & number pairs", len(text.strip())))

print(f"Total potential table pages: {len(possible_tables)}")
for p, reason, length in possible_tables:
    print(f"Page {p:3d} ({length} chars): {reason}")
