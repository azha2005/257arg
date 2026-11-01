"""Controles del reparto por radio: ubicacion de los locales y si los cambios de ganador siguen los limites de circuito o de partido.
python diagnostico.py  -> diagnostico.json"""
import os, sys, json, pickle, collections
import numpy as np, pandas as pd, shapely
from shapely.geometry import shape, Point
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "mapas", "mapaAMBA2025"))
os.environ.setdefault("CIRCUITOS_AR_GEOJSON", os.path.join(ROOT, "geometria", "circuitos_busqueda", "galeano_snapshot_2021", "geojson"))
import geomamba
d, feats, target = geomamba.load()
R = json.load(open(os.path.join(HERE, "radios_amba2022.geojson"), encoding="utf8"))["features"]
rg = [shapely.make_valid(shape(f["geometry"])) for f in R]
rep = [g.representative_point() for g in rg]
part = np.array([f["properties"]["partido"] + str(f["properties"]["comuna"]) for f in R])
pk = sorted({t for t in target.values() if t})
tree = shapely.STRtree([shapely.make_valid(feats[k]) for k in pk])
circ = np.full(len(rg), -1)
for a, b in zip(*tree.query(rep, predicate="intersects")): circ[a] = b
# vecinos (comparten borde)
rt = shapely.STRtree(rg)
pairs = set()
for i, j in zip(*rt.query([g.buffer(1e-6) for g in rg], predicate="intersects")):
    if i < j: pairs.add((i, j))
pairs = np.array(sorted(pairs))
out = {}
loc = pd.read_csv(os.path.join(HERE, "locales_amba2025.csv"), dtype=str)
out["locales"] = len(loc)
out["fuente_locales"] = loc.fuente.value_counts().to_dict()
out["electores_por_fuente"] = (loc.assign(e=loc.electores.astype(int)).groupby("fuente").e.sum() / loc.electores.astype(int).sum()).round(4).to_dict()
for var in ("idw", "pob"):
    A = pickle.load(open(os.path.join(HERE, "asignacion_%s.pkl" % var), "rb"))
    C = A["CATS"]; X = A["A"]
    w = np.where(X[:, C.index("FP")] >= X[:, C.index("LLA")], 0, 1)
    has = X[:, [k for k, c in enumerate(C) if not c.startswith("_")]].sum(1) > 0.5
    ok = has[pairs[:, 0]] & has[pairs[:, 1]] & (part[pairs[:, 0]] == part[pairs[:, 1]])   # dentro del mismo partido
    p = pairs[ok]
    diff = w[p[:, 0]] != w[p[:, 1]]
    cross = circ[p[:, 0]] != circ[p[:, 1]]
    out[var] = dict(pares_vecinos_mismo_partido=int(len(p)), pares_que_cruzan_circuito=round(float(cross.mean()), 4),
                    cambios_de_ganador=int(diff.sum()), cambios_de_ganador_sobre_limite_de_circuito=round(float(cross[diff].mean()), 4),
                    prob_cambio_si_cruza_circuito=round(float(diff[cross].mean()), 4), prob_cambio_dentro_del_circuito=round(float(diff[~cross].mean()), 4))
json.dump(out, open(os.path.join(HERE, "diagnostico.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
