"""Dos controles para elegir entre las versiones de presidente 1999 -> 2003 (replica_libro.py):
1. Ajuste fuera de muestra: cada versión se estima sin un quinto de los departamentos (5 grupos al azar, 3 repeticiones) y
   predice el reparto entre los cinco candidatos de 2003 en los que quedaron afuera. Error = raíz del error cuadrático medio
   en puntos, ponderado por votos de 2003, sobre todos los departamentos y por tamaño (más y menos de 10.000 votantes).
   No prueba que los flujos sean los reales: descarta versiones que encajan peor con los datos.
2. Córdoba por circuito: la estimación con los 630 circuitos de Córdoba (mismas categorías) contra lo que cada versión
   nacional dice para Córdoba (la principal, su matriz provincial; la de Calvo, la matriz nacional, que vale igual en todas).
   Se compara el reparto entre los cinco candidatos de cada fila grande; la distancia es ½ Σ |diferencia| en puntos.
    python transferencias/controles_1999.py          (después de replica_libro.py)
Salida: replica_libro_1999pe_2003pe/CONTROLES.md y controles.csv."""
import os, itertools, json
import numpy as np, pandas as pd
import estimar, replica_libro as rl
from rxc_calvo import fit
from estimar import fit_prov

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = rl.OUT
D, O = rl.D, rl.O
VERSIONES = ["+".join(c) or "base" for k in range(len(rl.CAUSAS) + 1) for c in itertools.combinations(rl.CAUSAS, k)]


def ajustar(X, Y, w, prov, lam, calvo):
    """Matriz por unidad de entrenamiento: Calvo = una nacional sin ponderar; principal = provincial encogida a la nacional."""
    if calvo:
        B = fit(X.values, Y.values, const=0.001)
        return lambda Xt, pt: Xt.values @ B
    Bn = fit(X.values, Y.values, const=0.001, w=w.values)
    g0 = np.log(Bn[:, :-1] / Bn[:, -1:]).ravel()
    Bp = {p: fit_prov(X[prov == p].values, Y[prov == p].values, lam * (prov == p).sum(), w[prov == p].values, g0)
          for p in prov.unique()}
    return lambda Xt, pt: np.vstack([Xt.values[i] @ Bp.get(p, Bn) for i, p in enumerate(pt)])


def control1(A, B):
    real = B[D].div(B[D].sum(1), axis=0)
    peso = B.sum(1); grande = A.sum(1) > 10000
    prov = pd.Series(A.index.get_level_values(0), index=A.index)
    filas = []
    for n in VERSIONES:
        c = n.split("+")
        rows = O if "tres_filas" in c else list(A.columns); cols = D if "cinco_destinos" in c else list(B.columns)
        X = A[rows].div(A[rows].sum(1), axis=0); Y = B[cols].div(B[cols].sum(1), axis=0)
        w = B[cols].sum(1) / B[cols].sum(1).mean()
        lam = json.load(open(os.path.join(OUT, n, "control.json"), encoding="utf8"))["lambda"]
        for calvo in (False, True):
            err = pd.DataFrame(index=A.index, columns=D, dtype=float)
            for rep in range(3):
                fold = np.random.default_rng(rep).integers(0, 5, len(A))
                for k in range(5):
                    tr = (fold != k) & (grande.values if "filtro" in c else True); te = fold == k
                    pr = ajustar(X[tr], Y[tr], w[tr], prov[tr], lam, calvo)(X[te], prov[te].values)
                    P = pd.DataFrame(pr, index=X.index[te], columns=cols)[D]
                    P = P.div(P.sum(1), axis=0)
                    e2 = ((P - real[te]) * 100) ** 2
                    err.loc[e2.index] = e2.values if rep == 0 else err.loc[e2.index].values + e2.values
            err = err / 3
            rmse = lambda m: float(np.sqrt(np.average(err[m].mean(1), weights=peso[m])))
            filas.append(dict(version=n, variante="Calvo" if calvo else "principal", rmse=round(rmse(err.index == err.index), 2),
                              rmse_grandes=round(rmse(grande.values), 2), rmse_chicos=round(rmse(~grande.values), 2)))
    return pd.DataFrame(filas)


def reparto(P):
    P = P.loc[O, D]
    return P.div(P.sum(1), axis=0) * 100


