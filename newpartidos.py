"""Partidos y departamentos creados despues del censo de 1991, con su propio poligono (atlas de 1997 y 2001).

El mapa de 1991 todavia incluye en el partido de origen a Ezeiza, Hurlingham, Ituzaingo, Presidente Peron, Punta Indio, San Miguel, Jose C. Paz,
Malvinas Argentinas y (en Chaco) 2 de Abril. Pedido del usuario: no fusionarlos con el partido de origen en el mapa, sino tomar su poligono del
shapefile de 2001. Como los dos shapefiles no digitalizan igual el limite, el contorno exterior de cada grupo queda el de 1991: cada poligono de
2001 se recorta a la union de los poligonos de 1991 del grupo, y lo que sobra de esa union se reparte entre los poligonos vecinos de 2001.

    import newpartidos; units = newpartidos.apply(geom.load())
"""
import os
import shapely
from shapely.ops import unary_union
from shp import read_shp, read_dbf
from geom import to_poly
from names import norm

HERE = os.path.dirname(os.path.abspath(__file__))
SHP2001 = os.path.join(HERE, "Base deptos 1869-2022", "Departamentos_2001")

# (provincia, nombre en el mapa de 1991 que se reemplaza) -> poligonos de 2001 (nombre, nombre para mostrar)
GROUPS = [
    ("Buenos Aires", ["Esteban Echeverria"], [("Esteban Echeverr", "Esteban Echeverria"), ("Ezeiza", "Ezeiza")]),
    ("Buenos Aires", ["Moron"], [("Moron", "Morón"), ("Hurlingham", "Hurlingham"), ("Ituzaing", "Ituzaingó")]),
    ("Buenos Aires", ["San Vicente"], [("San Vicente", "San Vicente"), ("Presidente Per", "Presidente Perón")]),
    ("Buenos Aires", ["Magdalena"], [("Magdalena", "Magdalena"), ("Punta Indio", "Punta Indio")]),
    ("Buenos Aires", ["Gnral.Sarmiento"], [("San Miguel", "San Miguel"), ("Jos", "José C. Paz"), ("Malvinas Argentinas", "Malvinas Argentinas")]),
    ("Chaco", ["12 de Octubre"], [("12 de Octubre", "12 de Octubre"), ("2 de Abril", "2 de Abril")]),
]
# San Salvador (Entre Rios) es posterior a 1997: la base de 1997 lo trae dentro de Concordia; la de 2001 ya lo trae aparte
GROUPS_2001 = [("Entre Ríos", ["Concordia"], [("Concordia", "Concordia"), ("San Salvador", "San Salvador")])]


def _find(units, prov, prefix):
    n = norm(prefix)
    hits = [i for i, u in enumerate(units) if u["prov"] == prov and norm(u["name"]).startswith(n)]
    return hits


def apply(units, desde2001=False, provincias=None):
    sh, db = read_shp(SHP2001 + ".shp"), read_dbf(SHP2001 + ".dbf")
    P2001 = {}
    for g, r in zip(sh, db):
        P2001.setdefault((r["PROV_COD"], norm(r["DEPTO"])), []).append((r["DEPTO"], to_poly(g), r["LINK_"]))
    codes = {"Buenos Aires": "06", "Chaco": "22", "Entre Ríos": "30"}
    drop, add = set(), []
    for prov, olds, news in GROUPS + (GROUPS_2001 if desde2001 else []):
        if provincias is not None and prov not in provincias: continue   # p. ej. 1993 y 1994: la base solo trae 2 de Abril (Chaco) aparte
        idx = []
        for o in olds:
            h = _find(units, prov, o)
            assert len(h) == 1, (prov, o, [units[i]["name"] for i in h])
            idx.append(h[0])
        R = unary_union([units[i]["geom"] for i in idx]).buffer(0)
        pieces = []
        for pref, disp in news:
            n = norm(pref)
            c = [v for (pc, k), vs in P2001.items() if pc == codes[prov] and k.startswith(n) for v in vs]
            assert len(c) == 1, (prov, pref, [v[0] for v in c])
            pieces.append([disp, c[0][1].buffer(0).intersection(R), c[0][2]])
        # lo que sobra de la union de 1991 (por diferencias de digitalizacion) se reparte entre los poligonos de 2001 vecinos
        rest = R.difference(unary_union([p[1] for p in pieces]))
        for q in (rest.geoms if hasattr(rest, "geoms") else [rest]):
            if q.is_empty or q.area <= 0: continue
            j = min(range(len(pieces)), key=lambda k: pieces[k][1].distance(q))
            pieces[j][1] = unary_union([pieces[j][1], q])
        for disp, g, link in pieces:
            kind = "partido" if prov == "Buenos Aires" else "departamento"
            add.append(dict(prov=prov, name=disp, kind=kind, link=[link], geom=g.buffer(0)))
        drop.update(idx)
        a1, a2 = R.area, unary_union([p[1] for p in pieces]).area
        assert abs(a1 - a2) / a1 < 1e-6, (prov, olds, a1, a2)
    return [u for i, u in enumerate(units) if i not in drop] + add
