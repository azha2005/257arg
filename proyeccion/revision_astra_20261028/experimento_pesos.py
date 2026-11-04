"""Piloto emparejado: pesos por fuerza frente a pesos comunes con fotos parciales.
No cambia el modelo operativo. 500 colecciones por par, semilla nueva.
Universo: el cruce del backtest existente, con sus limitaciones de cobertura.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.argv = [sys.argv[0], "2023p", "2025bl", "--circuito"]
import backtest as bt
import fotos_sim as fs
import fotos_modelo as fm


def main():
    rows = []
    for ori, des in [("2019p", "2023p"), ("2021bl", "2023p"), ("2023p", "2025bl")]:
        bt.Y0, bt.Y1, bt.CIRC = ori, des, True
        with contextlib.redirect_stdout(io.StringIO()):
            st, _, cols = bt.state()
        X, Y, e, dist = [st[k] for k in ["X", "Y", "e", "dist"]]
        strata = fm.region(st["distrito_id"], st["seccion_id"], "amba")
        st["amba"] = strata == "AMBA"
        shares = pd.Series(e).groupby(strata).sum().pipe(lambda s:s/s.sum()).to_dict()
        oc = [c.replace(" (orig)", "") for c in st["ocols"]]
        src = [[oc.index(c) for c in fs.SRC[(ori, des)].get(d, [d]) if c in oc] for d in cols]
        nat = (X*e[:,None]).sum(0)
        real = fm.pct(st["Vd"].sum(0), st["pos"])
        top = np.argsort(-real)[:2]
        rm = real[top[0]]-real[top[1]]
        rng = np.random.default_rng(20261028)
        for rep in range(500):
            idx, _ = fs.colecciones(st, rng, "como25", 30)
            x, y, w = X[idx], Y[idx].copy(), e[idx]
            s = strata[idx]
            common = fm.poststrat(w, s, shares)
            # Referencia con todas las columnas visibles.
            full = fm.pct(fm.goodman(x, y, common, nat, src, .1), st["pos"])
            # Caso sintetico: hasta diez actas AMBA solo informan a los dos primeros.
            partial = rng.choice(np.where(s == "AMBA")[0], min(10, (s == "AMBA").sum()), replace=False)
            hidden = [j for j in range(y.shape[1]) if j not in [st["pos"][t] for t in top]]
            y[np.ix_(partial, hidden)] = np.nan
            current = fm.pct(fm.goodman(x, y, common, nat, src, .1), st["pos"])
            adjusted = []
            for j in range(y.shape[1]):
                seen = np.isfinite(y[:,j])
                weights = fm.poststrat(w[seen], s[seen], shares)
                adjusted.append(fm.goodman(x[seen], y[seen,j:j+1], weights, nat, [src[j]], .1)[0])
            candidate = fm.pct(np.array(adjusted), st["pos"])
            for name, p in [("completas",full), ("parciales_peso_comun",current), ("parciales_peso_por_fuerza",candidate)]:
                rows.append(dict(par=ori+"->"+des, rep=rep, variante=name,
                                 mae_fuerzas=np.abs(p-real).mean(),
                                 error_margen=p[top[0]]-p[top[1]]-rm,
                                 abs_margen=abs(p[top[0]]-p[top[1]]-rm)))
    df=pd.DataFrame(rows)
    df.to_csv(HERE / "piloto_pesos.csv",index=False)
    summary=df.groupby(["par","variante"])[["mae_fuerzas","abs_margen","error_margen"]].mean()
    print(summary.round(3).to_string())
    (HERE / "piloto_pesos_resumen.json").write_text(summary.reset_index().to_json(orient="records",indent=2),encoding="utf-8")


if __name__ == "__main__":
    main()
