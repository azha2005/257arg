"""Geometria de circuitos del AMBA (CNE/INDEC georef, circuitos_electorales_AR) + union con los votos 2025."""
import json, re, os, pickle
import numpy as np, shapely
from shapely.geometry import shape
from shapely.ops import unary_union
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
# copia local de github.com/.../circuitos_electorales_AR (carpeta geojson)
GJ = os.environ.get("CIRCUITOS_AR_GEOJSON", os.path.join(HERE, "..", "circuitos_electorales_AR-main", "geojson"))

def load():
    d = pd.read_pickle(os.path.join(HERE, "dip_amba_mesas.pkl"))
    feats = {}
    for f, dist in (("CABA.geojson", "01"), ("PBA.geojson", "02")):
        for ft in json.load(open(os.path.join(GJ, f), encoding="utf8"))["features"]:
            p = ft["properties"]
            feats[(dist, "001" if dist == "01" else p["coddepto"], p["circuito"])] = shape(ft["geometry"])
    # cada circuito de la base -> poligono propio o el del circuito "padre" (la base subdivide con letras: 0364A -> 00364)
    rows = d[["dist", "sec", "cir", "part"]].drop_duplicates()
    target = {}
    for r in rows.itertuples():
        k = (r.dist, "001" if r.dist == "01" else r.sec, r.cir)
        if k in feats: target[(r.dist, r.sec, r.cir)] = k; continue
        m = re.match(r"0*(\d+)", r.cir)
        pk = (r.dist, "001" if r.dist == "01" else r.sec, m.group(1).zfill(5)) if m else None
        target[(r.dist, r.sec, r.cir)] = pk if pk in feats else None
    return d, feats, target

if __name__ == "__main__":
    d, feats, target = load()
    used = {t for t in target.values() if t}
    g = [feats[k] for k in used]
    print(len(used), "poligonos usados; bbox", shapely.total_bounds(g))
    print("sin poligono:", [k for k, t in target.items() if t is None])
