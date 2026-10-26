import fitz

doc = fitz.open("1-p-1922.pdf")

for p in [133, 135, 137, 139, 141, 143, 145, 147]:
    txt = doc[p-1].get_text()
    print(f"=== PAGE {p} ===")
    print(txt)
    print("\n" + "="*50 + "\n")
