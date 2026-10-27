"""Auditoria de las matrices de transferencias: marca las filas y celdas que no se pueden creer.
    python transferencias/auditar.py            # todos los pares -> transferencias/AUDITORIA.md
Criterios por fila de origen (sobre transferencias/<par>/):
  - peso: % del padron que representa la categoria de origen (las de menos de 5 % casi no mueven el ajuste);
  - dif_calvo: maxima diferencia en puntos entre la variante principal y la de Calvo (una sola matriz nacional);
  - ancho_ic: maximo ancho del intervalo bootstrap 5-95, en puntos.
Una fila es «no identificada» si difiere de Calvo en mas de 30 puntos en alguna celda, o en mas de 20 si pesa menos de 5 %.
Matriz poco informativa: si las filas grandes (partidos con 5 % o más del padrón) quedan casi iguales al resultado promedio
del destino (separación media menor a SEPARACION_MIN puntos), el origen no predice el destino y la matriz solo repite el
promedio: todas las filas «se reparten igual» por falta de señal, no porque los votantes lo hayan hecho. Las dos variantes
coinciden en ese caso, así que el criterio de Calvo no lo detecta.
Por provincia: una celda es imposible si manda a un destino mas votos que los que ese destino saco en la provincia."""
import os, json, glob
import pandas as pd
NO_PARTIDO = ("No votó", "Blanco y nulo", "Otros")
SEPARACION_MIN = 25     # los pares que se leen bien están en 29,5 o más; 1930 -> 1946 da 9,5
HERE = os.path.dirname(os.path.abspath(__file__))
PARES = ["2009_2011", "2011_2023", "2013_2025", "2019_2023", "2019_2025", "2021_2025", "2023_2025", "2019p_2023p", "2011p_2023p", "2023p_2023b", "2019p_2023b", "2011p_2023b", "1954p_1958p", "1954d_1965d", "2003p_2005", "2003p_2007p", "2003p_2009", "2009_2013", "2011p_2015p", "2015p_2015b", "2011p_2015b", "1958d_1962d", "1930d_1946d", "1937d_1946d", "1940d_1946d", "1999pc_2003pc", "1991c_1995c", "1999pe_2003pe"]


PARES.append("2013_2017")
PARES.extend(["2015p_2023p", "2015p_2023b", "2015b_2023p", "2015b_2023b"])
PARES.extend(["2013_2015p", "2013_2015b", "2009_2015p", "2009_2015b"])
PARES.extend(["2017_2019p", "2017_2019", "2015p_2019p", "2015b_2019p"])
PARES.extend(['1989p_1995p', '1989d_1994c'])
PARES.append('1985d_1987d')
PARES.extend(['1983p_1989p','1987d_1989p','1985d_1989p'])
PARES.append('1989p_1997d')
PARES.extend(['1995p_1997d','1995p_1999p','1983p_1985d'])
PARES.append('1914d_1916d')
PARES.extend(['2023pp_2025', '2023p_2025', '2023b_2025'])   # presidente 2023 (PASO, general, balotaje) -> diputados 2025
PARES.extend(['2015pp_2025', '2015p_2025', '2015b_2025'])
PARES.append('2017_2025')
PARES.append('brasil_2026p_2026b')


def pct(M):
    return M.div(M.sum(1), axis=0) * 100


