"""Punto de cada local de votacion del 7-sep-2025 en el AMBA (para el reparto por radio).
    python mapas/mapaPBA2025sep/locales_sep.py
1. El local ya ubicado en el atlas por radio de octubre (../mapaAMBA2025radios/locales_amba2025.csv): mismo codigo de local
   ('02_<partido>_<colegio>', la base de graficarpba usa el codigo de la DINE). Cubre el 99,99 % de los electores de mesas de nativos.
2. Los locales que solo tienen mesas de extranjeros (no figuran en octubre, sin direccion en la base): padron de escuelas de la DGCyE
   (escuelas.py del atlas de octubre) por tipo y numero de escuela o nombre muy parecido, dentro del partido y validado contra el
   circuito de sus mesas (300 m; si no, 1,5 km: sufijo «_cerca»).
3. Sin punto valido: el punto interior del circuito de sus mesas («centro_circuito»).
Salida: locales_sep.csv (lk, sec, nombre, mesas, electores, circuitos, fuente, lon, lat).
"""
import os, sys
import numpy as np, pandas as pd, shapely
from shapely.geometry import Point

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "mapas", "mapaAMBA2025radios"))
import cargar
import escuelas

d, feats, target = cargar.load("amba")
mes = d.drop_duplicates("mesa")
loc = mes.groupby("lk").agg(sec=("sec", "first"), sn=("seccion_nombre", "first"), nombre=("colegio_nombre", "first"),
                            mesas=("mesa", "size"), electores=("elec", "sum"), tipos=("tipo", lambda s: "".join(sorted(set(s)))),
                            cirs=("cir", lambda s: sorted(set(s)))).reset_index()
OCT = pd.read_csv(os.path.join(ROOT, "mapas", "mapaAMBA2025radios", "locales_amba2025.csv"), dtype={"sec": str, "codigo": str}).set_index("lk")
TOL = 300 / 111000
PP = {}
for (a, b, c), t in target.items():
    if t: PP.setdefault(b, []).append(shapely.make_valid(feats[t]))
PP = {k: shapely.union_all(v).buffer(TOL) for k, v in PP.items()}


def circ_poly(r):
    gs = [shapely.make_valid(feats[target[("02", r.sec, c)]]) for c in r.cirs if target.get(("02", r.sec, c))]
    return shapely.union_all(gs) if gs else None


ESC = escuelas.load()
rows = []
for r in loc.itertuples():
    if r.lk in OCT.index:
        o = OCT.loc[r.lk]
        rows.append(dict(fuente="octubre:" + o.fuente, lon=o.lon, lat=o.lat)); continue
    g = circ_poly(r)
    e = escuelas.match("02", r.sn, r.nombre, "", ESC)
    pick = None
    if e:
        p = Point(e[1], e[2])
        dd = (g.distance(p) * 100000) if g is not None else (0 if PP[r.sec].contains(p) else np.inf)
        if PP[r.sec].contains(p) and dd <= 300: pick = (e[0], e[1], e[2])
        elif PP[r.sec].contains(p) and dd <= 1500: pick = (e[0] + "_cerca", e[1], e[2])
    if pick is None:
        q = g.representative_point() if g is not None else None
        pick = ("centro_circuito", q.x, q.y) if q is not None else ("sin_punto", np.nan, np.nan)
    rows.append(dict(fuente=pick[0], lon=pick[1], lat=pick[2]))
out = pd.concat([loc.drop(columns=["sn"]), pd.DataFrame(rows)], axis=1)
out["circuitos"] = out.cirs.map(" ".join); out = out.drop(columns=["cirs"])
out.to_csv(os.path.join(HERE, "locales_sep.csv"), index=False, encoding="utf8")
f = out.fuente.str.split(":").str[0].where(~out.fuente.str.startswith("octubre"), "octubre")
print(out.groupby(f).agg(locales=("lk", "size"), electores=("electores", "sum")).assign(pct=lambda t: (100 * t.electores / t.electores.sum()).round(2)).to_string())
print(out[~out.fuente.str.startswith("octubre")].fuente.value_counts().to_string())
assert out.lon.notna().all()
