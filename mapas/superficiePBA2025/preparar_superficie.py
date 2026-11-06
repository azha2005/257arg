"""Votos por local de votacion de la PBA el 7-sep-2025 (provinciales) y el 26-oct-2025 (diputados nacionales), con un punto por local.
    python mapas/superficiePBA2025/preparar_superficie.py
Salida: locales_superficie.csv (lk, sec, partido, cir, lon, lat, fuente, y por eleccion FP, LLA, pos).
Septiembre: mesas_pba.pkl de ../mapaPBA2025sep (graficarpba, fuera de git), nativos y extranjeros.
Octubre: resultados2025.csv de la DINE (provisorio por mesa) + localesDeVotacionyMesas.csv (mesa -> local, sin coordenadas).
Punto de cada local, en este orden:
  1. el del atlas por radio de octubre (AMBA, locales_amba2025.csv) o el de septiembre (locales_sep.csv);
  2. padron de escuelas de la DGCyE (escuelas.match del atlas de octubre), validado: dentro de 1,5 km del circuito de sus mesas;
  3. punto interior del circuito de sus mesas.
"""
import os, sys, json
import numpy as np, pandas as pd, shapely
from shapely.geometry import Point

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
SEP = os.path.join(ROOT, "mapas", "mapaPBA2025sep")
sys.path.insert(0, SEP)
sys.path.insert(0, os.path.join(ROOT, "mapas", "mapaAMBA2025radios"))
import cargar, escuelas
from partidos_sep import bloc_of

# --- septiembre -----------------------------------------------------------------------------------------
d, feats, target = cargar.load("pba")
p = d[d.votos_tipo == "POSITIVO"].assign(b=lambda t: t.agrupacion_nombre.map(bloc_of))
s = p.groupby("lk").agg(sec=("sec", "first"), partido=("seccion_nombre", "first"), nombre=("colegio_nombre", "first"),
                        cir=("cir", lambda x: x.value_counts().index[0]), sep_pos=("v", "sum")).join(
    p[p.b.isin(["FP", "LLA"])].pivot_table(index="lk", columns="b", values="v", aggfunc="sum").add_prefix("sep_"))

# --- octubre --------------------------------------------------------------------------------------------
X = os.path.join(ROOT, "datos_oficiales", "2025", "x")
L = pd.read_csv(os.path.join(X, "localesDeVotacionyMesas.csv"), dtype=str)
L = L[L.distrito_id == "02"]
L["mesa"] = L.seccion_id + "|" + L.mesa_id.str.lstrip("0")
L["lk"] = "02_" + L.seccion_id + "_" + L.localvotacion_codigo
cache = os.path.join(HERE, "oct_mesas.pkl")
if os.path.exists(cache):
    o = pd.read_pickle(cache)
else:
    parts = []
    for ch in pd.read_csv(os.path.join(X, "resultados2025.csv"), chunksize=2_000_000, dtype={"circuito_id": str},
                          usecols=["distrito_id", "seccion_id", "circuito_id", "mesa_id", "cargo_nombre", "agrupacion_nombre", "votos_tipo", "votos_cantidad"]):
        ch = ch[(ch.distrito_id == 2) & (ch.cargo_nombre == "DIPUTADO NACIONAL") & (ch.votos_tipo == "POSITIVO")]
        parts.append(ch)
    o = pd.concat(parts, ignore_index=True)
    o.to_pickle(cache)
o["mesa"] = o.seccion_id.astype(int).map("{:03d}".format) + "|" + o.mesa_id.astype(str)
o["b"] = np.where(o.agrupacion_nombre.str.contains("FUERZA PATRIA"), "FP", np.where(o.agrupacion_nombre.str.contains("LIBERTAD AVANZA"), "LLA", "O"))
print("octubre, agrupaciones FP/LLA:", o[o.b != "O"].agrupacion_nombre.unique())
o = o.drop(columns=["seccion_id"]).merge(L[["mesa", "lk", "seccion_id", "seccion_nombre", "localvotacion_nombre", "localvotacion_direccion"]], on="mesa", how="left")
assert o.lk.notna().all(), o[o.lk.isna()].mesa.unique()[:10]
o["cir"] = o.circuito_id.str.zfill(5)
oc = o.groupby("lk").agg(sec=("seccion_id", "first"), partido=("seccion_nombre", "first"), nombre=("localvotacion_nombre", "first"),
                         direccion=("localvotacion_direccion", "first"), cir=("cir", lambda x: x.value_counts().index[0]), oct_pos=("votos_cantidad", "sum")).join(
    o[o.b != "O"].pivot_table(index="lk", columns="b", values="votos_cantidad", aggfunc="sum").add_prefix("oct_"))

# --- union y puntos -------------------------------------------------------------------------------------
loc = oc.combine_first(s)
loc = loc[[c for c in ["sec", "partido", "nombre", "direccion", "cir", "sep_FP", "sep_LLA", "sep_pos", "oct_FP", "oct_LLA", "oct_pos"]]]
known = {}
for f in (os.path.join(ROOT, "mapas", "mapaAMBA2025radios", "locales_amba2025.csv"), os.path.join(SEP, "locales_sep.csv")):
    for r in pd.read_csv(f).itertuples():
        if r.lk not in known and str(r.fuente) not in ("centro_circuito", "sin_punto"):
            known[r.lk] = (str(r.fuente).split(":")[-1], r.lon, r.lat)
ESC = escuelas.load()


def cpoly(sec, cir):
    t = target.get(("02", sec, cir))
    if t is None:
        import re
        m = re.match(r"0*(\d+)", cir)
        t = ("02", sec, m.group(1).zfill(5)) if m and ("02", sec, m.group(1).zfill(5)) in feats else None
    return shapely.make_valid(feats[t]) if t else None


PART = {}
for k, g in feats.items(): PART.setdefault(k[1], []).append(g)
PART = {k: shapely.union_all([shapely.make_valid(x) for x in v]) for k, v in PART.items()}
rows = []
for lk, r in loc.iterrows():
    if lk in known:
        rows.append(known[lk]); continue
    g = cpoly(r.sec, r.cir)
    e = escuelas.match("02", r.partido, r.nombre, r.direccion if isinstance(r.direccion, str) else "", ESC)
    if e and g is not None and g.distance(Point(e[1], e[2])) * 100000 <= 1500:
        rows.append(e); continue
    q = (g if g is not None else PART[r.sec]).representative_point()
    rows.append(("centro_circuito" if g is not None else "centro_partido", q.x, q.y))
loc[["fuente", "lon", "lat"]] = pd.DataFrame(rows, index=loc.index)
loc = loc.fillna({c: 0 for c in ["sep_FP", "sep_LLA", "sep_pos", "oct_FP", "oct_LLA", "oct_pos"]})
loc.index.name = "lk"
loc.to_csv(os.path.join(HERE, "locales_superficie.csv"), encoding="utf8")
for e in ("sep", "oct"):
    w = loc[e + "_pos"]
    print(e, "locales", int((w > 0).sum()), "positivos", int(w.sum()), "FP %.2f LLA %.2f" % (100 * loc[e + "_FP"].sum() / w.sum(), 100 * loc[e + "_LLA"].sum() / w.sum()))
    print((loc.groupby("fuente")[e + "_pos"].sum() / w.sum() * 100).round(2).to_string())
