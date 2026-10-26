"""Capital Federal entre la division electoral de 1973 (28 circunscripciones, hasta 2007) y la de la Res. 1507/2008 del
Ministerio del Interior (15 comunas y 167 circuitos, desde 2009). La resolucion describe los circuitos nuevos por calles y
no da equivalencias con los viejos, asi que el cruce es geometrico:
- antes de 2008: los circuitos se suman por circunscripcion (seccion_id de PolAr = numero de circunscripcion);
- desde 2009: cada circuito se reparte entre las circunscripciones segun la superficie que comparte con cada una
  (circuitos de circuitos_electorales_AR contra mapa1983/caba28.pkl, las 28 circunscripciones ajustadas al contorno),
  y esos pesos se calibran con el padron (ajuste proporcional iterativo): la superficie no ve la densidad y las
  circunscripciones del centro quedaban con 30 % menos electores que en 2003. Solo cambian los circuitos compartidos.
Las unidades comunes quedan con la clave ("01", 0, "C<nn>")."""
import os, json, pickle
import numpy as np, pandas as pd
from shapely.geometry import shape
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
GJ = os.path.join(os.environ.get("CIRCUITOS_AR_GEOJSON", os.path.join(ROOT, "circuitos_electorales_AR-main", "geojson")), "CABA.geojson")
CORTE = 2008        # anio de la Res. 1507/2008


def pesos():
    """DataFrame circuito (str sin ceros) x circunscripcion: fraccion de la superficie del circuito en cada una."""
    c28 = pickle.load(open(os.path.join(ROOT, "mapas/mapa1983", "caba28.pkl"), "rb"))
    feats = json.load(open(GJ, encoding="utf8"))["features"]
    W = {}
    for f in feats:
        g = shape(f["geometry"]).buffer(0)
        a = {n: g.intersection(p.buffer(0)).area for n, (_, p) in c28.items()}
        tot = sum(a.values())
        W[f["properties"]["circuito"].lstrip("0")] = {n: v / tot for n, v in a.items() if v / tot > 0.005}
    W = pd.DataFrame(W).T.fillna(0)
    return W.div(W.sum(1), axis=0)


def calibrar(W, e_nuevo, e_viejo, iters=200):
    """IPF: filas = electores de cada circuito nuevo; columnas = electores de cada circunscripcion en la eleccion
    vieja, escalados al total nuevo. Solo se mueven celdas con superficie en comun (el cero queda cero)."""
    M = W.mul(e_nuevo, axis=0)
    obj = e_viejo.reindex(W.columns).fillna(0) * e_nuevo.sum() / e_viejo.sum()
    for _ in range(iters):
        M = M.mul((obj / M.sum(0).replace(0, np.nan)).fillna(1), axis=1)
        M = M.mul(e_nuevo / M.sum(1), axis=0)
    return M.div(M.sum(1), axis=0)


def cruzar(T, anio, e_viejo=None):
    """Reemplaza las filas de Capital de T (indice distrito, seccion, circuito) por las 28 circunscripciones."""
    if "01" not in T.index.get_level_values(0): return T
    P = T.loc[["01"]]
    if anio < CORTE:
        P = P.groupby(level=1).sum()
        P.index = ["C%02d" % s for s in P.index]
    else:
        W = pesos()
        P = P.droplevel([0, 1])
        if e_viejo is not None:
            W = calibrar(W.loc[P.index], P.sum(1), e_viejo)
        falta = P.index.difference(W.index)
        if len(falta): raise ValueError("circuitos de Capital sin poligono: %s" % list(falta))
        P = W.loc[P.index].T.dot(P)
        P.index = ["C%02d" % n for n in P.index]
    P.index = pd.MultiIndex.from_tuples([("01", 0, c) for c in P.index], names=T.index.names)
    return pd.concat([T.drop(index="01", level=0), P]).sort_index()


if __name__ == "__main__":
    W = pesos()
    print(len(W), "circuitos;", (W.max(1) > 0.9).sum(), "con mas del 90 % en una sola circunscripcion")
    print(W.max(1).describe().round(3).to_dict())
