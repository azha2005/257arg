"""Reparte los votos de cada local de votacion entre los radios censales 2022 (metodo de Poblaciones / LN Data).
Entrada: dip_amba_mesas.pkl (provisorio por mesa, ../mapaAMBA2025), localesDeVotacionyMesas.csv (local de cada mesa),
locales_amba2025.csv (punto de cada local, geocodificar.py) y radios_amba2022.geojson (radios_amba.py).
Variantes (salida asignacion_<variante>.pkl):
  idw   Poblaciones: peso 1/d^2 entre el local y el centroide de cada radio de su mismo partido (comuna en Capital);
        los radios que reciben menos de 1 voto quedan en 0 y su parte vuelve, en proporcion, a los demas radios del local.
  pob   peso POB_TOT_P/d^2, solo radios de los circuitos de las mesas del local (el radio va al circuito que contiene su punto interior);
        mismo corte de 1 voto. Si un circuito no contiene ningun radio habitado, sus votos van al radio que contiene el local.
d tiene un piso de 25 m (un centroide pegado al local no se lleva el 100 %). Las sumas por partido son exactas.
"""
import os, re, sys, json, math, collections, unicodedata, pickle
import numpy as np, pandas as pd, shapely
from shapely.geometry import shape, Point
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "mapas", "mapaAMBA2025"))
os.environ.setdefault("CIRCUITOS_AR_GEOJSON", os.path.join(ROOT, "geometria", "circuitos_busqueda", "galeano_snapshot_2021", "geojson"))
import geomamba

DMIN = 25.0
KX = math.cos(math.radians(34.7)) * 111320.0; KY = 110574.0


def nrm(s): return re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode())


def bloc_of(n):
    if "FUERZA PATRIA" in n: return "FP"
    if "LA LIBERTAD AVANZA" in n: return "LLA"
    if "IZQUIERDA Y DE TRABAJADORES" in n: return "FIT"
    if n in ("CIUDADANOS UNIDOS", "ALIANZA PROVINCIAS UNIDAS"): return "PU"
    return None


def slug(n): return re.sub(r"[^a-z0-9]+", "_", unicodedata.normalize("NFD", n.lower()).encode("ascii", "ignore").decode()).strip("_")[:40]


# ---------------------------------------------------------------- votos por local
d, feats, target = geomamba.load()
d["mid5"] = d.mesa_id.str.zfill(5)
L = pd.read_csv(os.path.join(ROOT, "datos_oficiales", "2025", "x", "localesDeVotacionyMesas.csv"), dtype=str, encoding="utf8")
L = L[L.distrito_id.isin(["01", "02"])]
L["lk"] = L.distrito_id + "_" + L.seccion_id + "_" + L.localvotacion_codigo
m2l = dict(zip(zip(L.distrito_id, L.seccion_id, L.mesa_id), L.lk))
d["lk"] = [m2l[k] for k in zip(d.dist, d.sec, d.mid5)]
d["cat"] = np.where(d.votos_tipo == "POSITIVO", [bloc_of(x) or slug(x) if isinstance(x, str) else "x" for x in d.agrupacion_nombre],
                    d.votos_tipo.map({"EN BLANCO": "_BLA", "NULO": "_NUL", "IMPUGNADO": "_IMP", "RECURRIDO": "_IMP", "COMANDO": "_IMP"}))
LAB = {}
for c, n in zip(d.cat, d.agrupacion_nombre):
    if isinstance(n, str) and not c.startswith("_"): LAB.setdefault(c, n)
mes = d.drop_duplicates("mesa")[["mesa", "lk", "dist", "sec", "cir", "elec", "estado_final"]].copy()
mes["ok"] = (mes.estado_final == "ESCRUTADO").astype(int)
mes["_ELOK"] = mes.elec * mes.ok
# unidad de reparto: (local, circuito); casi siempre un local = un circuito
d["lc"] = d.lk + "|" + d.cir
mes["lc"] = mes.lk + "|" + mes.cir
V = d.pivot_table(index="lc", columns="cat", values="v", aggfunc="sum", fill_value=0)
V = V.join(mes.groupby("lc")[["_ELOK", "ok"]].sum().rename(columns={"ok": "_MOK"})).join(mes.groupby("lc").size().rename("_MES")).fillna(0)
CATS = list(V.columns)
VOT = V[[c for c in CATS if c not in ("_ELOK", "_MOK", "_MES")]].sum(1).to_dict()   # votantes de cada (local, circuito)
lcinfo = mes.drop_duplicates("lc").set_index("lc")[["lk", "dist", "sec", "cir"]]
part_of = d.drop_duplicates(["dist", "sec"]).set_index(["dist", "sec"]).part.to_dict()

loc = pd.read_csv(os.path.join(HERE, "locales_amba2025.csv"), dtype={"dist": str, "sec": str, "codigo": str}).set_index("lk")

