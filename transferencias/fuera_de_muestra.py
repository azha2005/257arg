"""¿Una sola matriz nacional (variante «Calvo») predice mejor que las provinciales encogidas (principal) cuando solo hay
datos por departamento? Ajuste fuera de muestra en los pares de Cantón: cada variante se estima sin un quinto de los
departamentos (5 grupos al azar, 3 repeticiones) y predice el reparto de destino (todas las categorías, también No votó)
de los que quedaron afuera. Error = raíz del error cuadrático medio en puntos, ponderado por electores de destino.
Referencia «sin origen»: el reparto medio de destino de los departamentos de entrenamiento de la misma provincia
(lo que se predice sin mirar la elección de origen). Mismo filtro y λ que la estimación publicada (control.json).
    python transferencias/fuera_de_muestra.py [par ...]
Salida: fuera_de_muestra/RESUMEN.md y resumen.csv."""
import os, sys, json
import numpy as np, pandas as pd
import estimar
from rxc_calvo import fit
from estimar import fit_prov

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fuera_de_muestra")
PARES = {"1930d_1946d": (0.5, 2), "1937d_1946d": (0.5, 2), "1940d_1946d": (0.5, 2),
         "1954p_1958p": (0.6, 2.3), "1954d_1965d": (0.6, 2.7), "1958d_1962d": (0.6, 2.3)}


def ajustar(X, Y, w, prov, lam, calvo):
    """Igual que en controles_1999.py (no se importa: agregacion.py lee sys.argv al importarse)."""
    if calvo:
        B = fit(X.values, Y.values, const=0.001)
        return lambda Xt, pt: Xt.values @ B
    Bn = fit(X.values, Y.values, const=0.001, w=w.values)
    g0 = np.log(Bn[:, :-1] / Bn[:, -1:]).ravel()
    Bp = {p: fit_prov(X[prov == p].values, Y[prov == p].values, lam * (prov == p).sum(), w[prov == p].values, g0)
          for p in prov.unique()}
    return lambda Xt, pt: np.vstack([Xt.values[i] @ Bp.get(p, Bn) for i, p in enumerate(pt)])


def sin_origen(Y, w, prov):
    """Reparto medio ponderado de la provincia en el entrenamiento (nacional si la provincia no tiene unidades)."""
    nac = np.average(Y.values, axis=0, weights=w.values)
    por = {p: np.average(Y[prov == p].values, axis=0, weights=w[prov == p].values) for p in prov.unique()}
    return lambda Xt, pt: np.vstack([por.get(p, nac) for p in pt])


def evaluar(par, ratio):
    y0, y1 = par.split("_")
    estimar.RATIO = ratio
    A, B, X, Y, w, rows, cols, ctl = estimar.prepare(y0, y1)
    lam = json.load(open(os.path.join(HERE, par, "control.json"), encoding="utf8"))["lambda"]
    prov = pd.Series(A.index.get_level_values(0), index=A.index)
    peso = B.sum(1)
    voto = [c for c in cols if c != "No votó"]
    modelos = {"principal": lambda Xr, Yr, wr, pr: ajustar(Xr, Yr, wr, pr, lam, False),
               "Calvo": lambda Xr, Yr, wr, pr: ajustar(Xr, Yr, wr, pr, lam, True),
               "sin origen": lambda Xr, Yr, wr, pr: sin_origen(Yr, wr, pr),
               "media nacional": lambda Xr, Yr, wr, pr: sin_origen(Yr, wr, pd.Series("", index=pr.index))}
    fila = dict(par=par, unidades=len(A), provincias=prov.nunique(), filas=len(rows), destinos=len(cols), lam=lam)
    for nombre, mk in modelos.items():
        e_all = np.zeros(len(A)); e_voto = np.zeros(len(A))
        for rep in range(3):
            fold = np.random.default_rng(rep).integers(0, 5, len(A))
            for k in range(5):
                tr, te = fold != k, fold == k
                P = pd.DataFrame(mk(X[tr], Y[tr], w[tr], prov[tr])(X[te], prov[te].values), index=X.index[te], columns=cols)
                P = P.div(P.sum(1), axis=0); R = Y[te]
                e_all[te] += (((P - R) * 100) ** 2).mean(1).values
                pv = P[voto].div(P[voto].sum(1), axis=0); rv = R[voto].div(R[voto].sum(1), axis=0)
                e_voto[te] += (((pv - rv) * 100) ** 2).mean(1).values
        fila["rmse_" + nombre] = round(float(np.sqrt(np.average(e_all / 3, weights=peso))), 2)
        fila["rmse_votantes_" + nombre] = round(float(np.sqrt(np.average(e_voto / 3, weights=peso))), 2)
    print(fila, flush=True)
    return fila


def main(pares):
    os.makedirs(OUT, exist_ok=True)
    f = os.path.join(OUT, "resumen.csv")
    T = pd.read_csv(f, encoding="utf-8-sig") if os.path.exists(f) else pd.DataFrame(columns=["par"])
    nuevas = pd.DataFrame([evaluar(p, PARES[p]) for p in pares])
    T = pd.concat([T[~T.par.isin(pares)], nuevas], ignore_index=True)
    T = T.set_index("par").reindex([p for p in PARES if p in set(T.par)]).reset_index()
    T = T.astype({c: int for c in ("unidades", "provincias", "filas", "destinos")})
    T.to_csv(f, index=False, encoding="utf-8-sig")
    md = lambda T: "\n".join(["| " + " | ".join(map(str, T.columns)) + " |", "|---" * len(T.columns) + "|"] +
                             ["| " + " | ".join(str(x) for x in r) + " |" for r in T.values])
    L = ["# Fuera de muestra: matrices provinciales contra una sola matriz nacional (pares de Cantón)", "",
         "rmse_*: error (puntos) al predecir el reparto de destino de departamentos que no entraron al ajuste, con todas las "
         "categorías (también No votó); rmse_votantes_*: solo el reparto entre fuerzas (sin No votó). Ponderado por electores "
         "de destino; 5 grupos × 3 repeticiones. «sin origen» = reparto medio de la provincia, sin mirar la elección de origen; «media nacional» = reparto medio "
         "del país (la referencia de la matriz nacional, que tampoco distingue provincias).", "",
         md(T)]
    open(os.path.join(OUT, "RESUMEN.md"), "w", encoding="utf8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:] or list(PARES))
