import sys, json, collections, re
import numpy as np, pandas as pd
from wikicolors import FILES, run as wrun
import wikicolors
sys.path.insert(0, "../../.claude/skills/mapa-electoral-wikipedia-1999/scripts")
from match_territories import norm, nprov
from cmp2 import BASE, bkey, byprov
import difflib

MOD = {
    "1999": ("Elecciones_presidenciales_de_Argentina_de_1999_-_Resultados.png", "1999_presidente"),
    "2003": ("Elecciones_presidenciales_de_Argentina_de_2003_-_Resultados.png", "2003_presidente"),
    "2007": ("Elecciones_presidenciales_de_Argentina_de_2007_-_Resultados.png", "2007_presidente"),
    "2011": ("Elecciones_presidenciales_de_Argentina_de_2011_-_Resultados.png", "2011_presidente"),
    "2015": ("Elecciones_presidenciales_de_Argentina_de_2015_-_Resultados.png", "2015_presidente"),
    "2015b": ("Elecciones_presidenciales_de_Argentina_de_2015__Segunda_vuelta__-_Resultados.png", "2015_presidente_balotaje"),
    "2019": ("Elecciones_presidenciales_de_Argentina_de_2019_-_Resultados.png", "2019_presidente"),
    "2023": ("Elecciones_presidenciales_de_Argentina_de_2023_-_Resultados.png", "2023_presidente"),
    "2023b": ("Elecciones_presidenciales_de_Argentina_de_2023__Segunda_vuelta__-_Resultados.png", "2023_presidente_balotaje"),
}
SKIP = {"provincia", "unidad", "blancos", "nulos", "impugnados", "votantes", "electores", "positivos", "total", "fuente_id", "recurridos", "en_blanco", "nulo", "blanco"}


def match_name(p, n):
    p = nprov(p); n = norm(n)
    if (p, n) in bkey: return bkey[(p, n)]
    cands = {norm(u["name"]): u["i"] for u in byprov[p]}
    m = difflib.get_close_matches(n, list(cands), 1, 0.85)
    return cands[m[0]] if m else None


def main(key):
    png, xl = MOD[key]
    wikicolors.FILES[key] = png
    wc = wrun(key)
    json.dump(wc, open("wiki_colors_%s.json" % key, "w"))
    d = pd.read_excel("../../resultados_xlsx/por_eleccion/%s.xlsx" % xl, sheet_name="resultados")
    cols = [c for c in d.columns if str(c).lower() not in SKIP and not str(c).lower().startswith("unnamed")]
    rows = []; miss = 0
    for _, r in d.iterrows():
        if not isinstance(r["unidad"], str) or not isinstance(r["provincia"], str): continue
        if str(r["provincia"]).lower().startswith(("capital", "caba", "ciudad")): continue
        b = match_name(r["provincia"], r["unidad"])
        if b is None or b not in wc: miss += 1; continue
        vals = r[cols].astype(float).fillna(0)
        if vals.sum() <= 0: continue
        w = vals.idxmax(); sh = vals.max() / vals.sum()
        import matplotlib.colors as mc
        hh = mc.rgb_to_hsv(np.array(wc[b]["rgb"]) / 255.)
        hue = int(round(hh[0] * 360 / 4.0) * 4) % 360 if hh[1] > 0.2 else -1
        rows.append(dict(prov=r["provincia"], unidad=r["unidad"], base=b, ours=w, share=round(sh * 100, 1), wiki=str(hue), rgb=wc[b]["rgb"], wsh=wc[b]["share"]))
    # clase modal por candidato
    modal = {}
    ct = collections.defaultdict(collections.Counter)
    for r in rows: ct[r["ours"]][r["wiki"]] += 1
    for w, c in ct.items(): modal[w] = c.most_common(1)[0][0]
    ok = sum(1 for r in rows if modal[r["ours"]] == r["wiki"])
    print("== %s: unidades comparadas %d (sin pareja %d); concordancia %.1f%%" % (key, len(rows), miss, 100. * ok / len(rows)))
    for w, c in sorted(ct.items(), key=lambda x: -sum(x[1].values())):
        print("   %-45s n=%3d  %s" % (w[:45], sum(c.values()), dict(c)))
    json.dump(dict(rows=rows, modal=modal), open("cmpm_%s.json" % key, "w", encoding="utf8"), ensure_ascii=False)


if __name__ == "__main__":
    for k in sys.argv[1:]: main(k)
