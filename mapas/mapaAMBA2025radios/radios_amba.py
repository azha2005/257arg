"""Extrae los radios censales 2022 del AMBA (CONICET, RADIOS_2022_V2025-1) a radios_amba2022.geojson (WGS84).
Necesita geopandas: correr con el Python del entorno de Mosaic, p. ej.
  "<venv de Mosaic>/python.exe" radios_amba.py
AMBA = Capital (PROV 02) + los 40 partidos del atlas por circuito (codigos INDEC de georef, depto_pba_georef.json)."""
import os, re, json, unicodedata
import geopandas as gpd
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
ZIP = os.path.join(ROOT, "geometria", "cartografia_argentina", "conicet", "radios", "RADIOS_2022_V2025-1.zip")


def n(s): return re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


AMBA = [n(x) for x in ("Almirante Brown,Avellaneda,Berazategui,Esteban Echeverría,Ezeiza,Florencio Varela,General San Martín,Hurlingham,Ituzaingó,"
                       "José C. Paz,La Matanza,Lanús,Lomas de Zamora,Malvinas Argentinas,Merlo,Moreno,Morón,Quilmes,San Fernando,San Isidro,San Miguel,Tigre,"
                       "Tres de Febrero,Vicente López,Berisso,Brandsen,Campana,Cañuelas,Ensenada,Escobar,Exaltación de la Cruz,General Las Heras,"
                       "General Rodríguez,La Plata,Luján,Marcos Paz,Pilar,Presidente Perón,San Vicente,Zárate").split(",")]
dep = {x["id"][2:]: x["nombre"] for x in json.load(open(os.path.join(HERE, "depto_pba_georef.json"), encoding="utf8"))["departamentos"] if n(x["nombre"]) in AMBA}
assert len(dep) == 40, sorted(dep.values())
g = gpd.read_file("zip://" + ZIP + "!Radios 2022 v2025-1.shp")
g = g[(g.PROV == "02") | ((g.PROV == "06") & g.DEPTO.isin(dep))].copy()
g["partido"] = [("Ciudad de Buenos Aires" if p == "02" else dep[d]) for p, d in zip(g.PROV, g.DEPTO)]
g["comuna"] = [int(d) // 7 if p == "02" else None for p, d in zip(g.PROV, g.DEPTO)]   # Capital: DEPTO 007, 014... = comuna 1, 2...
g = g.to_crs(4326)
g[["COD_2022", "PROV", "DEPTO", "partido", "comuna", "POB_TOT_P", "VIV_TOT_P", "geometry"]].to_file(os.path.join(HERE, "radios_amba2022.geojson"), driver="GeoJSON")
print(len(g), "radios;", int(g.POB_TOT_P.sum()), "habitantes;", g.partido.nunique(), "partidos")
