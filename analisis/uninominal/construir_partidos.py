"""Votos por radio de cada partido por separado (no dos bloques), para el mapa «Todos los partidos».
    <python de Mosaic> analisis/uninominal/construir_partidos.py   -> analisis/uninominal/radios_partidos.pkl
Mismo camino que construir.py + construir_radios.py, pero con una columna por fuerza:
  23  general 2023 (presidente): UxP, LLA, JxC, Hacemos, FIT
  25  diputados 2025: cada bloque de mapas/mapa2025/mapeo_listas_2025.csv (codigo B.., nombre y color del atlas 2025)
El balotaje 2023 ya es de dos. 2023 sobre circuitos 2025: voto directo si el codigo existe en los dos años y el
padron no cambio mas de 0,8-1,25; el resto de la seccion, partido por partido, a los demas circuitos de la seccion
en proporcion al padron 2025 (sin la correccion por la desviacion 2025 que usa construir.py para los dos bloques).
Circuito -> radios: por poblacion; los circuitos sin radio propio pasan sus votos al radio que mas se les superpone.
Salida: {"radios": DataFrame (dist, pid, columnas "23|<partido>" y "25|<codigo>"), "partidos": {eleccion: {codigo:
{"n": nombre, "c": color}}}}."""
import os, sys, glob, json, pickle, warnings
import numpy as np, pandas as pd, geopandas as gpd
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
AEA = "+proj=aea +lat_1=-28 +lat_2=-45 +lat_0=-35 +lon_0=-64 +datum=WGS84 +units=m"
P23 = {"UNION POR LA PATRIA": ("UxP", "Unión por la Patria", "#009ce4"),
       "LA LIBERTAD AVANZA": ("LLA", "La Libertad Avanza", "#6c4c98"),
       "JUNTOS POR EL CAMBIO": ("JxC", "Juntos por el Cambio", "#fcbc00"),
       "HACEMOS POR NUESTRO PAIS": ("HPNP", "Hacemos por Nuestro País", "#283084"),
       "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": ("FIT", "Frente de Izquierda", "#e3242b")}


def norm(s):
    return s.fillna("").astype(str).str.strip().str.upper().str.lstrip("0").replace("", "0")


def tabla(clave, partido):
    """(distrito, seccion, circuito) x partido, mas electores."""
    v, e = pd.read_pickle(os.path.join(ROOT, "transferencias", "circ_%s.pkl" % clave))
    v = v[v.votos_tipo.str.upper() == "POSITIVO"].copy()
    v["s"], v["c"] = norm(v.seccion_id), norm(v.circuito)
    v["p"] = [partido(d, a) for d, a in zip(v.distrito_id, v.agrupacion_id)]
    t = v[v.p.notna()].pivot_table(index=["distrito_id", "s", "c"], columns="p", values="v", aggfunc="sum", fill_value=0)
    e = e.reset_index()
    e["s"], e["c"] = norm(e.seccion_id), norm(e.circuito)
    return t, e.groupby(["distrito_id", "s", "c"]).e.sum()


m25 = pd.read_csv(os.path.join(ROOT, "mapas", "mapa2025", "mapeo_listas_2025.csv"), dtype=str, encoding="utf-8-sig")
COD25 = {(r.distrito, r.lista): r.codigo for r in m25.itertuples()}
cand = json.load(open(os.path.join(ROOT, "mapas", "mapa2025", "dataset_2025.json"), encoding="utf-8"))["candidates"]
t25, e25 = tabla("2025", lambda d, a: COD25.get((d, a)))
t23, e23 = tabla("2023p", lambda d, a: P23[a][0] if a in P23 else None)
print("2023", t23.sum().astype(int).to_dict())
print("2025", len(t25.columns), "bloques,", int(t25.values.sum()), "votos")

# circuitos 2025 (los de construir.py)
circ = pd.concat([gpd.read_file(f) for f in sorted(glob.glob(os.path.join(HERE, "shp", "*.shp")))], ignore_index=True)
circ["dist"] = circ.pid.str[:2]
circ["s"] = circ.pid.str.split("-").str[1]
circ["c"] = circ.pid.str.split("-").str[2]
idx = pd.MultiIndex.from_arrays([circ.dist, circ.s, circ.c])
padron = circ.set_index(idx).e25.astype(float)

# 2025: directo
v25 = t25.reindex(idx).fillna(0)
v25.index = circ.pid
# 2023: directo donde el circuito es estable, el resto de la seccion por padron 2025
tt = t23.reindex(idx)
et = e23.reindex(idx)
ok = (et > 0) & (padron.values / et.values > .8) & (padron.values / et.values < 1.25)
ok = ok.fillna(False).values
v23 = pd.DataFrame(0.0, index=idx, columns=t23.columns)
v23.loc[ok] = tt.loc[ok].values
sec = t23.groupby(level=[0, 1]).sum()
asig = v23.groupby(level=[0, 1]).sum()
resto = (sec - asig.reindex(sec.index).fillna(0)).clip(lower=0)
libres = ~ok
w = pd.Series(np.where(libres, padron.values, 0.0), index=idx)
wsum = w.groupby(level=[0, 1]).transform("sum")
frac = (w / wsum.replace(0, np.nan)).fillna(0)
rs = resto.reindex(pd.MultiIndex.from_arrays([idx.get_level_values(0), idx.get_level_values(1)])).fillna(0).values
v23 += rs * frac.values[:, None]
v23.index = circ.pid
print("2023 sobre circuitos 2025:", round(v23.values.sum() / t23.values.sum(), 4), "de los votos")

# circuitos -> radios
cols = ["23|" + c for c in v23.columns] + ["25|" + c for c in v25.columns]
vc = pd.concat([v23.add_prefix("23|"), v25.add_prefix("25|")], axis=1)
out = []
for f in sorted(glob.glob(os.path.join(HERE, "shp_radios", "*.shp"))):
    d = os.path.basename(f)[:2]
    r = gpd.read_file(f).to_crs(AEA)
    cg = gpd.read_file(glob.glob(os.path.join(HERE, "shp", f"{d}_*.shp"))[0]).to_crs(AEA)
    pop = r.population.astype(float)
    tot = pop.groupby(r.circ).transform("sum")
    area = r.area
    fr = np.where(tot > 0, pop / tot.replace(0, 1), area / area.groupby(r.circ).transform("sum"))
    vals = vc.reindex(r.circ).fillna(0).values * fr[:, None]
    huerf = cg[~cg.pid.isin(r.circ)]
    for c in huerf.itertuples():
        cand_r = r[r.intersects(c.geometry)]
        k = cand_r.geometry.intersection(c.geometry).area.idxmax() if len(cand_r) else r.distance(c.geometry).idxmin()
        vals[k] += vc.reindex([c.pid]).fillna(0).values[0]
    o = pd.DataFrame(np.round(vals).astype(np.int32), columns=cols)
    o.insert(0, "pid", r.pid.values)
    o.insert(0, "dist", d)
    out.append(o)
rad = pd.concat(out, ignore_index=True)
rad = rad.loc[:, (rad[cols].sum() > 0).reindex(rad.columns, fill_value=True)]
partidos = {"23": {k: {"n": n, "c": c} for k, n, c in P23.values()},
            "25": {k: {"n": cand[k]["n"], "c": cand[k]["base"]} for k in v25.columns if k in cand}}
print("radios", len(rad), "| 23:", int(rad.filter(like="23|").values.sum()), "| 25:", int(rad.filter(like="25|").values.sum()))
pickle.dump({"radios": rad, "partidos": partidos}, open(os.path.join(HERE, "radios_partidos.pkl"), "wb"))
