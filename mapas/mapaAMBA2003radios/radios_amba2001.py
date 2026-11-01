"""Extrae los radios censales 2001 del AMBA (CONICET, RADIOS_2001_V2025-1) a radios_amba2001.geojson (WGS84).
Necesita geopandas: correr con el Python del entorno de Mosaic, p. ej.
  "<venv de Mosaic>/python.exe" radios_amba2001.py
AMBA = Capital (PROV 02) + los 40 partidos del atlas AMBA 2025 (codigos INDEC de georef, depto_pba_georef.json; iguales en 2001)."""
import os, re, json, unicodedata
import geopandas as gpd
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
ZIP = os.path.join(ROOT, "geometria", "cartografia_argentina", "conicet", "radios", "RADIOS_2001_V2025-1.zip")


def n(s): return re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


AMBA = [n(x) for x in ("Almirante Brown,Avellaneda,Berazategui,Esteban Echeverría,Ezeiza,Florencio Varela,General San Martín,Hurlingham,Ituzaingó,"
                       "José C. Paz,La Matanza,Lanús,Lomas de Zamora,Malvinas Argentinas,Merlo,Moreno,Morón,Quilmes,San Fernando,San Isidro,San Miguel,Tigre,"
                       "Tres de Febrero,Vicente López,Berisso,Brandsen,Campana,Cañuelas,Ensenada,Escobar,Exaltación de la Cruz,General Las Heras,"
                       "General Rodríguez,La Plata,Luján,Marcos Paz,Pilar,Presidente Perón,San Vicente,Zárate").split(",")]
dep = {x["id"][2:]: x["nombre"] for x in json.load(open(os.path.join(HERE, "depto_pba_georef.json"), encoding="utf8"))["departamentos"] if n(x["nombre"]) in AMBA}
assert len(dep) == 40, sorted(dep.values())
g = gpd.read_file("zip://" + ZIP + "!Radios 2001 v2025-1.shp")
g = g[(g.PROV == "02") | ((g.PROV == "06") & g.DEPTO.isin(dep))].copy()
miss = set(dep) - set(g[g.PROV == "06"].DEPTO)
assert not miss, [dep[m] for m in miss]
g["partido"] = [("Ciudad de Buenos Aires" if p == "02" else dep[d]) for p, d in zip(g.PROV, g.DEPTO)]
g = g.to_crs(4326)
g[["COD_2001", "PROV", "DEPTO", "partido", "POB_TOT", "VIV_TOT", "geometry"]].to_file(os.path.join(HERE, "radios_amba2001.geojson"), driver="GeoJSON")
print(len(g), "radios;", int(g.POB_TOT.sum()), "habitantes;", g.partido.nunique(), "partidos;",
      "Capital", int(g[g.PROV == "02"].POB_TOT.sum()))
