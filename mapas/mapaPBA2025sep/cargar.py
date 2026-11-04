"""Mesas del 7-sep-2025 (preparar.py) + poligonos de circuito de la capa 2021 (circuitos_electorales_AR), como ../mapaAMBA2025/geomamba.py.
load("amba") -> los 40 partidos del AMBA; load("pba") -> los 135 partidos. Devuelve (d, feats, target): target[(dist, sec, cir)] = clave del
poligono propio o del circuito de origen (la base subdivide con letras: 0364A -> 00364), o None si la capa no lo tiene."""
import json, re, os
import pandas as pd
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__))
GJ = os.environ.get("CIRCUITOS_AR_GEOJSON", os.path.join(HERE, "..", "..", "geometria", "circuitos_busqueda", "galeano_snapshot_2021", "geojson"))


def caba_feats():
    return [shape(ft["geometry"]) for ft in json.load(open(os.path.join(GJ, "CABA.geojson"), encoding="utf8"))["features"]]


def load(region):
    d = pd.read_pickle(os.path.join(HERE, "mesas_%s.pkl" % region))
    feats = {}
    for ft in json.load(open(os.path.join(GJ, "PBA.geojson"), encoding="utf8"))["features"]:
        p = ft["properties"]
        feats[("02", p["coddepto"], p["circuito"])] = shape(ft["geometry"])
    secs = set(d.sec)
    feats = {k: g for k, g in feats.items() if k[1] in secs}
    target = {}
    for r in d[["dist", "sec", "cir"]].drop_duplicates().itertuples():
        k = (r.dist, r.sec, r.cir)
        if k in feats: target[k] = k; continue
        m = re.match(r"0*(\d+)", r.cir)
        pk = (r.dist, r.sec, m.group(1).zfill(5)) if m else None
        target[k] = pk if pk in feats else None
    return d, feats, target


if __name__ == "__main__":
    import sys
    d, feats, target = load(sys.argv[1] if len(sys.argv) > 1 else "pba")
    print(len(feats), "poligonos;", len(target), "circuitos de la base; sin poligono:", sorted(k for k, t in target.items() if t is None))