# ---------------------------------------------------------------- radios
R = json.load(open(os.path.join(HERE, "radios_amba2022.geojson"), encoding="utf8"))["features"]
rg = [shape(f["geometry"]) for f in R]
rp = pd.DataFrame([f["properties"] for f in R])
cen = np.array([[g.centroid.x, g.centroid.y] for g in rg])
rep = shapely.points(np.array([[p.x, p.y] for p in (g.representative_point() for g in rg)]))
rp["pkey"] = [("01", "%03d" % c) if p == "02" else ("02", nrm(pa)) for p, c, pa in zip(rp.PROV, rp.comuna.fillna(0).astype(int), rp.partido)]
POB = rp.POB_TOT_P.fillna(0).to_numpy(float)


def pkey_of(dist, sec):
    return ("01", sec) if dist == "01" else ("02", nrm(part_of[(dist, sec)]))


# radio -> circuito (poligono de la capa 2021; los circuitos con letras comparten el poligono de origen)
poly_keys = sorted({t for t in target.values() if t})
tree = shapely.STRtree([shapely.make_valid(feats[k]) for k in poly_keys])
ri, pi = tree.query(rep, predicate="intersects")
r2poly = {}
for a, b in zip(ri, pi): r2poly.setdefault(a, poly_keys[b])
poly2r = collections.defaultdict(list)
for a, k in r2poly.items(): poly2r[k].append(a)
rtree = shapely.STRtree(rg)


def xy(lon, lat): return np.column_stack([np.asarray(lon) * KX, np.asarray(lat) * KY])


CXY = xy(cen[:, 0], cen[:, 1])


def allocate(variant):
    out = np.zeros((len(rg), len(CATS)))
    notes = collections.Counter()
    groups = collections.defaultdict(list)
    for lc, r in lcinfo.iterrows():
        groups[pkey_of(r.dist, r.sec)].append(lc)
    rad_by_p = rp.groupby("pkey").indices
    for pk, lcs in groups.items():
        cand = np.asarray(rad_by_p[pk])
        Wl = []
        for lc in lcs:
            lk = lcinfo.at[lc, "lk"]; p = loc.loc[lk]
            pxy = xy([p.lon], [p.lat])[0]
            if variant == "idw":
                idx = cand; w = np.ones(len(idx))
            else:
                k = target.get((lcinfo.at[lc, "dist"], lcinfo.at[lc, "sec"], lcinfo.at[lc, "cir"]))
                idx = np.array([i for i in poly2r.get(k, []) if pk == rp.pkey[i]], int)
                w = POB[idx] if len(idx) else np.array([])
                if not len(idx) or w.sum() == 0:
                    hit = [i for i in rtree.query(Point(p.lon, p.lat), predicate="intersects") if rp.pkey[i] == pk]
                    if hit: idx = np.array(hit[:1]); w = np.ones(1)
                    else:
                        dd = np.hypot(*(CXY[cand] - pxy).T); idx = cand[[np.argmin(dd)]]; w = np.ones(1)
                    notes["circuito sin radios habitados"] += 1
            dd = np.maximum(np.hypot(*(CXY[idx] - pxy).T), DMIN)
            w = w / dd ** 2
            Wl.append((lc, idx, w / w.sum()))
        # corte de 1 voto: radios cuyo total < 1 quedan en 0 y el reparto de cada local se renormaliza (iterado hasta estabilizar)
        dead = set()
        for _ in range(20):
            tot = collections.Counter()
            for lc, idx, w in Wl:
                for i, x in zip(idx, w * VOT[lc]): tot[i] += x
            new = {i for i, t in tot.items() if t < 1} - dead
            if not new: break
            dead |= new
            W2 = []
            for lc, idx, w in Wl:
                keep = np.array([i not in dead for i in idx])
                if keep.any(): idx, w = idx[keep], w[keep] / w[keep].sum()
                else: notes["local sin radios >= 1 voto (se deja en el mas cercano)"] += 1; j = np.argmax(w); idx, w = idx[[j]], np.ones(1)
                W2.append((lc, idx, w))
            Wl = W2
        for lc, idx, w in Wl:
            out[idx] += np.outer(w, V.loc[lc].to_numpy(float))
    return out, notes


if __name__ == "__main__":
    res = {}
    for var in sys.argv[1:] or ["idw", "pob"]:
        A, notes = allocate(var)
        # control: suma por partido = DINE
        dv = V.copy(); dv["pk"] = [pkey_of(*lcinfo.loc[i, ["dist", "sec"]]) for i in V.index]
        rp_tot = pd.DataFrame(A, columns=CATS).groupby(rp.pkey).sum()
        dv_tot = dv.groupby("pk")[CATS].sum()
        err = (rp_tot.reindex(dv_tot.index).fillna(0) - dv_tot).abs().to_numpy().max()
        tv = A[:, [i for i, c in enumerate(CATS) if c not in ("_ELOK", "_MOK", "_MES")]].sum(1)
        print(var, "error maximo por partido y categoria:", err, "| radios sin votos:", int((tv < 1e-9).sum()), "de", len(tv),
              "| poblacion en radios sin votos:", int(POB[tv < 1e-9].sum()), dict(notes), file=sys.stderr)
        assert err < 1e-6
        res[var] = dict(A=A, notes=dict(notes))
        pickle.dump(dict(A=A, CATS=CATS, LAB=LAB, notes=dict(notes), radios=rp.drop(columns=["pkey"]), err=err),
                    open(os.path.join(HERE, "asignacion_%s.pkl" % var), "wb"))
