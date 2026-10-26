import json, csv, collections, sys
import pandas as pd
from cmp2 import nn, nprov, norm, MANUAL
sys.path.insert(0, "../../.claude/skills/mapa-electoral-wikipedia-1999/scripts")
NAME = {"red": "rojo", "blue": "azul", "teal": "turquesa", "purple": "violeta", "magenta": "magenta", "amber": "ámbar", "green": "verde"}
out = {}
for y, (pa, pb, ca, cb) in ((1983, ("ucr", "pj", "red", "blue")), (1989, ("ucr", "frejupo", "red", "blue")), (1995, (None, None, None, None))):
    rows = json.load(open("cmp2_%d.json" % y, encoding="utf8"))
    dip = {}
    if y in (1983, 1989):
        d = pd.read_csv("../../datos/base8399/ernesto/%d_diputados/dpto_partidos.csv" % y); d = d[d.tipo_fila == "agrupacion"]
        g = d.groupby(["provincia", "departamento", "codigo_partido"]).votos.sum().unstack(fill_value=0)
        for (p, dep), r in g.iterrows():
            if pa in r and pb in r: dip[(nprov(p), norm(dep))] = ca if r[pa] > r[pb] else cb
    ds = json.load(open("../../mapas/mapa%d/dataset_%d.json" % (y, y), encoding="utf8"))
    ofile = "informe/discrepancias_%d.csv" % y
    n = 0
    with open(ofile, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["provincia", "unidad", "ganador_nuestro", "nuestro_%", "color_wikipedia", "ganador_diputados_misma_base", "nuestras_3_primeras_listas"])
        for r in sorted(rows, key=lambda r: (r["prov"], r["name"])):
            if r["ours"] == r["wiki"]: continue
            k = (nprov(r["prov"]), nn(r["name"])); k = (k[0], MANUAL.get(k, k[1]))
            dw = NAME.get(dip.get((nprov(r["prov"]), norm(r["name"]))), "") if dip else ""
            w.writerow([r["prov"], r["name"], r["ours_w"], r["q"], NAME.get(r["wiki"], r["wiki"]), dw, "; ".join("%s %.1f%%" % (l[0][2:], l[2]) for l in r["lines"][:3])]); n += 1
    print(y, n, "filas ->", ofile)
# modernas
rows = json.load(open("cmpm_all.json", encoding="utf8"))
with open("informe/discrepancias_2003_2023.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["eleccion", "provincia", "unidad", "ganador_nuestros_datos", "%_del_ganador", "tono_wikipedia(grados)", "tono_esperado"])
    for r in rows:
        if not r["ok"]: w.writerow([r["eleccion"], r["prov"], r["unidad"], r["ours"], r["share"], r["wiki"], r["modal"]])