def auditar(par):
    d = os.path.join(HERE, par)
    M = pd.read_csv(os.path.join(d, "matriz_votos.csv"), index_col=0, encoding="utf-8-sig")
    C = pd.read_csv(os.path.join(d, "calvo_nacional.csv"), index_col=0, encoding="utf-8-sig")
    iv = pd.read_csv(os.path.join(d, "intervalos.csv"), encoding="utf-8-sig")
    pr = pd.read_csv(os.path.join(d, "por_provincia.csv"), encoding="utf-8-sig", dtype={"distrito": str})
    ctl = json.load(open(os.path.join(d, "control.json"), encoding="utf8"))
    P, Q = pct(M), pct(C)
    marg = M.sum(0) / M.values.sum() * 100
    sep_f = 0.5 * (P - marg).abs().sum(1); sep_c = 0.5 * (Q - marg).abs().sum(1)
    iv["ancho"] = (iv.p95 - iv.p5) / iv.origen.map(M.sum(1)) * 100
    filas = []
    for r in M.index:
        dif = (P.loc[r] - Q.loc[r]).abs()
        peso = M.loc[r].sum() / M.values.sum() * 100
        filas.append(dict(origen=r, peso=round(peso, 1), dif_calvo=round(dif.max(), 1), celda=dif.idxmax(),
                          principal=round(P.loc[r, dif.idxmax()], 1), calvo=round(Q.loc[r, dif.idxmax()], 1),
                          ancho_ic=round(iv[iv.origen == r].ancho.max(), 1),
                          sep=round(sep_f[r], 1), sep_calvo=round(sep_c[r], 1),
                          cerca_promedio=bool(peso >= 5 and r not in NO_PARTIDO and sep_f[r] < SEPARACION_MIN),
                          no_identificada=bool(dif.max() > 30 or (peso < 5 and dif.max() > 20))))
    # Criterios adicionales que trae el par en control.json (Brasil 2026: escala territorial y celdas en el borde).
    extra = ctl.get("auditoria_extra", {})
    for f in filas:
        e = extra.get(f["origen"], {})
        f["no_identificada"] = f["no_identificada"] or bool(e.get("no_identificada"))
        f["sensible"] = bool(e.get("sensible")) and not f["no_identificada"]
        f["borde"] = e.get("borde", [])
    pw = M.sum(1) / M.values.sum()
    big = [r for r in M.index if pw[r] >= .05 and r not in NO_PARTIDO]
    sep = float((sep_f[big] * pw[big]).sum() / pw[big].sum()) if big else float("nan")
    # por provincia: votos estimados hacia cada destino contra los reales (marginal de destino de la provincia)
    real = ctl.get("marginal_destino_provincia")
    imposibles = []
    if real:
        est = pr.groupby(["distrito", "destino"]).votos.sum()
        for (dd, c), v in est.items():
            rv = real.get(dd, {}).get(c)
            if rv is not None and v > 1.25 * rv + 2000:
                imposibles.append(dict(distrito=dd, destino=c, estimado=int(v), real=int(rv)))
    return dict(par=par, separacion=round(sep, 1), poco_informativa=bool(sep < SEPARACION_MIN), lam=ctl.get("lambda"), cv=ctl.get("validacion_cruzada_pp"), filas=filas, imposibles=imposibles)


def main():
    out = ["# Auditoría de las transferencias", "",
           "Generado por `auditar.py`. «Peso»: % del padrón de la categoría de origen. «Dif. Calvo»: máxima diferencia, en puntos, "
           "entre la variante principal y la de Calvo (una sola matriz nacional), con la celda donde ocurre. «IC»: máximo ancho del "
           "intervalo bootstrap 5–95. Una fila **no identificada** (más de 30 puntos de diferencia entre variantes en alguna celda, o más de 20 "
           "si pesa menos de 5 % del padrón) no se puede leer: los datos no alcanzan para saber adónde fueron esos votantes.", "",
           "«Separación»: cuánto se aparta en promedio cada fila grande (partidos con 5 %% o más del padrón) del resultado total del destino, "
           "en puntos (media ponderada de ½·Σ|fila − promedio|). Si es menor a %d, la matriz es **poco informativa**: el voto de origen casi no "
           "predice el de destino y todas las filas se parecen al promedio por falta de señal, no porque los votantes se hayan repartido igual. "
           "Las dos variantes coinciden en ese caso, así que el criterio de Calvo no lo detecta. «Sep.» por fila es la misma medida para esa "
           "fila (principal / Calvo); una fila de 5 %% o más del padrón con separación menor a %d se marca **cerca del promedio** (en el sankey, †): "
           "puede ser un electorado que de verdad se repartió como el total, o falta de señal para esa fila; si la variante de Calvo también "
           "queda cerca, lo segundo es más probable." % (SEPARACION_MIN, SEPARACION_MIN), ""]
    for par in PARES:
        if not os.path.exists(os.path.join(HERE, par, "control.json")): continue
        a = auditar(par)
        out += ["## " + par.replace("brasil_", "Brasil ").replace("_", " → "), "", "Penalización elegida: %s; error de validación cruzada (pp): %s" % (a["lam"], a["cv"]), "",
                "Separación de las filas: %s puntos%s" % (a["separacion"], " — **matriz poco informativa**: las filas repiten el promedio" if a["poco_informativa"] else ""), "",
                "| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |", "|---|---|---|---|---|---|---|---|---|"]
        for f in a["filas"]:
            marca = [m for m, c in (("**no identificada**", f["no_identificada"]), ("**cerca del promedio**", f["cerca_promedio"]),
                                    ("sensible a la escala o especificación", f.get("sensible"))) if c]
            if f.get("borde"): marca.append("en el borde (<0,5 %): " + ", ".join(f["borde"]))
            out.append("| %s | %s | %s | %s | %s | %s | %s | %s / %s | %s |" % (f["origen"], f["peso"], f["dif_calvo"], f["celda"], f["principal"],
                       f["calvo"], f["ancho_ic"], f["sep"], f["sep_calvo"], ", ".join(marca)))
        if a["imposibles"]:
            out += ["", "Provincias donde un destino recibe más del 125 % de sus votos reales:", ""]
            out += ["- %s, %s: %s estimados contra %s reales" % (i["distrito"], i["destino"], i["estimado"], i["real"]) for i in a["imposibles"]]
        out.append("")
    open(os.path.join(HERE, "AUDITORIA.md"), "w", encoding="utf8").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
