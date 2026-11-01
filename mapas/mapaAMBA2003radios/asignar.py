"""Reparte los votos presidenciales 2003 de cada circuito entre los radios censales 2001 del AMBA.
No hay registro de en qué local votó cada mesa en 2003 (PolAr llega hasta circuito y mesa). Se usan como locales aproximados
las escuelas de 2025 que caen dentro de cada circuito de 2003 (../mapaAMBA2025radios/locales_amba2025.csv, ya ubicadas y validadas),
y el circuito reparte sus votos entre ellas en proporción a sus electores de 2025. Desde ahí, igual que el atlas 2025 por radio.
Entrada: PolAr data__arg_presi_gral2003.csv (por mesa), capa de circuitos 2003 (geometria/circuitos_serie/por_anio/2003/aproximada,
aporte del usuario con códigos INDRA iguales a PolAr) y radios_amba2001.geojson (radios_amba2001.py).
Variantes (salida asignacion_<variante>.pkl):
  idw   peso 1/d^2 entre cada local aproximado y el centroide de cada radio de su partido (circunscripción en Capital);
        los radios que reciben menos de 1 voto quedan en 0 y su parte vuelve, en proporción, a los demás radios del local.
  pob   control sin locales: cada circuito reparte sus votos entre los radios 2001 cuyo punto interior cae en él, en proporción a su población.
d tiene un piso de 25 m. Las sumas por circuito, partido y circunscripción son exactas.
"""
import os, re, sys, json, math, collections, unicodedata, pickle
import numpy as np, pandas as pd, shapely
from shapely.geometry import shape, Point
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
DMIN = 25.0
KX = math.cos(math.radians(34.7)) * 111320.0; KY = 110574.0


def nrm(s): return re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode())


ALIAS = {"lasheras": "generallasheras", "jcpaz": "josecpaz", "matanza": "lamatanza"}
# tabla nacional de la Wikipedia (analisis/escenarios2003/preparar.py): código PolAr -> candidato
CAND03 = {"0133": "M", "0135": "K", "0131": "L", "0132": "R", "0134": "C", "0003": "MOREAU", "0136": "WALSH", "0050": "BRAVO",
          "0014": "ALTAMIRA", "0053": "VENTURINO", "0022": "SULLINGS", "0137": "ARCAGNI", "0030": "MAZZITELLI", "0001": "ZAFFORE",
          "0005": "HERRERA", "0051": "BREIDE", "0138": "MUSSA", "0037": "TERAN"}

# ---------------------------------------------------------------- radios 2001
R = json.load(open(os.path.join(HERE, "radios_amba2001.geojson"), encoding="utf8"))["features"]
rg = [shapely.make_valid(shape(f["geometry"])) for f in R]
rp = pd.DataFrame([f["properties"] for f in R])
PARTN = {nrm(p): p for p in rp.partido.unique()}
POB = rp.POB_TOT.fillna(0).to_numpy(float)
cen = np.array([[g.centroid.x, g.centroid.y] for g in rg])
rep = shapely.points(np.array([[p.x, p.y] for p in (g.representative_point() for g in rg)]))


def xy(lon, lat): return np.column_stack([np.asarray(lon) * KX, np.asarray(lat) * KY])


CXY = xy(cen[:, 0], cen[:, 1])

# ---------------------------------------------------------------- votos 2003 por circuito
d = pd.read_csv(os.path.join(ROOT, "datos_oficiales", "polar", "data__arg_presi_gral2003.csv"), dtype=str, encoding="utf8")
d = d[d.codprov.isin(["01", "02"])].copy()
d["pk"] = [nrm(x) for x in d.depto]
d["pk"] = d.pk.map(lambda k: ALIAS.get(k, k))
d = d[(d.codprov == "01") | d.pk.isin(PARTN)].copy()
assert d[d.codprov == "02"].pk.nunique() == 40, d[d.codprov == "02"].pk.nunique()
pcols = [c for c in d.columns if re.fullmatch(r"\d{4}", c)]
assert set(pcols) == set(CAND03), set(pcols) ^ set(CAND03)
for c in pcols + ["blancos", "nulos", "electores"]: d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
d["ck"] = d.codprov + "_" + d.coddepto + "_" + d.circuito
d["vt"] = d[pcols + ["blancos", "nulos"]].sum(1)
d["_MES"] = 1; d["_MOK"] = (d.vt > 0).astype(int); d["_ELOK"] = d.electores * d._MOK
V = d.groupby("ck")[pcols + ["blancos", "nulos", "_ELOK", "_MOK", "_MES"]].sum()
V = V.rename(columns={**{c: CAND03[c] for c in pcols}, "blancos": "_BLA", "nulos": "_NUL"})
CATS = list(V.columns)
cinfo = d.drop_duplicates("ck").set_index("ck")[["codprov", "coddepto", "circuito", "depto", "pk"]]
# unidad de restricción: partido en la Provincia, circunscripción en Capital
cinfo["unit"] = [("01", dp) if pv == "01" else ("02", PARTN[pk]) for pv, dp, pk in zip(cinfo.codprov, cinfo.coddepto, cinfo.pk)]
CIRCUNS = d[d.codprov == "01"].drop_duplicates("coddepto").set_index("coddepto").depto.to_dict()
VOTN = V[[c for c in CATS if not c.startswith("_") or c in ("_BLA", "_NUL")]].sum(1)
print("mesas", len(d), "sin votos", int((d.vt == 0).sum()), "| circuitos", len(V), "| votantes", int(VOTN.sum()), file=sys.stderr)