def control2():
    """Córdoba por circuito con las categorías de 1999pe/2003pe: solo el distrito 04, sin agrupar."""
    sub = os.path.join(OUT, "cordoba_circuito")
    base = estimar.prepare
    def prepare(y0, y1):
        A, B, XA, YB, w, rows, cols, ctl = base(y0, y1)
        m = A.index.get_level_values(0) == "04"
        A, B = A[m], B[m]
        ctl["unidades"] = len(A)
        return A, B, A.div(A.sum(1), axis=0), B.div(B.sum(1), axis=0), B.sum(1) / B.sum(1).mean(), rows, cols, ctl
    if not os.path.exists(os.path.join(sub, "matriz_votos.csv")):
        estimar.prepare = prepare; estimar.BOOT = 2
        estimar.main(rl.Y0, rl.Y1, out=sub)
        estimar.prepare = base
    lee = lambda f: pd.read_csv(f, index_col=0, encoding="utf-8-sig")
    ref = {"principal": reparto(lee(os.path.join(sub, "matriz_votos.csv"))), "Calvo": reparto(lee(os.path.join(sub, "calvo_nacional.csv")))}
    filas = []
    for n in VERSIONES:
        pp = pd.read_csv(os.path.join(OUT, n, "por_provincia.csv"), dtype={"distrito": str}, encoding="utf-8-sig")
        pp = pp[pp.distrito.str.zfill(2) == "04"].pivot_table(index="origen", columns="destino", values="votos", aggfunc="sum")
        for var, P in (("principal", reparto(pp)), ("Calvo", reparto(lee(os.path.join(OUT, n, "calvo_nacional.csv"))))):
            for rv, R in ref.items():
                d = (P - R).abs().sum(1) / 2
                filas.append(dict(version=n, variante=var, referencia_cordoba=rv, **{o.split(" ")[0]: round(d[o], 1) for o in O},
                                  media=round(float(d.mean()), 1)))
    return pd.DataFrame(filas), ref


def main():
    A, B, *_ = rl.DPTO(rl.Y0, rl.Y1)
    c1 = control1(A, B)
    c2, ref = control2()
    c1.merge(c2[c2.referencia_cordoba == "principal"][["version", "variante", "media"]].rename(columns={"media": "dist_cordoba"}),
             on=["version", "variante"]).to_csv(os.path.join(OUT, "controles.csv"), index=False, encoding="utf-8-sig")
    lib = pd.read_csv(os.path.join(OUT, "resumen.csv"), encoding="utf-8-sig")[["version", "variante", "media"]].rename(columns={"media": "dist_libro"})
    T = c1.merge(c2[c2.referencia_cordoba == "principal"][["version", "variante", "media"]].rename(columns={"media": "dist_cordoba_circ"}),
                 on=["version", "variante"]).merge(
        c2[c2.referencia_cordoba == "Calvo"][["version", "variante", "media"]].rename(columns={"media": "dist_cordoba_circ_calvo"}),
        on=["version", "variante"]).merge(lib, on=["version", "variante"]).sort_values("rmse")
    T.to_csv(os.path.join(OUT, "controles.csv"), index=False, encoding="utf-8-sig")
    md = lambda T: "\n".join(["| " + " | ".join(map(str, T.columns)) + " |", "|---" * len(T.columns) + "|"] +
                             ["| " + " | ".join(str(x) for x in r) + " |" for r in T.values])
    L = ["# Controles de las versiones de presidente 1999 → 2003", "",
         "rmse: error fuera de muestra (puntos) al predecir el reparto entre los cinco candidatos de 2003 por departamento; "
         "grandes/chicos: más/menos de 10.000 votantes en 1999.",
         "dist_cordoba_circ: distancia media (filas De la Rúa, Duhalde, Cavallo; reparto entre los cinco candidatos) con la estimación de "
         "Córdoba por circuito (principal; _calvo: su variante Calvo). dist_libro: distancia con la fig. 6.12.", "",
         md(T), "", "## Córdoba por circuito (referencia, reparto entre los cinco candidatos)", "", md(ref["principal"].round(1).reset_index())]
    open(os.path.join(OUT, "CONTROLES.md"), "w", encoding="utf8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
