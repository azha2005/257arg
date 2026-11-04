"""Backtest de la proyeccion de la Knesset durante el conteo (modelo.py) con las elecciones de 2019 a 2022.
    python -X utf8 proyeccion/israel/backtest.py
Para cada par (origen -> destino), orden de llegada (azar, geo) y corte del conteo (% de urnas comunes; el doble
sobre se proyecta), se compara con el resultado oficial: bancas por lista, bancas del bloque de Netanyahu, desenlace
(Netanyahu >= 61, oposicion judia >= 61 o ninguno) y si la banda del 90 % del bloque contiene el real. Referencia:
el conteo parcial pasado a bancas tal cual.
Salida: proyeccion/israel/backtest.csv y RESUMEN_BACKTEST.md."""
import os
import numpy as np
import pandas as pd

import datos as dt
import modelo as md

HERE = os.path.dirname(os.path.abspath(__file__))
PARES = [(21, 22), (22, 23), (23, 24), (24, 25)]
CORTES = [0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0]
REPS = 5
NBOOT = 200


def main():
    rows = []
    for o, de in PARES:
        st = md.preparar(o, de)
        ac = dt.ACUERDOS.get(de, ())
        v, p = dt.cargar(de)
        real = dt.bancas(v[p].sum().to_dict(), ac)
        rs = np.array([[real[x] for x in st["listas"]]])
        rb = md.bloques(st, rs, dt.BLOQUE[de])
        rres = md.resultado(rb["bibi"], rb["oposicion"])[0]
        ri = np.array([real[x] > 0 for x in st["listas"]])
        Yv = st["Y"] * st["w"][:, None]
        for kind in ("azar", "geo"):
            for rep in range(REPS):
                rng = np.random.default_rng(1000 * o + rep + (0 if kind == "azar" else 500))
                ordn = md.orden(st, kind, rng)
                for f in CORTES:
                    cnt = ordn[:max(1, int(round(f * len(ordn))))]
                    s, _ = md.proyectar(st, cnt, rng, NBOOT, ac)
                    b = md.bloques(st, s, dt.BLOQUE[de])
                    res = md.resultado(b["bibi"], b["oposicion"])
                    # conteo parcial tal cual
                    vc = Yv[cnt].sum(0)
                    sc = dt.bancas({st["dcols"][i]: vc[i] for i in range(len(st["dcols"]) - 1)}, ac)
                    sc = np.array([[sc[x] for x in st["listas"]]])
                    bc = md.bloques(st, sc, dt.BLOQUE[de])
                    lo, hi = np.percentile(b["bibi"][1:], [5, 95])
                    rows.append(dict(par="%d→%d" % (o, de), orden=kind, rep=rep, corte=f,
                                     err_bibi=b["bibi"][0] - rb["bibi"][0], err_bibi_conteo=bc["bibi"][0] - rb["bibi"][0],
                                     mae_listas=np.abs(s[0] - rs[0]).mean(), mae_conteo=np.abs(sc[0] - rs[0]).mean(),
                                     umbral_ok=((s[0] > 0) == ri).mean(), cubre90=lo <= rb["bibi"][0] <= hi,
                                     ancho90=hi - lo, desenlace_ok=res[0] == rres, p_real=(res[1:] == rres).mean(),
                                     desenlace_conteo_ok=md.resultado(bc["bibi"], bc["oposicion"])[0] == rres))
                print(o, de, kind, rep, flush=True)
    df = pd.DataFrame(rows)
    suf = os.environ.get("SUF", "")       # variantes (p. ej. KR=5000 SUF=_kr5000): solo el csv, sin el resumen
    df.to_csv(os.path.join(HERE, "backtest%s.csv" % suf), index=False)
    if not suf:
        informe(df)


def informe(df):
    df["abs_bibi"] = df.err_bibi.abs()
    df["abs_bibi_conteo"] = df.err_bibi_conteo.abs()
    L = ["# Knesset: backtest de la proyección durante el conteo", "",
         "Generado por `backtest.py`. Cuatro pares de elecciones (2019a→2019b, 2019b→2020, 2020→2021, 2021→2022), "
         "dos órdenes de llegada simulados (`azar` y `geo`: localidades chicas primero, ciudades grandes y localidades "
         "árabes después), 5 repeticiones por orden. El doble sobre (soldados, etc.; 6–10 % de los votos) siempre se "
         "proyecta. «conteo» = el conteo parcial pasado a bancas tal cual.", ""]
    for nombre, col, fmt in [("Error absoluto en las bancas del bloque de Netanyahu", "abs_bibi", "%.1f"),
                             ("Ídem, con el conteo parcial tal cual", "abs_bibi_conteo", "%.1f"),
                             ("Error medio por lista (bancas)", "mae_listas", "%.2f"),
                             ("Ídem, con el conteo parcial", "mae_conteo", "%.2f"),
                             ("Listas bien clasificadas por el umbral (%)", "umbral_ok", "%.0f"),
                             ("Desenlace acertado (%)", "desenlace_ok", "%.0f"),
                             ("Ídem, con el conteo parcial (%)", "desenlace_conteo_ok", "%.0f"),
                             ("Probabilidad que el modelo le daba al desenlace real (%)", "p_real", "%.0f"),
                             ("La banda del 90 % del bloque contiene el real (%)", "cubre90", "%.0f"),
                             ("Ancho de la banda del 90 % (bancas)", "ancho90", "%.1f")]:
        x = df.copy()
        if "%)" in nombre:
            x[col] = 100 * x[col].astype(float)
        t = x.pivot_table(index=["par", "orden"], columns="corte", values=col, aggfunc="mean")
        L += ["## " + nombre, "", "| Par | Orden | " + " | ".join("%g %%" % (100 * c) for c in t.columns) + " |",
              "|---|---|" + "---:|" * len(t.columns)]
        for (p, o), r in t.iterrows():
            L.append("| %s | %s | " % (p, o) + " | ".join(fmt % v for v in r) + " |")
        L.append("")
    open(os.path.join(HERE, "RESUMEN_BACKTEST.md"), "w", encoding="utf-8").write("\n".join(L))
    print("-> RESUMEN_BACKTEST.md")


if __name__ == "__main__":
    main()
