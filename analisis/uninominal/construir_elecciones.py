"""Votos por radio de las elecciones nacionales 2011-2025 (cada fuerza por separado), para el selector «Otras
elecciones» de mapa_257.html.
    <python de Mosaic> analisis/uninominal/construir_elecciones.py   -> analisis/uninominal/radios_elecciones.pkl
Fuente: transferencias/circ_<clave>.pkl (provisorios por mesa de la DINE agregados por circuito).
  Diputados (2011-2023): bloques de mapas/mapa<año>/mapeo_listas_<año>.csv (2013: LIST2BLOC de su build, via
  transferencias/estimar.mapeo), con nombre y color del atlas del año (dataset_<año>.json).
  Presidente, balotaje y PASO presidenciales: agrupaciones o precandidatos de estimar.CAT, colores de los mapas
  presidenciales de la Wikipedia que usan los atlas.
Fuerzas con menos de 0,5 % nacional y menos de 10 % en todas las provincias van a «Otros».
Las elecciones que ya estan en la pagina (general y balotaje 2023, diputados 2025) no se repiten.
Circuitos de cada año -> circuitos 2025, como construir_partidos.py: voto directo si el codigo existe en los dos
años y el padron cambio menos de 0,8-1,25; el resto de la seccion, fuerza por fuerza, a sus demas circuitos en
proporcion al padron 2025. Santa Fe renumero sus circuitos en 2023: antes de eso va casi todo por seccion.
Circuito -> radios: por poblacion (los circuitos sin radio propio pasan al radio que mas se les superpone)."""
import os, sys, glob, json, pickle, warnings
import numpy as np, pandas as pd, geopandas as gpd
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "transferencias"))
import estimar  # noqa: E402  (CAT, mapeo)
AEA = "+proj=aea +lat_1=-28 +lat_2=-45 +lat_0=-35 +lon_0=-64 +datum=WGS84 +units=m"
# clave del pkl, titulo, tipo
ELX = [("2011", "Diputados 2011", "dip"), ("2011p", "Presidente 2011", "pres"),
       ("2013", "Diputados 2013", "dip"),
       ("2015pp", "PASO presidencial 2015", "pres"), ("2015", "Diputados 2015", "dip"),
       ("2015p", "Presidente 2015", "pres"), ("2015b", "Balotaje 2015", "pres"),
       ("2017", "Diputados 2017", "dip"),
       ("2019", "Diputados 2019", "dip"), ("2019p", "Presidente 2019", "pres"),
       ("2021", "Diputados 2021", "dip"),
       ("2023pp", "PASO presidencial 2023", "pres"), ("2023", "Diputados 2023", "dip")]
# presidente: color por nombre de la categoria (paleta de los mapas presidenciales de la Wikipedia)
COL = {"Frente para la Victoria": "#50ade6", "FAP": "#ff6600", "UDESO (UCR)": "#d31515", "Compromiso Federal": "#1aff98",
       "Frente Popular": "#b73c96", "FIT": "#f65058", "CC-ARI": "#74b744", "Cambiemos": "#f4ce00", "UNA (Massa)": "#231f20",
       "Progresistas": "#ff6600", "Frente de Todos": "#2ea3ff", "Juntos por el Cambio": "#f4ce00",
       "Consenso Federal": "#2f3b81", "FIT-U": "#f65058", "NOS + Unite": "#8d6e63",
       "Scioli (FPV)": "#50ade6", "Macri (Cambiemos)": "#f4ce00", "Sanz (Cambiemos)": "#c62828", "Carrió (Cambiemos)": "#74b744",
       "Massa (UNA)": "#231f20", "De la Sota (UNA)": "#7b8794", "Stolbizer": "#ff6600", "Rodríguez Saá": "#1aff98",
       "Del Caño (FIT)": "#f65058", "Altamira (FIT)": "#b71c1c",
       "Massa (UxP)": "#009ce4", "Grabois (UxP)": "#0b4f8a", "Milei (LLA)": "#6c4c98", "Bullrich (JxC)": "#fcbc00",
       "Larreta (JxC)": "#e07b00", "Schiaretti (Hacemos)": "#283084", "Otros": "#9a9a9a"}
OTROS = "Otros"


def norm(s):
    return s.fillna("").astype(str).str.strip().str.upper().str.lstrip("0").replace("", "0")


