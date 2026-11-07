"""Exporta las parroquias electorales de Capital (1864-1898) a SHP y GeoPackage.

Usa la misma reconstrucción que el visor (parroquias1896.py) y deshace la proyección
lineal de geometria.py para volver a coordenadas geográficas (CRS de la base de
Rodríguez y De Grande).

Correr con el Python del venv de Mosaic (geopandas):
  "C:/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe" mapas/capital_canton/exportar_parroquias.py
Salida: geometria/parroquias_capital_1864_1898/
"""
import json, math, os, pickle, sys, zipfile
import geopandas as gpd
import numpy as np
from shapely.ops import transform, unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(AQUI))
B = os.path.join(R, "geometria", "Base deptos 1869-2022")
OUT = os.path.join(R, "geometria", "parroquias_capital_1864_1898")
sys.path.insert(0, AQUI)
import capital1954, parroquias1896

# Mismo encuadre que geometria.py (la proyección del calco depende de él).
b14 = gpd.read_file(os.path.join(B, "Departamentos_1914.shp"))
CRS = b14.crs
g20 = list(b14[b14.PROV_COD == "02"].geometry)
g51 = gpd.read_file(os.path.join(R, "mapas", "mapa1951", "shp", "circunscripciones_1951.shp"))
g51 = list(g51[g51.provincia.str.contains("Capital")].geometry)
g28 = [v[1] for v in pickle.load(open(os.path.join(R, "mapas", "mapa1983", "caba28.pkl"), "rb")).values()]
g54 = [u["geom"] for u in capital1954.geometria([])]
x0, y0, x1, y1 = unary_union(g20 + g28 + g51 + g54).bounds
k = math.cos(math.radians((y0 + y1) / 2))
esc = 760 / ((x1 - x0) * k)


def proyectar(x, y):
    return (np.asarray(x) - x0) * k * esc, (y1 - np.asarray(y)) * esc


def desproyectar(x, y):
    return np.asarray(x) / (k * esc) + x0, y1 - np.asarray(y) / esc


secc = {}
for anio in (1869, 1895):
    g = gpd.read_file(os.path.join(B, f"Departamentos_{anio}.shp"))
    g = g[(g.PROV_COD.astype(str) == "02") & g.DEPTO.str.startswith("SECCION")]
    secc[anio] = g
municipio1869 = unary_union(list(secc[1869].geometry))
secciones1895 = {r.DEPTO.split()[-1]: r.geometry for r in secc[1895].itertuples()}

parroquias, _, contorno = parroquias1896.reconstruir(secciones1895, proyectar)
etapas = parroquias1896.variantes(parroquias, contorno, municipio1869, secciones1895, proyectar)

VERSION = {
    "p1864": ("1864-1869", "Calco municipal adaptado al limite de 1869; Barracas al Norte agrupada y Balvanera anterior a San Cristobal reconstruida"),
    "p1872": ("1872-1886", "Calco municipal, limite occidental del SHP de 1869 y Riachuelo de la lamina"),
    "p1890": ("1890-1895", "Calco municipal con el area de San Bernardo reintegrada segun el cruce con las secciones de 1895"),
    "p1896": ("1896-03", "Calco de la lamina municipal cotejado con Canton y Jorrat, t. I, apendices 2 y 4"),
    "p1898": ("1898", "Lamina municipal para Carmen, Velez Sarsfield y San Carlos; decretos de 1896 para Las Heras y Balvanera Norte/Sur"),
}
RESERVA = "Reconstruccion aproximada, no delimitacion legal"


# Trazo «base»: el mismo que muestra el visor, calculado en su proyección.
BASE = parroquias1896.contornos_base(municipio1869, secc[1895].geometry, proyectar)


os.makedirs(OUT, exist_ok=True)
gpkg = os.path.join(OUT, "parroquias_capital_1864_1898.gpkg")
if os.path.exists(gpkg):
    os.remove(gpkg)
control = {}
tandas = []
for clave, (caras, limite) in etapas.items():
    tandas.append((clave, "lamina", {u: transform(desproyectar, g) for u, g in caras.items()}))
    ajuste = parroquias1896.ajustar_a_base(caras, BASE[clave])
    tandas.append((clave, "base", {u: transform(desproyectar, g) for u, g in ajuste.items()}))
for clave, trazo, geos in tandas:
    vig, metodo = VERSION[clave]
    filas = []
    for nombre, geom in sorted(geos.items()):
        diques = nombre == "DIQUES"
        filas.append({"parroquia": nombre.title() if not diques else "Diques y darsenas",
                      "tipo": "puerto" if diques else "parroquia",
                      "version": clave, "vigencia": vig, "trazo": trazo, "metodo": metodo[:254],
                      "reserva": RESERVA, "geometry": geom})
    gdf = gpd.GeoDataFrame(filas, crs=CRS)
    assert gdf.is_valid.all(), (clave, trazo)
    nombre = f"parroquias_{clave[1:]}" + ("_base" if trazo == "base" else "")
    clave = nombre
    gdf.to_file(os.path.join(OUT, nombre + ".shp"), encoding="utf-8")
    gdf.to_file(gpkg, layer=nombre, driver="GPKG")
    utm = gdf.to_crs(32721)
    control[clave] = {"vigencia": vig,
                      "parroquias": int((gdf.tipo == "parroquia").sum()),
                      "puerto": bool((gdf.tipo == "puerto").any()),
                      "km2": {r.parroquia: round(r.geometry.area / 1e6, 3) for r in utm.itertuples()},
                      "km2_total": round(utm.area.sum() / 1e6, 2),
                      "solapes_m2": round(utm.area.sum() - utm.union_all().area, 1)}

json.dump(control, open(os.path.join(OUT, "CONTROL.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with zipfile.ZipFile(os.path.join(OUT, "parroquias_capital_1864_1898_shp.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(OUT)):
        if f.startswith("parroquias_1") or f.startswith("parroquias_18"):
            if f.split(".")[-1] in ("shp", "shx", "dbf", "prj", "cpg"):
                z.write(os.path.join(OUT, f), f)
    for f in ("LEEME.md", "CONTROL.json"):
        if os.path.exists(os.path.join(OUT, f)):
            z.write(os.path.join(OUT, f), f)
for c, v in control.items():
    print(c, v["vigencia"], v["parroquias"], "parroquias", v["km2_total"], "km2", "solape", v["solapes_m2"])
