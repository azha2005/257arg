"""Mapa de los 257 distritos uninominales: cuatro planes, tres elecciones, camara completa o por mitades.
    <python de Mosaic> analisis/uninominal/mapa.py     -> analisis/uninominal/mapa_257.html (autocontenido)
Lee plan_radios[_<modo>]/<dd>.csv (de distritar.py) y shp_radios/. Los radios se simplifican como una cobertura
(shapely.coverage_simplify: cada borde compartido una sola vez), una para el pais y otra, mas fina, para el recuadro
del AMBA; distritos, provincias y partidos son uniones de esos radios, asi que sus lineas coinciden.
Renovacion por mitades: en cada provincia los distritos se ordenan de norte a sur y oeste a este y se alternan
entre la clase A (se elige con la general 2023) y la B (con diputados 2025); en provincias con bancas impares
la mitad grande va a 2023 en las primeras provincias (por codigo) hasta llegar a 130 + 127, como la Camara.
Boton «Ley Bases»: el proyecto original de la Ley Bases (0025-PE-2023, art. 447) manda sortear las
circunscripciones de la primera renovacion parcial; se sortean con semilla fija las mismas cantidades por provincia."""
import os, sys, glob, json, warnings
import numpy as np, pandas as pd, geopandas as gpd, shapely
from shapely.geometry import box
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reparto import CENSO
AEA = "+proj=aea +lat_1=-28 +lat_2=-45 +lat_0=-35 +lon_0=-64 +datum=WGS84 +units=m"
MODOS = [("neutral", "plan_radios", "Neutral compacto"), ("proporcional", "plan_radios_proporcional", "Proporcional"),
         ("peronista", "plan_radios_peronista", "Gerrymander peronista"), ("lla", "plan_radios_lla", "Gerrymander LLA"),
         ("peronista_extremo", "plan_radios_peronista_extremo", "Peronista extremo"),
         ("lla_extremo", "plan_radios_lla_extremo", "LLA extremo")]
# cada modo en tres versiones: limites libres (radios), respetando departamentos (distritar.py --deptos) y
# respetando circuitos electorales (--circuitos, cortes penalizados) y las dos cosas (--deptos --circuitos); dep = 0-3
PLANES = [(k, c + suf, t, dep) for dep, suf in ((0, ""), (1, "_deptos"), (2, "_circ"), (3, "_dc")) for k, c, t in MODOS]
# UNI_ANTI=1: pagina local aparte (mapa_257_antiperonista.html, elecciones en elecciones_257_anti/) con los
# gerrymanders antiperonistas guiados por elecciones viejas (distritar.py con UNI_GUIA), junto a los planes por
# circuitos de referencia. No se publica.
ANTI = os.environ.get("UNI_ANTI") == "1"
if ANTI:
    PLANES = [(k, c + "_circ", t, 2) for k, c, t in MODOS if k in ("neutral", "peronista_extremo", "lla_extremo")] + [
        ("anti" + g, f"plan_g{g}_lla_extremo_circ", t, 2) for g, t in (
            ("2011p", "Antiperonista: presidente 2011"), ("2015", "Antiperonista: diputados 2015"),
            ("2015p", "Antiperonista: presidente 2015"), ("2015b", "Antiperonista: balotaje 2015"),
            ("2019", "Antiperonista: diputados 2019"), ("2019p", "Antiperonista: presidente 2019"))]
XDIR = "elecciones_257_anti" if ANTI else "elecciones_257"
ELEC = [("23", "General 2023", "UxP", "LLA + JxC"), ("23b", "Balotaje 2023", "Massa", "Milei"),
        ("25", "Diputados 2025", "Fuerza Patria", "LLA")]
# recuadro del AMBA (Capital + conurbano): un rectangulo en la proyeccion que contiene este cuadro en grados
AMBA_LL = (-58.95, -35.0, -57.9, -34.4)
# tolerancias de coverage_simplify (raiz del area de los triangulos que se quitan, en metros): ~0,5 px en cada marco
# (el pais se puede ampliar hasta ~12 veces: 1 km ahi son ~2 px)
TOL_N, TOL_A = 1000, 120
# las coordenadas van en enteros a K veces el tamano del marco (560 y 620 px de ancho): precision de 1/K px
KN, KA = 20, 10
# lo que se dibuja del pais: sin la Antartida ni las Georgias/Sandwich (vienen con Tierra del Fuego)
VIS_LL = (-74.0, -55.3, -53.5, -21.5)

