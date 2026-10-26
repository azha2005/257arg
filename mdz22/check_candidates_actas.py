import fitz
import re

doc = fitz.open("1-p-1922.pdf")

# Let's inspect what is in pages 131 to 185
# Check if party votes or candidate votes are mentioned anywhere in this range
found_candidates = []
candidate_names = ["alvear", "gonzalez", "lencinas", "correa llano", "calzolari", "gomez", "ocupato", "rubilar", "obredor", "liberal", "democrata", "socialista"]

for p in range(130, 185):
    txt = doc[p].get_text()
    for c in candidate_names:
        if c in txt.lower():
            found_candidates.append((p + 1, c))

print("Candidate mentions in pages 131-185:", found_candidates)