# ---------------------------------------------------------------- circuitos 2003 (capa aproximada, CRS inferido)
L = json.load(open(os.path.join(ROOT, "geometria", "circuitos_serie", "por_anio", "2003", "aproximada", "circuitos_argentina.geojson"), encoding="utf8"))["features"]
CG = {}
for f in L:
    p = f["properties"]; a = p["atributos_originales"]
    if p["codigo_distrito"] not in ("01", "02"): continue
    k = p["codigo_distrito"] + "_" + a["DEPTO"] + "_" + a["CIRC"]
    if k in V.index:
        g = shapely.make_valid(shape(f["geometry"]))
        if g.geom_type == "GeometryCollection": g = unary_union([q for q in g.geoms if q.geom_type in ("Polygon", "MultiPolygon")])
        CG[k] = g
nopoly = [k for k in V.index if k not in CG]
assert not nopoly, nopoly
CK = list(V.index)
ctree = shapely.STRtree([CG[k] for k in CK])

# radio -> circuito 2003 que contiene su punto interior (o el más cercano de su partido, si cae en un hueco de la capa)
ri, ci_ = ctree.query(rep, predicate="intersects")
r2c = {}
for a, b in zip(ri, ci_): r2c.setdefault(a, CK[b])
rp["unit"] = None
for i in range(len(rg)):
    u = cinfo.at[r2c[i], "unit"] if i in r2c else None
    if u and ((rp.PROV[i] == "02" and u[0] == "01") or u[1] == rp.partido[i]):
        rp.at[i, "unit"] = cinfo.at[r2c[i], "unit"]
nohit = [i for i in range(len(rg)) if rp.unit[i] is None]
for i in nohit:   # hueco o desborde de la capa: Capital -> circunscripción del circuito más cercano; Provincia -> su partido
    if rp.PROV[i] == "02":
        cands = [k for k in CK if k.startswith("01_")]
        j = int(np.argmin([CG[k].distance(rep[i]) for k in cands])); rp.at[i, "unit"] = cinfo.at[cands[j], "unit"]
    else:
        rp.at[i, "unit"] = ("02", rp.partido[i])
print("radios fuera de un circuito 2003 de su partido:", len(nohit), "habitantes", int(POB[nohit].sum()), file=sys.stderr)

# ---------------------------------------------------------------- locales aproximados: escuelas 2025 dentro de cada circuito 2003
loc = pd.read_csv(os.path.join(ROOT, "mapas", "mapaAMBA2025radios", "locales_amba2025.csv"), dtype={"dist": str, "sec": str, "codigo": str})
loc = loc[loc.fuente != "centro_circuito"].reset_index(drop=True)   # punto interior de un circuito 2025, no una escuela
lp = shapely.points(loc[["lon", "lat"]].to_numpy())
li, lc = ctree.query(lp, predicate="intersects")
l2c = {}
for a, b in zip(li, lc): l2c.setdefault(a, CK[b])
seats = collections.defaultdict(list)   # circuito -> [(lon, lat, peso)]
mism = 0
for i, r in loc.iterrows():
    k = l2c.get(i)
    if k is None: continue
    pv = cinfo.at[k, "codprov"]
    if pv != r.dist: mism += 1; continue
    if pv == "02" and nrm(cinfo.at[k, "unit"][1]) != nrm(r.seccion): mism += 1; continue   # la capa corrida no cruza partidos
    seats[k].append((r.lon, r.lat, float(r.electores)))