radios = []
for f in sorted(glob.glob(os.path.join(HERE, "shp_radios", "*.shp"))):
    g = gpd.read_file(f).to_crs(AEA)
    g["dist"] = os.path.basename(f)[:2]
    radios.append(g)
radios = gpd.GeoDataFrame(pd.concat(radios, ignore_index=True), crs=AEA)
radios["geometry"] = radios.geometry.buffer(0)
# todos los partidos por separado (construir_partidos.py)
_pp = pd.read_pickle(os.path.join(HERE, "radios_partidos.pkl"))
PCOL = [c for c in _pp["radios"].columns if "|" in c]
radios = radios.merge(_pp["radios"], on=["dist", "pid"], how="left")
radios[PCOL] = radios[PCOL].fillna(0)
# otras elecciones 2011-2023 (construir_elecciones.py): un JSON por eleccion en elecciones_257/, que la pagina carga
# solo cuando se elige (no engordan el HTML)
_px = pd.read_pickle(os.path.join(HERE, "radios_elecciones.pkl"))
XCOL = [c for c in _px["radios"].columns if "|" in c]
radios = radios.merge(_px["radios"], on=["dist", "pid"], how="left")
radios[XCOL] = radios[XCOL].fillna(0)
XORD = _px["orden"]


def lado(n):
    """Lugar en el hemiciclo (izquierda 0 a derecha 5) por el nombre de la fuerza."""
    n = n.lower()
    if "izquierda" in n or "fit" in n or "caño" in n or "altamira" in n: return 0
    if any(w in n for w in ("victoria", "todos", "ciudadana", "patria", "scioli", "massa (uxp)", "grabois", "kirchner")): return 1
    if any(w in n for w in ("libertad", "milei", "libertarios")): return 5
    if any(w in n for w in ("udeso", "ucr", "progresista", "fap", "stolbizer", "cc-ari", "cívica")): return 3
    if any(w in n for w in ("cambiemos", "cambio", "propuesta republicana", "macri", "bullrich", "larreta", "carrió", "sanz")) or n == "pro": return 4
    return 2.5


XPART = {k: [{"k": f"{k}:{i}", "n": x["n"], "c": x["c"], "o": lado(x["n"])}
             for i, x in enumerate(_px["partidos"][k]["p"].values())] for k in XORD}
XCOLS = {k: [f"{k}|{c}" for c in _px["partidos"][k]["p"]] for k in XORD}
XDATA = {k: {"t": _px["partidos"][k]["t"], "partidos": XPART[k], "planes": {}} for k in XORD}
# familias que se cuentan juntas en la renovacion por mitades, y orden izquierda-derecha del hemiciclo
FAM = {"23|UxP": "PER", "25|B02": "PER", "23|LLA": "LLA", "25|B01": "LLA"}
RANGO = {"23|FIT": 0, "25|B04": 0, "25|B15": 0, "PER": 1, "23|HPNP": 3, "25|B03": 3, "23|JxC": 4, "25|B12": 3.5,
         "25|B16": 3.5, "25|B28": 4.5, "LLA": 5, "25|B08": 5.5, "25|B27": 5.5}
PARTIDOS = {}
for e in ("23", "25"):
    cs = [c for c in PCOL if c.startswith(e + "|")]
    cs.sort(key=lambda c: -radios[c].sum())
    PARTIDOS[e] = [{"k": FAM.get(c, c), "n": _pp["partidos"][e][c[3:]]["n"], "c": _pp["partidos"][e][c[3:]]["c"],
                    "o": RANGO.get(FAM.get(c, c), 2)} for c in cs]
ORDEN = {e: [c for c in sorted([c for c in PCOL if c.startswith(e + "|")], key=lambda c: -radios[c].sum())] for e in ("23", "25")}
VOT = [p + e for e, *_ in ELEC for p in "DR"]
amba = box(*gpd.GeoSeries([box(*AMBA_LL)], crs=4326).to_crs(AEA).total_bounds)
vis = gpd.GeoSeries([box(*VIS_LL)], crs=4326).to_crs(AEA).iloc[0]

