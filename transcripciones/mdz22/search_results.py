import fitz
import re

doc = fitz.open("1-p-1922.pdf")

print("Searching for vote / escrutinio / result indicators across all pages...")

results = []

for i, page in enumerate(doc):
    text = page.get_text()
    
    # Check for keywords indicating results/counts
    score = 0
    matches = []
    
    if re.search(r'\bvotos?\b', text, re.IGNORECASE):
        voto_count = len(re.findall(r'\bvotos?\b', text, re.IGNORECASE))
        matches.append(f"votos ({voto_count})")
        score += voto_count
        
    if re.search(r'\bescrutinio\b', text, re.IGNORECASE):
        matches.append("escrutinio")
        score += 5
        
    if re.search(r'\bsufragios?\b', text, re.IGNORECASE):
        matches.append("sufragio")
        score += 2
        
    if re.search(r'\btotal\b', text, re.IGNORECASE):
        matches.append("total")
        score += 1

    # Check for clusters of numbers (tables of votes)
    numbers = re.findall(r'\b\d{2,6}\b', text)
    if len(numbers) > 10:
        matches.append(f"{len(numbers)} numbers")
        score += len(numbers) // 5

    if score > 5:
        results.append((i + 1, score, matches, text[:200].replace('\n', ' ')))

results.sort(key=lambda x: x[1], reverse=True)

print(f"Top {len(results)} pages with electoral result indicators:")
for page_num, score, m, preview in results[:30]:
    print(f"Page {page_num:3d} (Score {score:3d}) [{', '.join(m)}]: {preview[:100]}")
