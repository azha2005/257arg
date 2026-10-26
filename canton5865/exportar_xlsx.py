"""Cantón 1958/1962/1965 corregido -> xlsx_resultados/por_eleccion/ (reemplaza la salida de scratch/compilar_canton.py, que no tenía correcciones).

    python canton5865/exportar_xlsx.py

Por elección: <año>_<cargo>_canton.xlsx (hojas totales/varones/mujeres, bloque de Wikipedia en «bloques», correcciones aplicadas)
y <año>_<cargo>_<categoría>.csv; además canton_1958_1962_1965_consolidado.xlsx con todo.
"""
import os, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import pandas as pd
from datos import cargar_todo, unidades
from sospechas import kinds
import mapeo, wikiprov

OUT = os.path.join(H, "..", "xlsx_resultados", "por_eleccion")
CATS = {"T": "totales", "V": "varones", "M": "mujeres"}
CARGO = {"P": "presidente", "D": "diputados"}
W = {1962: wikiprov.parse("w1962.txt", "== Resultados por provincia"), 1965: wikiprov.parse("w1965.txt", "== Resultados por distrito")}


def hoja(T, a, c, cat):
    rows, order = [], []
    for (a2, c2, p, k), t in T.items():
        if (a2, c2, k) != (a, c, cat): continue
        ins, vot, rest = kinds(t["cols"])
        for n in [t["cols"][x] for x in rest]:
            if n not in order: order.append(n)
        for u, r in t["rows"].items():
            d = {"provincia": p, "unidad": u, "categoria": CATS[cat], "inscriptos": r.get(ins) if ins else None, "votantes": r.get(vot) if vot else None}
            for x in rest:
                if isinstance(r.get(x), int): d[t["cols"][x]] = d.get(t["cols"][x], 0) + r[x]
            d["imputado"] = "sí" if u in t.get("imput", ()) else ""
            d["paginas_pdf"] = ", ".join(str(x) for x in t["pages"])
            rows.append(d)
    tail = [n for n in order if mapeo.es_blanco(n) or mapeo.es_nulo(n)]
    cols = ["provincia", "unidad", "categoria", "inscriptos", "votantes"] + [n for n in order if n not in tail] + tail + ["imputado", "paginas_pdf"]
    return pd.DataFrame(rows, columns=cols)


def bloques(T, a):
    out = []
    for (p, u), d in unidades(T, a).items():
        for n, v, b in d["parties"]:
            f = mapeo.fila(a, p, n, W.get(a, {}).get(p, [])) if a != 1958 else mapeo.fila58(p, n)
            out.append(dict(provincia=p, unidad=u, partido_canton=n, fila_wikipedia=f, bloque=b or "otros", votos=v))
    return pd.DataFrame(out)


if __name__ == "__main__":
    T, LOG = cargar_todo()
    corr = pd.DataFrame(LOG, columns=["anio", "cargo", "provincia", "categoria", "unidad", "columna", "transcripto", "corregido", "motivo"])
    elecs = sorted({(a, c) for (a, c, _, _) in T})
    with pd.ExcelWriter(os.path.join(OUT, "canton_1958_1962_1965_consolidado.xlsx"), engine="openpyxl") as M:
        for a, c in elecs:
            key = "%d_%s" % (a, CARGO[c])
            with pd.ExcelWriter(os.path.join(OUT, key + "_canton.xlsx"), engine="openpyxl") as E:
                for cat in "TVM":
                    df = hoja(T, a, c, cat)
                    if df.empty: continue
                    df.to_excel(E, sheet_name=CATS[cat], index=False); df.to_excel(M, sheet_name=(key + "_" + CATS[cat])[:31], index=False)
                    df.to_csv(os.path.join(OUT, "%s_%s.csv" % (key, CATS[cat])), index=False, encoding="utf-8-sig")
                    print(key, CATS[cat], df.shape)
                if (a == 1958 and c == "P") or (a in (1962, 1965)):
                    bloques(T, a).to_excel(E, sheet_name="bloques", index=False)
                corr[(corr.anio == a) & (corr.cargo == c)].to_excel(E, sheet_name="correcciones", index=False)
        corr.to_excel(M, sheet_name="correcciones", index=False)
    print("correcciones:", len(corr))
