"""Shapefiles por provincia para Mosaic (circuitos 2025, censo 2022, tres elecciones en dos bloques).
    <python de Mosaic> analisis/uninominal/construir.py      -> analisis/uninominal/shp/<dd>_<provincia>.shp
Geometria: geometria/circuitos_serie/por_anio/2025/aproximada (la que mejor empareja: 97,7 % de los
electores de 2023 y 99,9 % de 2025). Poblacion: electores 2025 del circuito escalados al censo 2022 de
la provincia (no hay censo por circuito). county = seccion (partido/departamento).
Bloques (Mosaic es bipartidista: DEM = peronismo, GOP = antiperonismo):
  23  general 2023, presidente: UxP / LLA + JxC
  23b balotaje 2023: Massa / Milei
  25  diputados 2025: Fuerza Patria / La Libertad Avanza (bloques de mapas/mapa2025/mapeo_listas_2025.csv)
2023 sobre circuitos 2025: si el codigo existe en los dos años y el padron no cambio mas de 0,8-1,25,
voto directo; el resto de la seccion se reparte entre sus otros circuitos con el padron 2025 y la
desviacion del circuito en 2025 respecto de su seccion. Los totales de cada seccion de 2023 se conservan
(Santa Fe renumero circuitos dentro de las secciones en 2023-25)."""
import os, sys, json, warnings
import numpy as np, pandas as pd, geopandas as gpd
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
from reparto import CENSO
OUT = os.path.join(HERE, "shp")
AEA = "+proj=aea +lat_1=-28 +lat_2=-45 +lat_0=-35 +lon_0=-64 +datum=WGS84 +units=m"


def norm(s):
    return s.fillna("").astype(str).str.strip().str.upper().str.lstrip("0").replace("", "0")


def votos(clave, dem, gop):
    """(distrito, seccion, circuito) -> dem, gop, electores."""
    v, e = pd.read_pickle(os.path.join(ROOT, "transferencias", "circ_%s.pkl" % clave))
    v = v[v.votos_tipo.str.upper() == "POSITIVO"].copy()
    v["s"], v["c"] = norm(v.seccion_id), norm(v.circuito)
    v["b"] = [dem(d, a) and "D" or gop(d, a) and "R" or "" for d, a in zip(v.distrito_id, v.agrupacion_id)]
    t = v[v.b != ""].pivot_table(index=["distrito_id", "s", "c"], columns="b", values="v", aggfunc="sum", fill_value=0)
    e = e.reset_index()
    e["s"], e["c"] = norm(e.seccion_id), norm(e.circuito)
    e = e.groupby(["distrito_id", "s", "c"]).e.sum()
    return t.join(e, how="outer").fillna(0)


m25 = pd.read_csv(os.path.join(ROOT, "mapas", "mapa2025", "mapeo_listas_2025.csv"), dtype=str, encoding="utf-8-sig")
B25 = {(r.distrito, r.lista): r.bloque for r in m25.itertuples()}
EL = {
    "23": votos("2023p", lambda d, a: a == "UNION POR LA PATRIA",
                lambda d, a: a in ("LA LIBERTAD AVANZA", "JUNTOS POR EL CAMBIO")),
    "23b": votos("2023b", lambda d, a: "PATRIA" in a.upper(), lambda d, a: "LIBERTAD" in a.upper()),
    "25": votos("2025", lambda d, a: B25.get((d, a)) == "Fuerza Patria",
                lambda d, a: B25.get((d, a)) == "La Libertad Avanza"),
}
for k, t in EL.items():
    print(k, "D", int(t.D.sum()), "R", int(t.R.sum()))

# geometria: circuitos 2025, claves duplicadas se disuelven
g = gpd.read_file(os.path.join(ROOT, "geometria", "circuitos_serie", "por_anio", "2025", "aproximada", "shp",
                               "circuitos_argentina.shp"))
g = g[~g.geometry.is_empty & g.geometry.notna()].to_crs(AEA)
g["geometry"] = g.geometry.make_valid().buffer(0)
g["s"], g["c"] = norm(g.seccion), norm(g.circuito)
g = g.dissolve(by=["dist", "s", "c"], as_index=False)[["dist", "s", "c", "geometry"]]
g = g.set_index(["dist", "s", "c"])
g.index.names = ["distrito_id", "s", "c"]

