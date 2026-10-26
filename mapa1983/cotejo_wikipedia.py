"""Cotejo de los totales provinciales de la base de Ernesto con la tabla «Resultados por distrito» de Wikipedia (w1983.txt)."""
import re, sys, os, csv, collections
HERE = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(HERE, "w1983.txt"), encoding="utf8").read()
i0 = txt.index("=== Resultados por distrito ==="); i1 = txt.index("==Resultados del Colegio Electoral==")
sec = txt[i0:i1]
rows = [r for r in re.split(r"\n\|-", sec) if "Provincia de" in r or "Capital Federal" in r or re.search(r"\|\s*\[\[", r)]
W = {}
for r in rows:
    cells = [c.strip() for c in re.findall(r"^\|\s*(.*)$", r, flags=re.M)]
    if len(cells) < 18: continue
    name = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", cells[0]).strip("' ")
    def num(s):
        s = re.sub(r"\{\{orden\|\d+\|([\d.]+)\}\}", r"\1", s).replace("'", "")
        s = s.replace(".", "")
        return int(s) if s.isdigit() else None
    W[name] = dict(UCR=num(cells[2]), PJ=num(cells[5]), PI=num(cells[8]), MID=num(cells[11]), OTROS=num(cells[14]), BN=num(cells[16]), E=num(cells[18]) if len(cells) > 18 else None)
print(len(W), list(W)[:30])
import pickle
pickle.dump(W, open(os.path.join(HERE, "wiki_distritos.pkl"), "wb"))
