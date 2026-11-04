# python transferencias/2025s_2025/comparar_municipios.py   (necesita provinciales2025/bases.pkl, que está en el repo del explorador)
"""Compara PBA sept->oct 2025: original por municipio (definitivo) vs agregado propio por municipio y por circuito (provisorio).
Mismo metodo (RxC Calvo ponderado por votos validos de destino), mismas categorias, base votos validos (sin No voto)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "transferencias")
from rxc_calvo import fit

O = ["LLA", "FP", "Somos", "Potencia", "FIT-U", "Otros", "Blanco"]
D = ["FP", "LLA", "PU", "FIT-U", "Prop. Federal", "Otros", "Blanco"]

def estimar(X, Y):
    X, Y = X[(X.sum(1) > 0) & (Y.sum(1) > 0)], Y[(X.sum(1) > 0) & (Y.sum(1) > 0)]
    XA, YB = X.div(X.sum(1), axis=0), Y.div(Y.sum(1), axis=0)
    w = Y.sum(1) / Y.sum(1).mean()
    V = XA.mul(Y.sum(1), axis=0).sum().values
    out = {}
    for nom, ww in (("principal", w.values), ("calvo", None)):
        B = fit(XA.values, YB.values, const=0.001, w=ww)
        M = B * V[:, None]
        out[nom] = pd.DataFrame(M / M.sum(1, keepdims=True) * 100, index=O, columns=D)
    out["votos"] = pd.DataFrame(fit(XA.values, YB.values, const=0.001, w=w.values) * V[:, None], index=O, columns=D)
    out["n"] = len(X)
    return out

# 1) original: municipios, escrutinio definitivo
X, Y, _ = pd.read_pickle("transferencias/provinciales2025/bases.pkl")["pba_prov2025_dn2025"]
X.columns, Y.columns = O, D
r1 = estimar(X.astype(float), Y.astype(float))

# 2) y 3) propios: septiembre (graficarpba, mesas X) y octubre (DINE), provisorios
vs, _ = pd.read_pickle("transferencias/circ_2025s.pkl")
so = {"LA LIBERTAD AVANZA": "LLA", "FUERZA PATRIA": "FP", "SOMOS BUENOS AIRES": "Somos", "POTENCIA": "Potencia",
      "FTE DE IZQ. Y DE TRABAJADORES - UNIDAD": "FIT-U"}
vs = vs[vs.votos_tipo.isin(["POSITIVO", "EN BLANCO"])].copy()
vs["cat"] = np.where(vs.votos_tipo == "EN BLANCO", "Blanco", vs.agrupacion_id.map(so).fillna("Otros"))
vn, _ = pd.read_pickle("transferencias/circ_2025.pkl")
vn = vn[(vn.distrito_id == "02") & vn.votos_tipo.str.upper().isin(["POSITIVO", "EN BLANCO"])].copy()
dn = {"0248": "FP", "0110": "LLA", "0259": "PU", "0372": "FIT-U", "0258": "Prop. Federal"}
vn["cat"] = np.where(vn.votos_tipo.str.upper() == "EN BLANCO", "Blanco", vn.agrupacion_id.map(dn).fillna("Otros"))
k = ["seccion_id", "circuito"]
Xs = vs.pivot_table(index=k, columns="cat", values="v", aggfunc="sum", fill_value=0).reindex(columns=O, fill_value=0)
Yn = vn.pivot_table(index=k, columns="cat", values="v", aggfunc="sum", fill_value=0).reindex(columns=D, fill_value=0)
idx = Xs.index.intersection(Yn.index)
r3 = estimar(Xs.loc[idx].astype(float), Yn.loc[idx].astype(float))
r2 = estimar(Xs.groupby(level=0).sum().astype(float), Yn.groupby(level=0).sum().astype(float))

pd.set_option("display.width", 200)
print("marginales origen  original:", X.sum().astype(int).to_dict())
print("marginales origen  propio  :", Xs.loc[idx].sum().astype(int).to_dict())
for nom, r in (("1) ORIGINAL municipios, definitivo", r1), ("2) PROPIO sumado a municipio, provisorio", r2), ("3) PROPIO por circuito, provisorio", r3)):
    print("\n==", nom, "| unidades", r["n"], "| principal (Calvo entre parentesis en celdas que difieren > 5)")
    P, C = r["principal"].round(1), r["calvo"].round(1)
    print(P.to_string())
def dif(a, b, V):
    return float((np.abs(a["votos"].values / a["votos"].values.sum() - b["votos"].values / b["votos"].values.sum())).sum() / 2 * 100)
print("\n%% de votos que cambian de celda: 1 vs 2 (fuente) %.1f | 2 vs 3 (nivel) %.1f | 1 vs 3 (total) %.1f" % (dif(r1, r2, 0), dif(r2, r3, 0), dif(r1, r3, 0)))
print("principal vs Calvo: 1) %.1f  2) %.1f  3) %.1f" % tuple(
    float((np.abs(r["principal"] - r["calvo"]).values * r["votos"].sum(1).values[:, None] / r["votos"].values.sum()).sum() / 2) for r in (r1, r2, r3)))
print("\nDiferencia en puntos (3 - 1):"); print((r3["principal"] - r1["principal"]).round(1).to_string())