def tabla(k, tipo):
    """(distrito, seccion, circuito) x fuerza (codigo), electores y {codigo: (nombre, color)}."""
    v, e = pd.read_pickle(os.path.join(ROOT, "transferencias", "circ_%s.pkl" % k))
    v = v[v.votos_tipo.str.upper() == "POSITIVO"].copy()
    if tipo == "dip":
        y = int(k)
        m = estimar.mapeo(y)
        cod = {(r.distrito, r.lista): r.codigo for r in m.itertuples()}
        cand = json.load(open(os.path.join(ROOT, "mapas", f"mapa{y}", f"dataset_{y}.json"), encoding="utf-8"))["candidates"]
        v["p"] = [cod.get((d, a), OTROS) for d, a in zip(v.distrito_id, v.agrupacion_id)]
        v.loc[~v.p.isin(cand), "p"] = OTROS
        info = {c: (x["n"], x.get("base", "#9a9a9a")) for c, x in cand.items()}
    else:
        cat = estimar.CAT[k]
        v["p"] = v.agrupacion_id.map(cat).fillna(OTROS)
        info = {n: (n, COL.get(n, "#9a9a9a")) for n in set(cat.values())}
    info[OTROS] = ("Otros", "#9a9a9a")
    v["s"], v["c"] = norm(v.seccion_id), norm(v.circuito)
    t = v.pivot_table(index=["distrito_id", "s", "c"], columns="p", values="v", aggfunc="sum", fill_value=0)
    # las chicas a Otros: menos de 0,5 % nacional y menos de 10 % en todas las provincias
    tot = t.sum()
    pv = t.groupby(level=0).sum()
    pv = pv.div(pv.sum(1), axis=0)
    chicas = [c for c in t.columns if c != OTROS and tot[c] / tot.sum() < .005 and pv[c].max() < .10]
    if chicas:
        t[OTROS] = t.get(OTROS, 0) + t[chicas].sum(1)
        t = t.drop(columns=chicas)
    t = t[[c for c in t.sum().sort_values(ascending=False).index]]
    e = e.reset_index()
    e["s"], e["c"] = norm(e.seccion_id), norm(e.circuito)
    return t, e.groupby(["distrito_id", "s", "c"]).e.sum(), {c: info.get(c, (c, "#9a9a9a")) for c in t.columns}


# circuitos 2025 (los de construir.py) y su padron
circ = pd.concat([gpd.read_file(f) for f in sorted(glob.glob(os.path.join(HERE, "shp", "*.shp")))], ignore_index=True)
circ["dist"] = circ.pid.str[:2]
circ["s"] = circ.pid.str.split("-").str[1]
circ["c"] = circ.pid.str.split("-").str[2]
idx = pd.MultiIndex.from_arrays([circ.dist, circ.s, circ.c])
padron = circ.set_index(idx).e25.astype(float)


def a_2025(t, e):
    """Votos del año sobre los circuitos 2025."""
    tt, et = t.reindex(idx), e.reindex(idx)
    q = padron.values / et.values
    ok = ((et > 0) & (q > .8) & (q < 1.25)).fillna(False).values
    out = pd.DataFrame(0.0, index=idx, columns=t.columns)
    out.loc[ok] = tt.loc[ok].fillna(0).values
    sec = t.groupby(level=[0, 1]).sum()
    resto = (sec - out.groupby(level=[0, 1]).sum().reindex(sec.index).fillna(0)).clip(lower=0)
    w = pd.Series(np.where(~ok, padron.values, 0.0), index=idx)
    frac = (w / w.groupby(level=[0, 1]).transform("sum").replace(0, np.nan)).fillna(0)
    rs = resto.reindex(pd.MultiIndex.from_arrays([idx.get_level_values(0), idx.get_level_values(1)])).fillna(0).values
    out += rs * frac.values[:, None]
    out.index = circ.pid
    return out, float(out.values.sum() / t.values.sum()), float(ok.mean())


vcs, partidos, control = [], {}, {}
for k, tit, tipo in ELX:
    t, e, info = tabla(k, tipo)
    v, cob, directo = a_2025(t, e)
    vcs.append(v.add_prefix(k + "|"))
    partidos[k] = {"t": tit, "p": {c: {"n": info[c][0], "c": info[c][1]} for c in v.columns}}
    control[k] = {"votos_conservados": round(cob, 4), "circuitos_directos": round(directo, 3), "fuerzas": len(v.columns)}
    print(k, tit, control[k], flush=True)
vc = pd.concat(vcs, axis=1)
cols = list(vc.columns)

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
    for c in cg[~cg.pid.isin(r.circ)].itertuples():
        cand_r = r[r.intersects(c.geometry)]
        j = cand_r.geometry.intersection(c.geometry).area.idxmax() if len(cand_r) else r.distance(c.geometry).idxmin()
        vals[j] += vc.reindex([c.pid]).fillna(0).values[0]
    o = pd.DataFrame(np.round(vals).astype(np.int32), columns=cols)
    o.insert(0, "pid", r.pid.values)
    o.insert(0, "dist", d)
    out.append(o)
rad = pd.concat(out, ignore_index=True)
pickle.dump({"radios": rad, "partidos": partidos, "orden": [k for k, *_ in ELX], "control": control},
            open(os.path.join(HERE, "radios_elecciones.pkl"), "wb"))
json.dump(control, open(os.path.join(HERE, "control_elecciones.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("radios", len(rad), "columnas", len(cols))
