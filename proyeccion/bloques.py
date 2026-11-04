"""Diputados por mesa llevados a bloques de la Wikipedia (mapas/mapa<año>/mapeo_listas_<año>.csv), para usarlos como
destino o como origen de la proyeccion:
    python proyeccion/bloques.py 2021 2025
Escribe proyeccion/mesas_<año>bl.pkl (por mesa, como mesas.py) y proyeccion/circ_<año>bl.pkl (por circuito, en el
formato de transferencias/circ_*.pkl: votos en largo y electores por circuito). Los bloques de menos del 3 % del
pais van a OTRAS; los nombres largos se acortan con CORTO."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
KEY = ["distrito_id", "seccion_id", "circuito", "mesa_id", "mesa_tipo"]
CORTO = {"La Libertad Avanza": "LLA", "Fuerza Patria": "FP", "Provincias Unidas": "PU",
         "Frente de Izquierda y de Trabajadores - Unidad": "FIT", "Frente de Todos": "FdT",
         "Juntos por el Cambio": "JxC", "Avanza Libertad y La Libertad Avanza": "LLA",
         "Tercera vía y el Peronismo Federal": "Tercera Via"}


def main(anio):
    m = pd.read_csv(os.path.join(ROOT, "mapas", "mapa%s" % anio, "mapeo_listas_%s.csv" % anio), dtype=str,
                    encoding="utf-8-sig")
    m["votos"] = m.votos.astype(int)
    tot = m.groupby("bloque").votos.sum()
    big = set(tot[tot >= .03 * tot.sum()].index)
    mp = {(r.distrito, r.nombre.strip().upper()): CORTO.get(r.bloque, r.bloque) if r.bloque in big else "OTRAS"
          for r in m.itertuples()}
    w = pd.read_pickle(os.path.join(HERE, "mesas_%s.pkl" % anio))
    fixed = [c for c in ("BLANCO", "NULO", "OTROS") if c in w]
    parties = [c for c in w.columns if c not in KEY + ["e"] + fixed]
    blocs = sorted({CORTO.get(b, b) for b in big}) + ["OTRAS"]
    out = w[KEY + ["e"] + fixed].copy()
    for b in blocs:
        out[b] = 0
    sin = set()
    for d, g in w.groupby("distrito_id"):
        for p in parties:
            if g[p].sum() == 0:
                continue
            b = mp.get((d, p))
            if b is None:
                sin.add((d, p))
                b = "OTRAS"
            out.loc[g.index, b] += g[p]
    out.to_pickle(os.path.join(HERE, "mesas_%sbl.pkl" % anio))
    # por circuito, en largo
    k = ["distrito_id", "seccion_id", "circuito"]
    c = out.groupby(k)[blocs + fixed + ["e"]].sum()
    elect = c.pop("e").rename("e")
    v = c.stack().rename("v").reset_index().rename(columns={"level_3": "col"})
    v["agrupacion_id"] = np.where(v.col.isin(blocs), v.col, "")
    v["votos_tipo"] = v.col.map({"BLANCO": "EN BLANCO", "NULO": "NULO", "OTROS": "OTROS"}).fillna("POSITIVO")
    pd.to_pickle((v[k + ["agrupacion_id", "votos_tipo", "v"]], elect), os.path.join(HERE, "circ_%sbl.pkl" % anio))
    t = out[blocs].sum()
    print(anio, "bloques", (100 * t / t.sum()).round(2).to_dict(), "listas sin bloque:", len(sin), flush=True)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        main(a)
