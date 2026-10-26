import fitz

doc = fitz.open("1-p-1922.pdf")

for p in range(197, 205):
    txt = doc[p-1].get_text().strip()
    print(f"=== PAGE {p} ===")
    print(txt)
    print("\n" + "="*50 + "\n")