# coberturas simplificadas: radios a una grilla de 1 m (asi casi todos los bordes compartidos coinciden), recortados
# al marco y simplificados juntos
def poligonal(gs):
    """Solo las partes poligonales (un recorte puede dejar lineas, puntos o nada)."""
    out = []
    for g_ in gs:
        if g_.geom_type not in ("Polygon", "MultiPolygon"):
            ps = [p for p in shapely.get_parts(g_) if p.geom_type == "Polygon"] if not g_.is_empty else []
            g_ = shapely.MultiPolygon(ps) if ps else shapely.Polygon()
        out.append(g_)
    return np.array(out, dtype=object)


geo = shapely.set_precision(radios.geometry.values, 1.0)
GN = shapely.coverage_simplify(poligonal(shapely.intersection(geo, vis)), TOL_N)
iA = np.flatnonzero(shapely.intersects(geo, amba))
GA = shapely.coverage_simplify(poligonal(shapely.intersection(geo[iA], amba)), TOL_A)


def unir(geoms, claves):
    """Union de las geometrias por clave, en el orden de las claves."""
    s_ = pd.Series(list(geoms))
    return s_.groupby(np.asarray(claves)).agg(lambda x: shapely.union_all(x.values))


prov = unir(GN, radios.dist)


def path(geom, tol, ox, oy, s):
    """SVG path (y hacia abajo) de un poligono simplificado, en enteros relativos (cortos)."""
    out = []
    for p in getattr(geom, "geoms", [geom]):
        if p.geom_type != "Polygon" or p.area < (tol * tol * 4): continue
        # sin los huecos diminutos que dejan los pocos bordes que no coinciden
        for ring in [p.exterior] + [i for i in p.interiors if abs(shapely.Polygon(i).area) > tol * tol * 4]:
            c = np.asarray(ring.coords)[:-1]
            c = np.rint(np.column_stack(((c[:, 0] - ox) * s, (oy - c[:, 1]) * s))).astype(int)
            c = c[np.r_[True, (np.diff(c, axis=0) != 0).any(axis=1)]]
            if len(c) < 3: continue
            d = np.diff(c, axis=0)
            out.append(f"M{c[0, 0]} {c[0, 1]}l" + " ".join(f"{a} {b}" for a, b in d) + "z")
    return "".join(out)


# marco nacional: 560 px de ancho
minx, miny, maxx, maxy = shapely.total_bounds(prov.values)
SN = 560 * KN / (maxx - minx)
ax0, ay0, ax1, ay1 = amba.bounds
SA = 620 * KA / (ax1 - ax0)
data = {"planes": [], "elec": [{"k": k, "t": t, "d": d, "r": r} for k, t, d, r in ELEC],
        "prov": [path(geom, TOL_N, minx, maxy, SN) for geom in prov.values],
        "provA": [path(g_, TOL_A, ax0, ay1, SA) for g_ in unir(GA, radios.dist.values[iA]).values],
        "deptoA": [path(g_, TOL_A, ax0, ay1, SA) for k_, g_ in unir(GA, radios.county.values[iA]).items()
                   if k_.startswith("06")],
        "ambaBox": [(ax0 - minx) * SN, (maxy - ay1) * SN, (ax1 - ax0) * SN, (ay1 - ay0) * SN],
        "W": 560 * KN, "H": (maxy - miny) * SN, "WA": 620 * KA, "HA": (ay1 - ay0) * SA,
        "nombres": {d: v[0] for d, v in CENSO.items()}, "partidos": PARTIDOS,
        "familias": {"PER": "Peronismo", "LLA": "La Libertad Avanza"}}