e25 = EL["25"].e
base = g.join(e25.rename("e25")).fillna({"e25": 0})
# voto 2025 del circuito
t25 = EL["25"].reindex(base.index).fillna(0)
base["D25"], base["R25"] = t25.D, t25.R
notas = {}


def a_circuitos_2025(t, clave):
    """Lleva una eleccion de 2023 a los circuitos 2025 conservando el total de cada seccion."""
    out = pd.DataFrame(0.0, index=base.index, columns=["D", "R"])
    sec_t = t.groupby(level=[0, 1])[["D", "R", "e"]].sum()
    tt = t.reindex(base.index)
    ok = tt.e.notna() & (tt.e > 0) & (base.e25 / tt.e).between(.8, 1.25)
    out.loc[ok, ["D", "R"]] = tt.loc[ok, ["D", "R"]].values
    directo = 0
    for (d, s), grp in base.groupby(level=[0, 1]):
        if (d, s) not in sec_t.index: continue
        resto = sec_t.loc[(d, s), ["D", "R"]] - out.loc[grp.index, ["D", "R"]].sum()
        libres = grp.index[~ok.loc[grp.index].values]
        if len(libres) == 0 or resto.sum() <= 0:
            continue
        lb = base.loc[libres]
        # desviacion 2025 del circuito respecto del resto de su seccion
        sh_sec = lb.D25.sum() / max(lb.D25.sum() + lb.R25.sum(), 1)
        sh_c = np.where(lb.D25 + lb.R25 > 0, lb.D25 / (lb.D25 + lb.R25).clip(lower=1), sh_sec)
        sh0 = resto.D / resto.sum()
        sh = np.clip(sh0 + (sh_c - sh_sec), .01, .99)
        w = lb.e25.values.astype(float)
        if w.sum() == 0: w = np.ones(len(lb))
        tot = resto.sum() * w / w.sum()
        # ajuste para que la suma del bloque D de la seccion cierre exacto
        d_ = tot * sh
        d_ *= resto.D / max(d_.sum(), 1e-9)
        d_ = np.minimum(d_, tot)
        out.loc[libres, "D"] = d_
        out.loc[libres, "R"] = tot - d_
    directo = t.reindex(base.index[ok.values])[["D", "R"]].sum().sum() / t[["D", "R"]].sum().sum()
    notas[clave] = {"votos_directos": round(float(directo), 4),
                    "votos_en_secciones_sin_circuito": float(t[~t.index.droplevel(2).isin(base.index.droplevel(2))][["D", "R"]].sum().sum())}
    return out.round().astype(int)


for k in ("23", "23b"):
    o = a_circuitos_2025(EL[k], k)
    base["D" + k], base["R" + k] = o.D, o.R
print(json.dumps(notas))

base = gpd.GeoDataFrame(base, geometry="geometry", crs=AEA).reset_index()
base.columns = ["dist", "seccion", "circuito"] + list(base.columns[3:])
os.makedirs(OUT, exist_ok=True)
resumen = {}
for d, (nom, pob) in CENSO.items():
    p = base[base.dist == d].copy().reset_index(drop=True)
    tot = p.e25.sum()
    p["population"] = (p.e25 * pob / tot).round().astype(int) if tot else 0
    p["pid"] = p.dist + "-" + p.seccion + "-" + p.circuito
    p["county"] = p.dist + "-" + p.seccion
    cols = ["pid", "county", "population", "e25", "D23", "R23", "D23b", "R23b", "D25", "R25", "geometry"]
    p = p[cols]
    for c in cols[3:-1]: p[c] = p[c].astype(int)
    slug = "".join(ch for ch in nom.lower().replace(" ", "_") if ch.isalnum() or ch == "_")
    slug = slug.translate(str.maketrans("áéíóú", "aeiou"))
    f = os.path.join(OUT, f"{d}_{slug}.shp")
    p.to_crs(4326).to_file(f, encoding="utf-8")
    resumen[d] = {"provincia": nom, "circuitos": len(p), "sin_padron": int((p.e25 == 0).sum()),
                  "poblacion": int(p.population.sum()), "archivo": os.path.basename(f)}
    print(d, nom, len(p), "circuitos,", resumen[d]["sin_padron"], "sin padron")
json.dump({"notas_2023": notas, "provincias": resumen}, open(os.path.join(OUT, "resumen.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
