import re,sys
y=sys.argv[1]
t=open(f"mapas/mapa{y}/w{y}.txt",encoding="utf8").read()
a=t.index("== Resultados ==")
b=t.index("== Resultados por provincia ==") if "== Resultados por provincia ==" in t else len(t)
seg=t[a:b]
rows=seg.split("\n|-")
for r in rows:
    ls=[l.strip() for l in r.strip().split("\n") if l.strip()]
    cells=[l for l in ls if l.startswith("|") or l.startswith("!")]
    txt=[re.sub(r"\{\{[^{}]*\}\}|\[\[(?:[^|\]]*\|)?([^\]]*)\]\]",lambda m:m.group(1) or "",c.lstrip("|! ")) for c in cells]
    nums=[x for x in txt if re.fullmatch(r"[\d\.]{4,}",x.strip())]
    name=[x for x in txt if re.search(r"[A-Za-zÁ-ú]{3}",x) and not x.startswith("bgcolor") and "style" not in x and "align=left" not in x or x.startswith("align=left")]
    if nums: print(" | ".join(x.replace("align=left|","").strip()[:70] for x in txt if x.strip() and not x.startswith("bgcolor") and "style=" not in x)[:230])
