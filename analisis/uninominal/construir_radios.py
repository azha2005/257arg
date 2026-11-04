"""Shapefiles por provincia para Mosaic con radios censales 2022 (poblacion del censo, votos del circuito).
    <python de Mosaic> analisis/uninominal/construir_radios.py   -> analisis/uninominal/shp_radios/<dd>_<provincia>.shp
Requiere antes construir.py (shp/ tiene los votos por circuito 2025).
Radios: geometria/cartografia_argentina/conicet/radios/RADIOS_2022_V2025-1.zip (CONICET, POB_TOT_P = poblacion
en viviendas particulares del censo 2022). Cada radio va al circuito 2025 que contiene su punto interior (si no
cae en ninguno, al mas cercano de su provincia). Los votos de cada circuito se reparten entre sus radios en
proporcion a la poblacion: el total de cada circuito se conserva exacto, pero dentro del circuito todos los
radios tienen el mismo porcentaje. Un circuito sin radios propios (muy chico) pasa sus votos al radio que mas
se le superpone. county = departamento del censo."""
import os, sys, glob, json, zipfile, warnings
import numpy as np, pandas as pd, geopandas as gpd
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
from reparto import CENSO
OUT = os.path.join(HERE, "shp_radios")
AEA = "+proj=aea +lat_1=-28 +lat_2=-45 +lat_0=-35 +lon_0=-64 +datum=WGS84 +units=m"
ZIP = os.path.join(ROOT, "geometria", "cartografia_argentina", "conicet", "radios", "RADIOS_2022_V2025-1.zip")
# INDEC -> DINE: los dos siguen el orden alfabetico historico
INDEC = ["02", "06", "10", "14", "18", "22", "26", "30", "34", "38", "42", "46", "50", "54", "58", "62", "66", "70",
         "74", "78", "82", "86", "90", "94"]
DINE = {c: "%02d" % (i + 1) for i, c in enumerate(INDEC)}
VOT = ["D23", "R23", "D23b", "R23b", "D25", "R25", "e25"]

tmp = os.path.join(HERE, "_radios_tmp")
if not os.path.exists(os.path.join(tmp, "Radios 2022 v2025-1.shp")):
    zipfile.ZipFile(ZIP).extractall(tmp)
rad = gpd.read_file(os.path.join(tmp, "Radios 2022 v2025-1.shp")).to_crs(AEA)
rad["geometry"] = rad.geometry.make_valid().buffer(0)
rad = rad[~rad.geometry.is_empty].reset_index(drop=True)
rad["dist"] = rad.PROV.map(DINE)
rad["pop"] = rad.POB_TOT_P.fillna(0).astype(int)
print(len(rad), "radios", int(rad["pop"].sum()), "habitantes")

os.makedirs(OUT, exist_ok=True)
resumen = {}
for d, (nom, _) in CENSO.items():
    circ = gpd.read_file(glob.glob(os.path.join(HERE, "shp", f"{d}_*.shp"))[0]).to_crs(AEA)
    r = rad[rad.dist == d].copy().reset_index(drop=True)
    pts = gpd.GeoDataFrame(geometry=r.geometry.representative_point(), crs=AEA)
    j = gpd.sjoin(pts, circ[["pid", "geometry"]], how="left", predicate="within")
    j = j[~j.index.duplicated()]
    r["circ"] = j.pid.values
    fuera = r.circ.isna()
    if fuera.any():
        nn = gpd.sjoin_nearest(pts[fuera.values], circ[["pid", "geometry"]], how="left")
        r.loc[fuera, "circ"] = nn[~nn.index.duplicated()].pid.values
    # circuitos sin radio propio: sus votos van al radio que mas se les superpone
    huerf = circ[~circ.pid.isin(r.circ) & (circ[VOT].sum(axis=1) > 0)]
    extra = {}
    for c in huerf.itertuples():
        cand = r[r.intersects(c.geometry)]
        if len(cand) == 0:
            cand = r.iloc[[r.distance(c.geometry).idxmin()]]
        k = cand.geometry.intersection(c.geometry).area.idxmax()
        extra.setdefault(k, []).append(c.pid)
    # reparto de los votos del circuito por poblacion (si el circuito no tiene poblacion, por superficie)
    w = r["pop"].astype(float)
    tot_c = w.groupby(r.circ).transform("sum")
    area = r.area
    w_area = area / area.groupby(r.circ).transform("sum")
    frac = np.where(tot_c > 0, w / tot_c.replace(0, 1), w_area)
    cv = circ.set_index("pid")[VOT]
    vals = cv.reindex(r.circ).values * frac[:, None]
    for k, pids in extra.items():
        vals[k] += cv.loc[pids].sum().values
    out = r[["COD_2022", "PROV", "DEPTO", "circ", "pop", "geometry"]].copy()
    for i, c in enumerate(VOT):
        out[c] = np.round(vals[:, i]).astype(int)
    out = out.rename(columns={"COD_2022": "pid", "pop": "population"})
    out["county"] = out.PROV + out.DEPTO
    out = out[["pid", "county", "circ", "population"] + VOT + ["geometry"]]
    slug = os.path.basename(glob.glob(os.path.join(HERE, "shp", f"{d}_*.shp"))[0])
    out.to_crs(4326).to_file(os.path.join(OUT, slug), encoding="utf-8")
    dif = {c: int(out[c].sum() - cv[c].sum()) for c in VOT}
    resumen[d] = {"provincia": nom, "radios": len(out), "poblacion": int(out.population.sum()),
                  "circuitos": len(circ), "circuitos_sin_radio": len(huerf),
                  "radios_fuera_de_circuito": int(fuera.sum()), "dif_redondeo": dif}
    print(d, nom, resumen[d])
json.dump(resumen, open(os.path.join(OUT, "resumen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