sinloc = [k for k in CK if not seats[k]]
for k in sinloc:
    p = CG[k].representative_point(); seats[k].append((p.x, p.y, 1.0))
CTRL = dict(locales_2025=len(loc), locales_en_circuito=len(l2c), locales_descartados_por_partido=mism,
            circuitos=len(CK), circuitos_sin_escuela=len(sinloc), votantes_en_circuitos_sin_escuela=int(VOTN[sinloc].sum()),
            votantes=int(VOTN.sum()), radios=len(rg), radios_fuera_de_circuito=len(nohit))
print(json.dumps(CTRL), file=sys.stderr)


def allocate(variant):
    out = np.zeros((len(rg), len(CATS)))
    notes = collections.Counter()
    rad_by_u = collections.defaultdict(list)
    for i, u in enumerate(rp.unit): rad_by_u[u].append(i)
    rad_by_c = collections.defaultdict(list)
    for i, k in r2c.items(): rad_by_c[k].append(i)
    groups = collections.defaultdict(list)
    for k in CK: groups[cinfo.at[k, "unit"]].append(k)
    for u, ks in groups.items():
        cand = np.asarray(rad_by_u[u])
        Wl = []   # (circuito, local, idx, w, fracción del circuito)
        for k in ks:
            S = seats[k]; tot = sum(s[2] for s in S)
            if variant == "pob":
                idx = np.array([i for i in rad_by_c.get(k, []) if rp.unit[i] == u], int)
                w = POB[idx] if len(idx) else np.array([])
                if not len(idx) or w.sum() == 0:
                    p = CG[k].representative_point(); pxy = xy([p.x], [p.y])[0]
                    idx = cand[[np.argmin(np.hypot(*(CXY[cand] - pxy).T))]]; w = np.ones(1)
                    notes["circuito sin radios habitados (va al radio más cercano)"] += 1
                Wl.append((k, idx, w / w.sum(), 1.0))
                continue
            for lon, lat, e in S:
                pxy = xy([lon], [lat])[0]
                dd = np.maximum(np.hypot(*(CXY[cand] - pxy).T), DMIN)
                w = 1 / dd ** 2
                Wl.append((k, cand, w / w.sum(), e / tot))
        dead = set()
        for _ in range(20):
            tot = collections.Counter()
            for k, idx, w, f in Wl:
                for i, x in zip(idx, w * f * VOTN[k]): tot[i] += x
            new = {i for i, t in tot.items() if t < 1} - dead
            if not new: break
            dead |= new
            W2 = []
            for k, idx, w, f in Wl:
                keep = np.array([i not in dead for i in idx])
                if keep.any(): idx, w = idx[keep], w[keep] / w[keep].sum()
                else: notes["local sin radios >= 1 voto (queda en el más cercano)"] += 1; j = np.argmax(w); idx, w = idx[[j]], np.ones(1)
                W2.append((k, idx, w, f))
            Wl = W2
        for k, idx, w, f in Wl:
            out[idx] += np.outer(w * f, V.loc[k].to_numpy(float))
    return out, notes


if __name__ == "__main__":
    for var in sys.argv[1:] or ["idw", "pob"]:
        A, notes = allocate(var)
        dv = V.copy(); dv["u"] = [cinfo.at[k, "unit"] for k in V.index]
        a_tot = pd.DataFrame(A, columns=CATS).groupby(rp.unit).sum()
        d_tot = dv.groupby("u")[CATS].sum()
        err = (a_tot.reindex(d_tot.index).fillna(0) - d_tot).abs().to_numpy().max()
        tv = A[:, [i for i, c in enumerate(CATS) if not c.startswith("_") or c in ("_BLA", "_NUL")]].sum(1)
        print(var, "error máximo por unidad y categoría:", err, "| radios sin votos:", int((tv < 1e-9).sum()), "de", len(tv),
              "| población en radios sin votos:", int(POB[tv < 1e-9].sum()), dict(notes), file=sys.stderr)
        assert err < 1e-6
        pickle.dump(dict(A=A, CATS=CATS, notes=dict(notes), radios=rp, err=err, ctrl=CTRL, circuns=CIRCUNS,
                         seats={k: v for k, v in seats.items()}, sinloc=sinloc),
                    open(os.path.join(HERE, "asignacion_%s.pkl" % var), "wb"))
    json.dump(CTRL, open(os.path.join(HERE, "control_asignacion.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
