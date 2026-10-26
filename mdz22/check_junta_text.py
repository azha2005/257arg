import fitz

doc = fitz.open("1-p-1922.pdf")

# Search for what happened during the session of the Junta
# Let's inspect page 131, 133, 135, 137, and pages 180-205 in detail
for p in [133, 135, 137, 181, 183, 185, 187, 189, 191, 193, 195, 197, 199, 201]:
    txt = doc[p-1].get_text().strip()
    print(f"=== PAGE {p} ===")
    print(txt[:1000])
    print("\n" + "="*50 + "\n")