bancas = radios.groupby("dist").size()  # se reemplaza abajo
for clave, carpeta, titulo, dep in PLANES:
    hechas = glob.glob(os.path.join(HERE, carpeta, "[0-9][0-9].csv"))
    if len(hechas) < len(CENSO):
        print("falta", carpeta, len(hechas), "de", len(CENSO)); continue
    asig = pd.concat([pd.read_csv(f, dtype={"pid": str}).assign(dist=os.path.basename(f)[:2])
                      for f in glob.glob(os.path.join(HERE, carpeta, "[0-9][0-9].csv"))])
    r = radios.merge(asig, on=["pid", "dist"], how="left")
    assert r.distrito.notna().all(), carpeta
    r["key"] = r.dist + "-" + r.distrito.astype(int).astype(str)
    dis = r.groupby("key").agg({**{c: "sum" for c in VOT + PCOL}, "population": "sum", "dist": "first"})
    gN, gA = unir(GN, r.key), unir(GA, r.key.values[iA])
    dis["geometry"] = gN.reindex(dis.index)
    cen = shapely.centroid(dis.geometry.values)
    dis["cx"], dis["cy"] = shapely.get_x(cen), shapely.get_y(cen)
    # clases de renovacion
    dis["clase"] = dis["sorteo"] = ""
    nprov = dis.groupby("dist").size()
    impares = [d for d in sorted(nprov.index) if nprov[d] % 2]
    k = 130 - int((nprov // 2).sum())  # provincias impares que eligen la mitad grande en 2023
    for d in sorted(nprov.index):
        sub = dis[dis.dist == d].sort_values(["cy", "cx"], ascending=[False, True])
        n = len(sub)
        a = n // 2 + (1 if d in impares[:k] else 0)
        cl = ["A" if i % 2 == 0 else "B" for i in range(n)]
        if cl.count("A") > a: cl[-1] = "B"
        dis.loc[sub.index, "clase"] = cl
        # «Ley Bases» (proyecto 0025-PE-2023, art. 447 -> art. 162 del Codigo Electoral): la Camara sortea las
        # circunscripciones de la primera renovacion parcial. Misma cantidad de clase A por provincia, al azar
        # con semilla fija (reproducible)
        rng = np.random.default_rng(int(d) * 1000 + 2023)
        cb = np.array(["B"] * n); cb[rng.choice(n, a, replace=False)] = "A"
        dis.loc[sub.index, "sorteo"] = cb
    ds = []
    for key, row in dis.iterrows():
        enA = key in gA.index
        ds.append({"id": key, "p": row.dist, "pob": int(row.population), "c": row.clase, "cb": row.sorteo,
                   "v": [int(row[c]) for c in VOT],
                   # votos por partido, ralos: [indice en DATA.partidos[e], votos]
                   "vp": {e: [[i, int(row[c])] for i, c in enumerate(ORDEN[e]) if row[c] > 0] for e in ORDEN},
                   "n": path(row.geometry, TOL_N / 2, minx, maxy, SN),
                   "a": path(gA[key], TOL_A, ax0, ay1, SA) if enA else ""})
    data["planes"].append({"k": clave, "t": titulo, "dep": dep, "d": ds})
    dx = r.groupby("key")[XCOL].sum().reindex(dis.index)
    for k in XORD:
        m = dx[XCOLS[k]].values.astype(np.int64)
        XDATA[k]["planes"][f"{clave}|{dep}"] = [[[i, int(v)] for i, v in enumerate(fila) if v > 0] for fila in m]
    print(clave, len(ds), "distritos; clase A", (dis.clase == "A").sum())

data["extra"] = [{"k": k, "t": XDATA[k]["t"]} for k in XORD]
os.makedirs(os.path.join(HERE, XDIR), exist_ok=True)
for k in XORD:
    with open(os.path.join(HERE, XDIR, f"{k}.json"), "w", encoding="utf-8") as fh:
        json.dump(XDATA[k], fh, separators=(",", ":"), ensure_ascii=False)
print("elecciones_257:", sum(os.path.getsize(os.path.join(HERE, XDIR, f"{k}.json")) for k in XORD) // 1024, "KB")
html = open(os.path.join(HERE, "mapa_plantilla.html"), encoding="utf-8").read()
out = os.path.join(HERE, "mapa_257_antiperonista.html" if ANTI else "mapa_257.html")
if ANTI:
    html = html.replace('fetch("elecciones_257/"', 'fetch("elecciones_257_anti/"').replace(
        "<title>Argentina con 257 distritos uninominales: mapa interactivo</title>",
        "<title>257 distritos: gerrymanders antiperonistas (local)</title>")
open(out, "w", encoding="utf-8").write(html.replace("/*DATA*/null", json.dumps(data, separators=(",", ":"))))
print(out, os.path.getsize(out) // 1024, "KB")
