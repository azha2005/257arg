"""Lee las tablas de senadores (escrutinio definitivo) de los artículos de la Wikipedia 2021, 2023 y 2025
(datos/wikileg/wleg<año>.txt): por provincia, cada fuerza con votos, % y bancas reales."""
import os, re, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def limpiar(s):
    s = re.sub(r"\{\{Lista desplegable.*", "", s)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"<[^>]+>|\{\{[^}]*\}\}|'''?", "", s)
    return s.strip(" |")

def leer(anio, sen=True):
    t = open(os.path.join(ROOT, f"datos/wikileg/wleg{anio}.txt"), encoding="utf8").read()
    out = {}
    for m in re.finditer(r'\|-\s*id="Sen([^"]+)"' if sen else r'\|-\s*id="(?!Sen)([^"]+)"', t):
        prov = m.group(1)
        fin = t.find("|}", m.end())
        nxt = t.find('id="', m.end())
        blq = t[m.end(): min(x for x in (fin, nxt) if x > 0)]
        filas = []
        for f in re.split(r"\n\|-", blq):
            if "align=left" not in f or "porcentaje" not in f: continue
            mn = re.search(r"align=\"?left\"?\s*\|(.*)", f)
            if not mn: continue
            nom = limpiar(mn.group(1))
            lp = [l for l in f.split(chr(10)) if "porcentaje" in l][0]
            pct = float(re.findall(r"(\d+(?:,\d+)?)\}\}", lp)[-1].replace(",", "."))
            ban = re.search(r"escaños\|hex=.*?\|(\d+)\|(\d+)\}\}", f)
            vot = re.search(r"\n\|\s*([\d.]+)\s*\n", f)
            filas.append({"fuerza": nom, "votos": int(vot.group(1).replace(".", "")) if vot else None,
                          "pct": pct, "bancas": int(ban.group(1)) if ban else 0})
        out[prov] = sorted(filas, key=lambda r: -r["pct"])
    return out

if __name__ == "__main__":
    todo = {f"sen{a}": leer(a) for a in (2021, 2023, 2025)}
    todo.update({f"dip{a}": leer(a, False) for a in (2021, 2023, 2025)})
    for a, d in todo.items():
        print(a, len(d))
        for p, f in d.items():
            print("  ", p, "|", " ; ".join(f"{r['fuerza']} {r['pct']} ({r['bancas']})" for r in f[:3]), "| suma bancas", sum(r["bancas"] for r in f))
    json.dump(todo, open(os.path.join(os.path.dirname(__file__), "tablas.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
