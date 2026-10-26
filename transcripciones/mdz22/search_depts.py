import fitz

doc = fitz.open("1-p-1922.pdf")

# Search for "Junin", "Santa Rosa", "La Paz", "Tunuyan", "San Carlos" together with "Mesa" or numbers
targets = ["junin", "santa rosa", "la paz", "tunuyan", "tupungato", "san carlos"]

matches = []
for p in range(len(doc)):
    txt = doc[p].get_text().lower()
    for t in targets:
        if t in txt:
            matches.append((p + 1, t))

print(f"Total target matches: {len(matches)}")
for p, t in matches:
    print(f"Page {p:3d}: mentions {t}")
